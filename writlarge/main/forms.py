from datetime import date

from django import forms

from writlarge.main.models import ExtendedDate


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
        edt = self.get_extended_date()

        display_format = edt.__str__()
        if 'invalid' in display_format or 'None' in display_format:
            self._errors['__all__'] = self.error_class([
                'Please specify a valid date'])
            return

        self._set_errors(edt, cleaned_data)
        return cleaned_data

    def get_extended_date(self):
        return ExtendedDate.objects.from_dict(self.cleaned_data)

    def get_error_messages(self):
        msg = ''
        for key, val in self.errors.items():
            if key != '__all__':
                msg += key + ': '
            msg += val[0]
            msg += '<br />'
        return msg

    def get_start_date(self, edt):
        try:
            return edt.start()
        except ValueError:
            return None

    def get_end_date(self, edt):
        try:
            return edt.end()
        except ValueError:
            return None

    def _set_errors(self, edt, cleaned_data):
        start = self.get_start_date(edt)

        if cleaned_data['is_range']:
            end = self.get_end_date(edt)
            self._set_errors_is_range(start, end)
        elif start is None:
            self._errors['__all__'] = self.error_class([
                'Please specify a valid date'])
        elif start > date.today():
            self._errors['__all__'] = self.error_class([
                'The date must be today or earlier'])

    def _set_errors_is_range(self, start, end):
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
        edtf = self.get_extended_date()
        edtf.save()
        return edtf
