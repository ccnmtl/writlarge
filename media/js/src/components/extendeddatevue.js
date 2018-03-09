/* exported ExtendedDateVue */

var ExtendedDateVue = {
    props: [
        'id', 'name', 'initial-errors',
        'initial-millenium1', 'initial-century1', 'initial-decade1',
        'initial-year1', 'initial-month1', 'initial-day1',
        'initial-approximate1', 'initial-uncertain1'],
    template: '#edtf-template',
    data: function() {
        return {
            errors: 0,
            dateDisplay: '',
            millenium1: '',
            century1: '',
            decade1: '',
            year1: '',
            month1: '',
            day1: '',
            approximate1: false,
            uncertain1: false
        };
    },
    methods: {
        el: function() {
            return $('#' + this.id);
        },
        setFocus: function() {
            document.getElementById(this.id).scrollIntoView();
        },
        markRequired: function() {
            // If a field is not populated, and subsequent fields *are*
            // populated, mark the field as "required"
            // @todo - this is less reactive then it could be
            // consider how this could be re-expressed
            const $el = this.el();
            $el.find('.required').removeClass('required');

            function hasValue() {
                var value = $(this).val();
                return value && value.length > 0;
            }

            // grab rightmost edtf-entry field with a valid value
            // then verify the specified dependencies have values
            // mark class with "required" if no value is found
            const $row = $el.find('.row').first();

            let elts = $row.find('input[type="number"],select');
            elts = elts.filter(hasValue).get().reverse();

            let required = 0;
            let selector = $(elts).first().attr('data-required');
            $row.find(selector).not(hasValue).each(function() {
                $(this).addClass('required');
                required++;
            });
            return required;
        },
        limit: function(evt) {
            const charCode = (evt.which) ? evt.which : evt.keyCode;
            if (charCode >= 48 && charCode <= 57) {
                const $elt = $(evt.currentTarget);
                const len = parseInt($elt.attr('maxlength'), 10);
                const curLen = $elt.val().length + 1;
                if (curLen > len) {
                    // don't accept anymore characters
                    evt.preventDefault();
                    evt.stopImmediatePropagation();
                } else if (curLen === len && $elt.hasClass('jump')) {
                    $elt.nextAll('input').first().focus();
                }
            }
        },
        display: function(evt) {
            this.errors = this.markRequired();

            if (this.errors > 0) {
                return;
            }

            const params = {
                url: WritLarge.baseUrl + 'date/display/',
                data: this.toDict()
            };

            $.post(params, (response) => {
                if (response.success) {
                    this.dateDisplay = response.display;
                } else {
                    this.errors = 1;
                }
            });
        },
        toDict: function() {
            return {
                'millenium1': this.millenium1,
                'century1': this.century1,
                'decade1': this.decade1,
                'year1': this.year1,
                'month1': this.month1,
                'day1': this.day1,
                'approximate1': this.approximate1,
                'uncertain1': this.uncertain1,
                'is_range': false
            };
        },
    },
    mounted: function() {
        const $el = this.el();
        $el.find('[data-toggle="popover"]').popover({
            'html': true,
            'trigger': 'focus',
            'placement': 'bottom'
        });
        $el.find('[data-toggle="tooltip"]').tooltip();

        this.approximate1 = this.initialApproximate1;
        this.uncertain1 = this.initialUncertain1;
        this.millenium1 = this.initialMillenium1;
        this.century1 = this.initialCentury1;
        this.decade1 = this.initialDecade1;
        this.year1 = this.initialYear1;
        this.month1 = this.initialMonth1;
        this.day1 = this.initialDay1;
        this.errors = this.initialErrors;
    }
};
