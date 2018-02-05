requirejs(['./common'], function() {
    requirejs(['jquery', 'bootstrap', 'Vue'], function($, bootstrap, Vue) {
        new Vue({
            el: '#map-view'
        });
    });
});

