/* global GoogleMapVue */

requirejs(['./common'], function() {
    const a = ['jquery', 'bootstrap', 'Vue', 'mapVue'];
    requirejs(a, function($, bootstrap, Vue, mapVue) {
        new Vue({
            el: '#map-container',
            components: {
                'google-map': GoogleMapVue
            }
        });
    });
});

