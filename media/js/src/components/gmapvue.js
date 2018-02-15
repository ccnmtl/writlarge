/* global google: true */
/* exported GoogleMapVue */

var GoogleMapVue = {
    template: '#google-map-template',
    data: function() {
        return {
            mapName: 'the-map',
            sites: [],
            map: null,
            markers: [],
            bounds: null,
            newPin: null,
            address: ''
        };
    },
    methods: {
        dropPin: function(event) {
            if (this.newPin) {
                this.newPin.setMap(null);
            }

            this.newPin = new google.maps.Marker({
                position: event.latLng,
                map: this.map
            });

            this.reverseGeocode(this.newPin);
        },
        removeNewPin: function(event) {
            this.newPin.setMap(null);
            this.newPin = null;
        },
        savePin: function(event) {
        },
        editPin: function(event) {
        },
        geocode: function(event) {
            this.geocoder.geocode({
                address: this.address,
            }, (responses) => {
                if (responses && responses.length > 0) {
                    if (this.newPin) {
                        this.newPin.setMap(null);
                    }

                    this.newPin = new google.maps.Marker({
                        position: responses[0].geometry.location,
                        map: this.map
                    });
                }
            });

        },
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
    created: function() {
        const url = WritLarge.baseUrl + 'api/site/';
        jQuery.getJSON(url, (data) => {
            this.sites = data;
        });
    },
    mounted: function() {
        this.bounds = new google.maps.LatLngBounds();
        const elt = document.getElementById(this.mapName);

        this.geocoder = new google.maps.Geocoder();

        this.map = new google.maps.Map(elt, {
            mapTypeControl: false
        });
        this.map.addListener('click', (ev) => {
            this.dropPin(ev);
        });
    },
    updated: function() {
        this.sites.forEach((site) => {
            const position = new google.maps.LatLng(
                site.latitude, site.longitude);
            const marker = new google.maps.Marker({
                position: position,
                map: this.map
            });
            this.markers.push(marker);
            if (!this.newPin) {
                // don't change the viewport
                this.map.fitBounds(this.bounds.extend(position));
            }
        });
    }
};
