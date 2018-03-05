/* exported ExtendedDateVue */

var ExtendedDateVue = {
    props: [
        'id', 'name', 'initial-errors',
        'millenium1', 'century1', 'decade1', 'year1',
        'month1', 'day1', 'approximate1', 'uncertain1'],
    template: '#edtf-template',
    data: function() {
        return {
            errors: 0,
            dateDisplay: ''
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
            const $el = this.el();
            return {
                'millenium1': $el
                    .find('input[name="' + this.name + '-millenium1"]')
                    .val(),
                'century1': $el
                    .find('input[name="' + this.name + '-century1"]').val(),
                'decade1': $el
                    .find('input[name="' + this.name + '-decade1"]').val(),
                'year1': $el
                    .find('input[name="' + this.name + '-year1"]').val(),
                'month1': $el
                    .find('select[name="' + this.name + '-month1"]').val(),
                'day1': $el
                    .find('input[name="' + this.name + '-day1"]').val(),
                'approximate1': $el
                    .find('input[name="' + this.name + '-approximate1"]')
                    .prop('checked'),
                'uncertain1': $el
                    .find('input[name="' + this.name + '-uncertain1"]')
                    .prop('checked'),
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

        if (this.approximate1 === 'True') {
            $el.find('input.approximate').prop('checked', true);
        }
        if (this.uncertain1 === 'True') {
            $el.find('input.uncertain').prop('checked', true);
        }
        if (this.millenium1) {
            $el.find('.millenium').val(this.millenium1);
        }
        if (this.century1) {
            $el.find('.century').val(this.century1);
        }
        if (this.decade1) {
            $el.find('.decade').val(this.decade1);
        }
        if (this.year1) {
            $el.find('.year').val(this.year1);
        }
        if (this.month1) {
            const selector = '.month option[value=' +
                this.month1.replace(/^[0]+/g, '') + ']';
            $el.find(selector).attr('selected','selected');
        }
        if (this.day1) {
            $el.find('.day').val(this.day1);
        }

        if (this.initialErrors) {
            this.errors = 1;
        }
    }
};
