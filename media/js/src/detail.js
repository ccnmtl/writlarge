/* global GoogleMiniMapVue */

requirejs(['./common'], function() {
    const a = ['jquery', 'utils', 'bootstrap', 'Vue', 'miniMapVue'];
    requirejs(a, function($, utils, bootstrap, Vue, miniMapVue) {
        new Vue({
            el: '#detail-container',
            components: {
                'google-mini-map': GoogleMiniMapVue
            }
        });
    });
});

