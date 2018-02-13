var vuePath = 'lib/vue/vue.min';
if (WritLarge.debug == 'true') {
    vuePath = 'lib/vue/vue';
}

var mapsPath = 'https://maps.google.com/maps/api/js?key=' +
    WritLarge.mapKey + '&libraries=places';

requirejs.config({
    baseUrl: '../../media/js/',
    paths: {
        'jquery': 'lib/jquery-3.2.1.min',
        'domReady': 'lib/require/domReady',
        'bootstrap': 'lib/bootstrap/js/bootstrap.bundle.min',
        'googleMaps': mapsPath,
        'Vue': vuePath,
        'mapVue': 'src/components/gmapvue'
    },
    shim: {
        'bootstrap': {
            'deps': ['jquery']
        }
    },
    urlArgs: 'bust=' + (new Date()).getTime()
});
