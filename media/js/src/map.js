/* global GoogleMapVue:true, csrfSafeMethod:true */

requirejs(['./common'], function() {
    const a = ['jquery', 'utils', 'bootstrap', 'Vue', 'mapVue'];
    requirejs(a, function($, utils, bootstrap, Vue, mapVue) {

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
            el: '#map-container',
            components: {
                'google-map': GoogleMapVue
            }
        });
    });
});

