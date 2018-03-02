/* exported ExtendedDateVue */

var ExtendedDateVue = {
    props: ['id'],
    template: '#edtf-template',
    data: function() {
        return {
            dateDisplay: '',
            errors: 0,
        };
    },
    methods: {
        el: function() {
            return $('#' + this.id);
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
            var selector = $(elts).first().data('required');
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
        }
    },
    mounted: function() {
        const $el = this.el();
        $el.find('[data-toggle="popover"]').popover({
            'html': true,
            'trigger': 'focus',
            'placement': 'bottom'
        });
        $el.find('[data-toggle="tooltip"]').tooltip();
    }
};
