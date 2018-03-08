from datetime import date
import re

from edtf import parse_edtf
from edtf.parser.parser_classes import (
    EARLIEST, PRECISION_YEAR, PRECISION_MONTH, PRECISION_DAY)
from edtf.parser.edtf_exceptions import EDTFParseException


def filter_fields(request_data, prefix):
    data = dict()
    for k in request_data.keys():
        if k.startswith(prefix):
            data[k[len(prefix):]] = request_data[k]
    return data


class ExtendedDateWrapper(object):
    month_names = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April',
        5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'September',
        10: 'October', 11: 'November', 12: 'December'}

    modifiers = [
        'unknown',  # empty date
        'open'  # range modifier, no beginning date or no end date specified
    ]

    @classmethod
    def _as_edtf_object(cls, edtf_format):
        try:
            return parse_edtf(edtf_format)
        except EDTFParseException:
            return None

    @classmethod
    def create(cls, edtf_format):
        edtf_object = cls._as_edtf_object(edtf_format)

        if hasattr(edtf_object, 'upper'):
            upper = ExtendedDateWrapper(edtf_object.upper)
        else:
            upper = None

        if hasattr(edtf_object, 'lower'):
            lower = ExtendedDateWrapper(edtf_object.lower)
        elif edtf_object is None and edtf_format in cls.modifiers:
            lower = ExtendedDateWrapper(edtf_format)
        else:
            lower = ExtendedDateWrapper(edtf_object)

        return (lower, upper)

    def __init__(self, edtf_object):

        if hasattr(edtf_object, 'date'):
            self.edtf_date = edtf_object.date
        else:
            self.edtf_date = edtf_object

        if hasattr(edtf_object, 'ua') and edtf_object.ua:
            self.is_uncertain = edtf_object.ua.is_uncertain
            self.is_approximate = edtf_object.ua.is_approximate
        else:
            self.is_uncertain = False
            self.is_approximate = False

    def _validate_python_date(self, dt):
        # the python-edtf library returns "date.max" on a ValueError
        # and, if approximate or uncertain are set, the day/month are adjusted
        # just compare the year 9999 to the returned year
        return None if dt.year == date.max.year else dt

    def start_date(self):
        try:
            dt = self.edtf_date._strict_date(EARLIEST)
        except AttributeError:
            dt = self.edtf_date.lower_strict()
        except AttributeError:
            return None

        return self._validate_python_date(dt)

    def end_date(self):
        dt = self.edtf_date.upper_strict()
        return self._validate_python_date(dt)

    def get_year(self):
        return self.edtf_date.get_year()

    def get_month(self):
        return self.edtf_date.get_month()

    def get_day(self):
        return self.edtf_date.day

    def get_precision(self):
        return self.edtf_date.precision

    def get_precise_year(self):
        return self.edtf_date._precise_year(EARLIEST)

    def is_empty(self):
        return self.edtf_date == 'unknown'

    def is_invalid(self):
        return self.edtf_date is None

    def ordinal(self, n):
        # cribbed from http://codegolf.stackexchange.com/
        # questions/4707/outputting-ordinal-numbers-1st-2nd-3rd#answer-4712
        return "%d%s" % (
            n, "tsnrhtdd"[(n / 10 % 10 != 1) * (n % 10 < 4) * n % 10::4])

    def fmt_modifier(self):
        if self.edtf_date == 'open':
            return 'present'
        if self.edtf_date == 'unknown':
            return '?'

    def fmt_century(self, century):
        return '{}s'.format(century)

    def fmt_millenium(self, millenium):
        millenium = int(millenium) + 1
        return '{} millenium'.format(self.ordinal(millenium))

    def fmt_month(self):
        month = self.get_month()
        try:
            return self.month_names[int(month)]
        except (KeyError, ValueError):
            return 'unknown month'

    def fmt_precision(self):
        precision = self.get_precision()

        if precision not in (PRECISION_YEAR, PRECISION_MONTH, PRECISION_DAY):
            return 'invalid'

        if precision == PRECISION_DAY:
            return '{} {}, {}'.format(
                self.fmt_month(), self.get_day(), self.get_year())

        if precision == PRECISION_MONTH:
            return '{} {}'.format(
                self.fmt_month(), self.get_year())

        year = self.get_year()
        m = re.match('([1-2])uuu', year)
        if m:
            return self.fmt_millenium(m.group(1))

        m = re.match('([1-2][0-9])uu', year)
        if m:
            return self.fmt_century(self.get_precise_year())

        m = re.match('([1-2][0-9][0-9])u', year)
        if m:
            return '{}s'.format(self.get_precise_year())

        return '{}'.format(self.get_precise_year())

    def format(self):
        if self.edtf_date is None:
            return 'invalid'

        if isinstance(self.edtf_date, str):
            return self.fmt_modifier()

        result = self.fmt_precision()

        if self.is_uncertain:
            result += '?'

        if self.is_approximate:
            result = 'c. ' + result

        return result

    def to_dict(self, ordinal):
        if not self.edtf_date or self.edtf_date in self.modifiers:
            return {}

        year = self.get_year()
        return {
            'approximate{}'.format(ordinal): self.is_approximate,
            'uncertain{}'.format(ordinal): self.is_uncertain,
            'millenium{}'.format(ordinal): year[0],
            'century{}'.format(ordinal): None if year[1] == 'u' else year[1],
            'decade{}'.format(ordinal): None if year[2] == 'u' else year[2],
            'year{}'.format(ordinal): None if year[3] == 'u' else year[3],
            'month{}'.format(ordinal): self.get_month(),
            'day{}'.format(ordinal): self.get_day()
        }
