/* global google: true, enlargeBounds: true */
/* exported GoogleMiniMapVue */

var GoogleMiniMapVue = {
    props: ['siteid'],
    template: '#google-mini-map-template',
    data: function() {
        return {
            mapName: 'the-map',
            site: null,
            address: null
        };
    },
    methods: {
        reverseGeocode: function(marker) {
            this.geocoder.geocode({
                latLng: marker.getPosition(),
            }, (responses) => {
                if (responses && responses.length > 0) {
                    this.address = responses[0].formatted_address;
                } else {
                    this.address = '';
                }
            });
        }
    },
    mounted: function() {
        this.geocoder = new google.maps.Geocoder();

        const elt = document.getElementById(this.mapName);
        this.map = new google.maps.Map(elt, {
            mapTypeControl: false,
            clickableIcons: false
        });

        const url = WritLarge.baseUrl + 'api/site/' + this.siteid + '/';
        jQuery.getJSON(url, (data) => {
            this.site = data;

            const position = new google.maps.LatLng(
                this.site.latitude, this.site.longitude);
            const marker = new google.maps.Marker({
                position: position,
                map: this.map
            });
            this.site.marker = marker;
            this.reverseGeocode(marker);
        });
    },
    updated: function() {
        this.bounds = new google.maps.LatLngBounds();

        // zoom in on the pin, but not too far
        this.bounds = new google.maps.LatLngBounds();
        this.bounds.extend(this.site.marker.position);
        this.bounds = enlargeBounds(this.bounds);
        this.map.fitBounds(this.bounds);
    }
};
