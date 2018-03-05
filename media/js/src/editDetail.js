/* global ExtendedDateVue, csrfSafeMethod:true */

requirejs(['./common'], function() {
    const a = ['jquery', 'utils', 'bootstrap', 'Vue', 'edtfVue'];
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
                'edtf': ExtendedDateVue
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
                }
            }
        });
    });
});

