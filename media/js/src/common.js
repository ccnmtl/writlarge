let vuePath = 'lib/vue/vue.min';
let urlArgs = 'bust=' + (new Date()).getTime();
if (WritLarge.debug == 'true') {
    vuePath = 'lib/vue/vue';
    urlArgs = '';
}

var mapsPath = 'https://maps.google.com/maps/api/js?key=' +
    WritLarge.mapKey + '&libraries=places';

requirejs.config({
    baseUrl: WritLarge.staticUrl + 'js/',
    paths: {
        'bootstrap': 'lib/bootstrap/js/bootstrap.bundle.min',
        'domReady': 'lib/require/domReady',
        'jquery': 'lib/jquery-3.3.1.min',
        'edtfVue': 'src/components/extendeddatevue',
        'googleMaps': mapsPath,
        'Vue': vuePath,
        'mapVue': 'src/components/gmapvue',
        'miniMapVue': 'src/components/gmapminivue',
        'familyNetworkVue': 'src/components/familynetworkvue',
        'utils': 'src/utils'
    },
    shim: {
        'bootstrap': {
            'deps': ['jquery']
        }
    },
    urlArgs: urlArgs
});
