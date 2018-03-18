from datetime import date

from django import forms
from django.forms.widgets import (
    TextInput, CheckboxSelectMultiple, HiddenInput)

from writlarge.main.models import (
    ExtendedDate, LearningSite, DigitalObject, ArchivalCollection, Place)
from writlarge.main.utils import filter_fields


class ExtendedDateForm(forms.Form):
    is_range = forms.BooleanField(initial=False, required=False)

    millenium1 = forms.IntegerField(min_value=1, max_value=2, required=False)
    century1 = forms.IntegerField(min_value=0, max_value=9, required=False)
    decade1 = forms.IntegerField(min_value=0, max_value=9, required=False)
    year1 = forms.IntegerField(min_value=0, max_value=9, required=False)
    month1 = forms.IntegerField(min_value=1, max_value=12, required=False)
    day1 = forms.IntegerField(min_value=1, max_value=31, required=False)
    approximate1 = forms.BooleanField(initial=False, required=False)
    uncertain1 = forms.BooleanField(initial=False, required=False)

    millenium2 = forms.IntegerField(min_value=1, max_value=2, required=False)
    century2 = forms.IntegerField(min_value=0, max_value=9, required=False)
    decade2 = forms.IntegerField(min_value=0, max_value=9, required=False)
    year2 = forms.IntegerField(min_value=0, max_value=9, required=False)
    month2 = forms.IntegerField(min_value=1, max_value=12, required=False)
    day2 = forms.IntegerField(min_value=1, max_value=31, required=False)
    approximate2 = forms.BooleanField(initial=False, required=False)
    uncertain2 = forms.BooleanField(initial=False, required=False)

    def clean(self):
        cleaned_data = super(ExtendedDateForm, self).clean()
        self.is_empty = False

        self.instance = self.get_extended_date()
        (lower, upper) = self.instance.wrap()

        if lower.is_invalid():
            self._errors['__all__'] = self.error_class([
                'Please specify a valid date'])
        elif lower.is_empty():
            self.is_empty = True
        elif cleaned_data['is_range']:
            self._set_range_errors(lower, upper)
        else:
            self._set_errors(lower)

        return cleaned_data

    def get_extended_date(self):
        try:
            return ExtendedDate.objects.from_dict(self.cleaned_data)
        except (TypeError, AttributeError):
            return None

    def get_error_messages(self):
        msg = ''
        for key, val in self.errors.items():
            if key != '__all__':
                msg += key + ': '
            msg += val[0]
            msg += '<br />'
        return msg

    def _set_errors(self, edt):
        start = edt.start_date()

        if start is None:
            self._errors['__all__'] = self.error_class([
                'Please specify a valid date'])
        elif start > date.today():
            self._errors['__all__'] = self.error_class([
                'The date must be today or earlier'])

    def _set_range_errors(self, lower, upper):
        start = lower.start_date()
        end = upper and upper.end_date()

        if start is None:
            self._errors['__all__'] = self.error_class([
                'Please specify a valid start date'])
        elif end is None:
            self._errors['__all__'] = self.error_class([
                'Please specify a valid end date'])
        elif start > date.today() or end > date.today():
            self._errors['__all__'] = self.error_class([
                'All dates must be today or earlier'])
        elif start > end:
            self._errors['__all__'] = self.error_class([
                'The start date must be earlier than the end date.'])

    def save(self):
        self.instance.save()
        return self.instance

    def create_or_update(self, parent, field_name):
        if self.errors and len(self.errors) > 0:
            return

        edt = getattr(parent, field_name)
        if edt and self.is_empty:
            # remove the date
            setattr(parent, field_name, None)
            parent.save()
            edt.delete()
        elif edt:
            # update existing date
            edt.edtf_format = self.instance.edtf_format
            edt.save()
        else:
            # add new date
            self.instance.save()
            setattr(parent, field_name, self.instance)
            parent.save()


class LearningSiteForm(forms.ModelForm):

    class Meta:
        model = LearningSite
        fields = ['title', 'description',
                  'category', 'instructional_level', 'target_audience',
                  'established', 'defunct', 'founder',
                  'tags', 'notes']
        widgets = {
            'title': TextInput,
            'category': CheckboxSelectMultiple,
            'instructional_level': CheckboxSelectMultiple,
            'target_audience': CheckboxSelectMultiple,
            'established': HiddenInput,
            'defunct': HiddenInput,
            'founder': TextInput
        }

    def clean(self):
        cleaned_data = forms.ModelForm.clean(self)

        self.form_established = ExtendedDateForm(
            filter_fields(self.data, 'established-'))
        self.form_defunct = ExtendedDateForm(
            filter_fields(self.data, 'defunct-'))

        if not self.form_established.is_valid():
            self._errors['established'] = \
                self.form_established.get_error_messages()
        if not self.form_defunct.is_valid():
            self._errors['defunct'] = \
                self.form_defunct.get_error_messages()

        return cleaned_data

    def save(self, commit=True):
        instance = forms.ModelForm.save(self, commit=commit)
        self.form_established.create_or_update(instance, 'established')
        self.form_defunct.create_or_update(instance, 'defunct')
        return instance


class ArchivalCollectionForm(forms.ModelForm):
    class Meta:
        model = ArchivalCollection

        fields = ['repository', 'title', 'description',
                  'finding_aid_url', 'linear_feet',
                  'inclusive_start', 'inclusive_end']
        widgets = {
            'title': TextInput,
            'inclusive_start': HiddenInput,
            'inclusive_end': HiddenInput
        }

    def clean(self):
        cleaned_data = forms.ModelForm.clean(self)

        self.form_start = ExtendedDateForm(
            filter_fields(self.data, 'inclusive-start-'))
        self.form_end = ExtendedDateForm(
            filter_fields(self.data, 'inclusive-end-'))

        if not self.form_start.is_valid():
            self._errors['inclusive-start'] = \
                self.form_start.get_error_messages()
        if not self.form_end.is_valid():
            self._errors['inclusive-end'] = \
                self.form_end.get_error_messages()

        return cleaned_data

    def save(self, commit=True):
        instance = forms.ModelForm.save(self, commit=commit)
        self.form_start.create_or_update(instance, 'inclusive_start')
        self.form_end.create_or_update(instance, 'inclusive_end')
        return instance


class DigitalObjectForm(forms.ModelForm):

    class Meta:
        model = DigitalObject

        fields = [
            'file', 'source_url', 'description', 'date_taken', 'source'
        ]
        widgets = {
            'description': TextInput,
            'date_taken': HiddenInput,
            'source': TextInput
        }

    def clean(self):
        cleaned_data = forms.ModelForm.clean(self)

        if not cleaned_data['file'] and not cleaned_data['source_url']:
            self.add_error('source_url', '')
            self.add_error('file', '')
            self.add_error(
                None, 'Please upload a file or specify a source url')

        self.form_date_taken = ExtendedDateForm(
            filter_fields(self.data, 'date-taken-'))

        if not self.form_date_taken.is_valid():
            self._errors['date_taken'] = \
                self.form_date_taken.get_error_messages()

        return cleaned_data

    def save(self, commit=True):
        instance = forms.ModelForm.save(self, commit=commit)
        self.form_date_taken.create_or_update(instance, 'date_taken')
        return instance


class PlaceForm(forms.ModelForm):

    class Meta:
        model = Place
        fields = ['title', 'latlng', 'start_date', 'end_date']
        widgets = {
            'title': HiddenInput,
            'latlng': HiddenInput,
            'start_date': HiddenInput,
            'end_date': HiddenInput
        }

    def clean(self):
        cleaned_data = forms.ModelForm.clean(self)

        self.form_start = ExtendedDateForm(
            filter_fields(self.data, 'start_date-'))
        self.form_end = ExtendedDateForm(
            filter_fields(self.data, 'end_date-'))

        if not self.form_start.is_valid():
            self._errors['start_date'] = \
                self.form_start.get_error_messages()
        if not self.form_end.is_valid():
            self._errors['end_date'] = \
                self.form_end.get_error_messages()

        return cleaned_data

    def save(self, commit=True):
        instance = forms.ModelForm.save(self, commit=commit)
        self.form_start.create_or_update(instance, 'start_date')
        self.form_end.create_or_update(instance, 'end_date')
        return instance
