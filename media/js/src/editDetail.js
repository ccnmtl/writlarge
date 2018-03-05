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
            }
        });
    });
});

