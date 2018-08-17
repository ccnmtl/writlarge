/* global ExtendedDateVue:true, csrfSafeMethod:true, GoogleMapVue:true */

requirejs(['./common'], function() {
    const a = ['jquery', 'utils', 'bootstrap', 'Vue',
        'edtfVue', 'mapVue'];

    requirejs(a, function($, utils, bootstrap, Vue, edtfVue) {

        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    const token =
                        $('meta[name="csrf-token"]').attr('content');
                    xhr.setRequestHeader('X-CSRFToken', token);
                }
            }
        });

        new Vue({
            el: '#edit-detail-container',
            components: {
                'edtf': ExtendedDateVue,
                'google-map': GoogleMapVue,
            },
            methods: {
                onSubmit: function(event) {
                    for (let i=0; i < this.$children.length; i++) {
                        if (this.$children[i].errors > 0) {
                            this.$children[i].setFocus();
                            event.preventDefault();
                            event.stopPropagation();
                            break;
                        }
                    }
                },
                toggleNextGroup: function(evt) {
                    const $elt = $(event.currentTarget);
                    const $grp = $elt.parents('.form-group')
                        .first().nextAll('.form-group').first();
                    if ($elt.is(':checked')) {
                        $grp.show();
                    } else {
                        $grp.hide();
                    }
                }
            }
        });
    });
});

