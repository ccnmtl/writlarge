/* global GoogleMapVue:true, csrfSafeMethod:true */

requirejs(['./common'], function() {
    const a = ['jquery', 'utils', 'bootstrap', 'noUiSlider', 'Vue', 'mapVue'];
    requirejs(a, function($, utils, bootstrap, noUiSlider, Vue, mapVue) {

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
            data: {
                noUiSlider: noUiSlider
            },
            components: {
                'google-map': GoogleMapVue
            }
        });
    });
});

