import re

from edtf.parser.parser_classes import (
    EARLIEST, PRECISION_YEAR, PRECISION_MONTH, PRECISION_DAY, Interval,
    UncertainOrApproximate)


month_names = {
    1: 'January', 2: 'February', 3: 'March', 4: 'April',
    5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'September',
    10: 'October', 11: 'November', 12: 'December'}


def append_uncertain(dt, uncertain):
    if uncertain:
        dt = '{}?'.format(dt)
    return dt


def append_approximate(dt, approximate):
    if approximate:
        dt = '{}~'.format(dt)
    return dt


def ordinal(n):
    # cribbed from http://codegolf.stackexchange.com/
    # questions/4707/outputting-ordinal-numbers-1st-2nd-3rd#answer-4712
    return "%d%s" % (
        n, "tsnrhtdd"[(n / 10 % 10 != 1) * (n % 10 < 4) * n % 10::4])


def fmt_modifier(edtf_obj):
    if edtf_obj == 'open':
        return 'present'
    if edtf_obj == 'unknown':
        return '?'


def fmt_century(year, is_interval):
    if is_interval:
        return '{}s'.format(year)

    century = int(str(year)[:2]) + 1

    return '{} century'.format(ordinal(century))


def fmt_millenium(millenium):
    millenium = int(millenium) + 1
    return '{} millenium'.format(ordinal(millenium))


def fmt_month(month):
    try:
        return month_names[int(month)]
    except (KeyError, ValueError):
        return 'unknown month'


def fmt_precision(date_obj, is_interval):
    if isinstance(date_obj, str):
        return fmt_modifier(date_obj)

    precision = date_obj.precision

    if precision == PRECISION_DAY:
        return '{} {}, {}'.format(
            fmt_month(date_obj.get_month()),
            date_obj.day, date_obj.get_year())

    if precision == PRECISION_MONTH:
        return '{} {}'.format(
            fmt_month(date_obj.get_month()), date_obj.get_year())

    if precision != PRECISION_YEAR:
        return 'invalid'

    year = date_obj.year
    m = re.match('([1-2])uuu', year)
    if m:
        return fmt_millenium(m.group(1))

    m = re.match('([1-2][0-9])uu', year)
    if m:
        return fmt_century(date_obj._precise_year(EARLIEST), is_interval)

    m = re.match('([1-2][0-9][0-9])u', year)
    if m:
        return '{}s'.format(date_obj._precise_year(EARLIEST))

    return '{}'.format(date_obj._precise_year(EARLIEST))


def fmt_edtf_date(edtf_obj, is_interval):
    #  @todo - the model now carries this function, factor it out.
    if isinstance(edtf_obj, UncertainOrApproximate):
        date_obj = edtf_obj.date
        is_uncertain = edtf_obj.ua and edtf_obj.ua.is_uncertain
        is_approximate = edtf_obj.ua and edtf_obj.ua.is_approximate
    else:
        date_obj = edtf_obj
        is_uncertain = False
        is_approximate = False

    result = fmt_precision(date_obj, is_interval)

    if is_uncertain:
        result += '?'

    if is_approximate:
        result = 'c. ' + result

    return result


def edtf_to_text(edtf_object):
    if edtf_object is None:
        return 'invalid'

    if isinstance(edtf_object, Interval):
        return "%s - %s" % (fmt_edtf_date(edtf_object.lower, True),
                            fmt_edtf_date(edtf_object.upper, True))
    else:
        return fmt_edtf_date(edtf_object, False)
