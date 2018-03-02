/* global ExtendedDateVue */

requirejs(['./common'], function() {
    const a = ['jquery', 'utils', 'bootstrap', 'Vue', 'edtfVue'];
    requirejs(a, function($, utils, bootstrap, Vue, edtfVue) {
        new Vue({
            el: '#edit-detail-container',
            components: {
                'edtf': ExtendedDateVue
            }
        });
    });
});

