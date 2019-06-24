requirejs(['./common'], function(common) {
    requirejs(['jquery', 'domReady', 'bootstrap'],
        function($, domReady, bootstrap) {
            domReady(function() {
                // common functionality for vanilla pages goes here
            });
        }
    );
});
