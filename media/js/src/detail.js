/* global GoogleMiniMapVue, FamilyNetworkVue */

requirejs(['./common'], function() {
    const a = ['jquery', 'utils', 'bootstrap', 'Vue',
        'miniMapVue', 'familyNetworkVue'];
    requirejs(a, function($, utils, bootstrap, Vue,
        miniMapVue, familyNetworkVue) {
        new Vue({
            el: '#detail-container',
            components: {
                'google-mini-map': GoogleMiniMapVue,
                'family-network': FamilyNetworkVue
            }
        });
    });
});

