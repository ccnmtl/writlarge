var vue_path = 'lib/vue/vue.min';
if (WritLarge.debug == 'true') {
    vue_path = 'lib/vue/vue';
}

requirejs.config({
    baseUrl: '../../media/js/',
    paths: {
        'jquery': 'lib/jquery-3.2.1.min',
        'domReady': 'lib/require/domReady',
        'bootstrap': 'lib/bootstrap/js/bootstrap.bundle.min',
        'Vue': vue_path
    },
    shim: {
        'bootstrap': {
            'deps': ['jquery']
        }
    },
    urlArgs: 'bust=' + (new Date()).getTime()
});
