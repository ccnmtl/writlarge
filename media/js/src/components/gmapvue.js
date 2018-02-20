/* global google: true, enlargeBounds: true */
/* exported GoogleMapVue */

var GoogleMapVue = {
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
            selectedPlace: null
        };
    },
    methods: {
        clearNewPin: function(event) {
            if (this.newPin) {
                this.newPin.setMap(null);
                this.newPin = null;
                this.address = '';
            }
        },
        dropPin: function(event) {
            this.clearNewPin();
            this.selectedPlace = null;

            this.newPin = new google.maps.Marker({
                position: event.latLng,
                map: this.map
            });

            this.reverseGeocode(this.newPin);
        },
        savePin: function(event) {
            const data = {
                'title': this.newTitle,
                'latlng': this.newPin.position.toJSON()
            };

            const params = {
                url: WritLarge.baseUrl + 'api/place/',
                dataType: 'json',
                contentType: 'application/json',
                data: JSON.stringify(data)
            };

            $.post(params, (response) => {
                response.marker = this.newPin;
                this.places.push(response);
                this.selectedPlace = response;
                this.newPin = null;
            });
        },
        viewPin: function(event) {
            // eslint-disable-next-line scanjs-rules/assign_to_href
            window.location.href = '/place/view/' + this.selectedPlace.id;
        },
        deselectPlace: function(event) {
            this.selectedPlace = null;
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

                    // zoom in on the pin, but not too far
                    this.bounds = new google.maps.LatLngBounds();
                    this.bounds.extend(this.newPin.position);
                    this.bounds = enlargeBounds(this.bounds);
                    this.map.fitBounds(this.bounds);
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
        const url = WritLarge.baseUrl + 'api/place/';
        jQuery.getJSON(url, (data) => {
            this.places = data;
        });
    },
    mounted: function() {
        const elt = document.getElementById(this.mapName);

        this.geocoder = new google.maps.Geocoder();

        this.map = new google.maps.Map(elt, {
            mapTypeControl: false,
            clickableIcons: false
        });
        this.map.addListener('click', (ev) => {
            this.dropPin(ev);
        });
    },
    updated: function() {
        this.bounds = new google.maps.LatLngBounds();
        this.places.forEach((place) => {
            const position = new google.maps.LatLng(
                place.latitude, place.longitude);
            const marker = new google.maps.Marker({
                position: position,
                map: this.map
            });
            place.marker = marker;
            google.maps.event.addListener(marker, 'click', (ev) => {
                this.clearNewPin();
                this.selectedPlace = place;
            });
            if (!this.newPin) {
                this.map.fitBounds(this.bounds.extend(position));
            }
        });
    }
};
