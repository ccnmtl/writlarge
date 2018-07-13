/* global google: true, enlargeBounds: true, lightGrayStyle: true */
/* exported GoogleMapVue */

var GoogleMapVue = {
    props: ['readonly', 'showplaces', 'latitude',
        'longitude', 'title', 'icon', 'autodrop'],
    template: '#google-map-template',
    data: function() {
        return {
            mapName: 'the-map',
            places: [],
            map: null,
            bounds: null,
            address: '',
            newPin: null,
            newTitle: '',
            newType: '',
            selectedPlace: null,
            year: 'Present'
        };
    },
    computed: {
        latlng: {
            get: function() {
                if (this.newPin) {
                    return 'SRID=4326;POINT(' +
                        this.newPin.position.lng() + ' ' +
                        this.newPin.position.lat() + ')';
                }
            },
        }
    },
    methods: {
        isReadOnly: function() {
            return this.readonly === 'true';
        },
        clearNewPin: function(event) {
            if (this.newPin) {
                this.newPin.setMap(null);
                this.newPin = null;
                this.address = '';
                this.newTitle = '';
            }
        },
        dropPin: function(event) {
            this.clearNewPin();
            this.selectedPlace = null;

            this.newPin = new google.maps.Marker({
                position: event.latLng,
                map: this.map,
                icon: WritLarge.staticUrl + 'png/pin-' + this.icon + '.png'
            });

            this.reverseGeocode(this.newPin);
        },
        savePin: function(event) {
            const data = {
                'title': this.newTitle,
                'latlng': this.newPin.position.toJSON(), // to be deprecated
                'place': [{
                    'title': this.address,
                    'latlng': this.newPin.position.toJSON()
                }]
            };

            const params = {
                url: WritLarge.baseUrl + 'api/site/',
                dataType: 'json',
                contentType: 'application/json',
                data: JSON.stringify(data)
            };

            $.post(params, (response) => {
                response.marker = this.newPin;
                this.places.push(response);
                this.selectedPlace = response;
                this.newPin = null;
                this.newTitle = '';
            });
        },
        deselectPlace: function(event) {
            this.selectedPlace = null;
        },
        getAddress: function(event) {
            return this.address;
        },
        getPlace: function(event) {
            return this.selectedPlace || this.newPin;
        },
        geocode: function(event) {
            this.clearNewPin();
            this.selectedPlace = null;

            this.geocoder.geocode({
                address: this.address,
            }, (responses) => {
                if (responses && responses.length > 0) {
                    this.address = responses[0].formatted_address;
                    const position = responses[0].geometry.location;

                    // zoom in on the location, but not too far
                    this.bounds = new google.maps.LatLngBounds();
                    this.bounds.extend(position);
                    this.bounds = enlargeBounds(this.bounds);
                    this.map.fitBounds(this.bounds);

                    if (this.autodrop === 'true') {
                        const marker = new google.maps.Marker({
                            position: position,
                            map: this.map,
                            icon: WritLarge.staticUrl +
                                'png/pin-' + this.icon + '.png'
                        });
                        this.newPin = marker;
                    }
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
        },
        changeOverlay: function(event) {
            const id = jQuery(event.currentTarget).data('id');
            if (this.map.overlayMapTypes.getLength() > 0) {
                this.map.overlayMapTypes.pop();
            }
            if (id === 'Present') {
                return;
            }

            var overlay = new google.maps.ImageMapType({
                getTileUrl: function(coord, zoom) {
                    return 'http://maps.nypl.org/warper/layers/tile/' + id
                        + '/' + zoom + '/' + coord.x + '/' + coord.y +
                        '.png';
                },
                tileSize: new google.maps.Size(256, 256),
                maxZoom: 9,
                minZoom: 0,
                name: 'NYPL Overlay'
            });
            this.map.overlayMapTypes.insertAt(0, overlay);
            this.year = jQuery(event.currentTarget).html();
        }
    },
    created: function() {
        if (this.showplaces === 'true') {
            const url = WritLarge.baseUrl + 'api/site/';
            jQuery.getJSON(url, (data) => {
                this.places = data;
            });
        }
    },
    mounted: function() {
        const elt = document.getElementById(this.mapName);

        this.geocoder = new google.maps.Geocoder();

        this.map = new google.maps.Map(elt, {
            mapTypeControl: false,
            clickableIcons: false,
            zoom: 12,
            center: new google.maps.LatLng(40.778572, -73.970616),
            fullscreenControlOptions: {
                position: google.maps.ControlPosition.RIGHT_BOTTOM,
            },
            mapTypeControlOptions: {
                mapTypeIds: ['styled_map']
            }
        });
        this.map.mapTypes.set('styled_map', lightGrayStyle);
        this.map.setMapTypeId('styled_map');

        this.map.data.setStyle(function(feature) {
            var color = 'gray';
            if (feature.getProperty('isColorful')) {
                color = feature.getProperty('color');
            }
            return ({
                fillOpacity: 0.0,
                strokeColor: color,
                strokeWeight: .5
            });
        });

        if (!this.isReadOnly()) {
            this.map.addListener('click', (ev) => {
                this.dropPin(ev);
            });
            this.map.data.addListener('click', (ev) => {
                this.dropPin(ev);
            });
        }

        if (this.latitude && this.longitude) {
            const position = new google.maps.LatLng(
                this.latitude, this.longitude);
            const marker = new google.maps.Marker({
                position: position,
                map: this.map,
                icon: WritLarge.staticUrl + 'png/pin-' + this.icon + '.png'
            });
            this.newPin = marker;
            this.address = this.title;
        }
    },
    updated: function() {
        this.places.forEach((site) => {
            if (!site.marker) {
                const position = new google.maps.LatLng(
                    site.place[0].latitude, site.place[0].longitude);
                const icon = site.category.length > 0 ?
                    site.category[0].group : 'other';
                const marker = new google.maps.Marker({
                    position: position,
                    map: this.map,
                    icon: WritLarge.staticUrl + 'png/pin-' + icon + '.png'
                });
                site.marker = marker;
                google.maps.event.addListener(marker, 'click', (ev) => {
                    this.clearNewPin();
                    this.selectedPlace = site;
                });
            }
        });
    }
};
