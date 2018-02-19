/* global google: true */
/* exported GoogleMapVue */

var GoogleMapVue = {
    template: '#google-map-template',
    data: function() {
        return {
            mapName: 'the-map',
            sites: [],
            map: null,
            bounds: null,
            address: '',
            newPin: null,
            newTitle: '',
            newType: '',
            selectedSite: null
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
            this.selectedSite = null;

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
                url: WritLarge.baseUrl + 'api/site/',
                dataType: 'json',
                contentType: 'application/json',
                data: JSON.stringify(data)
            };

            $.post(params, (response) => {
                response.marker = this.newPin;
                this.sites.push(response);
                this.selectedSite = response;
                this.newPin = null;
            });
        },
        viewPin: function(event) {
            // eslint-disable-next-line scanjs-rules/assign_to_href
            window.location.href = '/site/view/' + this.selectedSite.id;
        },
        deselectSite: function(event) {
            this.selectedSite = null;
        },
        enlargeBounds: function(bounds) {
            // Don't zoom in too far on only one marker
            // http://stackoverflow.com/questions/3334729/
            // google-maps-v3-fitbounds-zoom-too-close-for-single-marker
            if (bounds.getNorthEast().equals(bounds.getSouthWest())) {
                var extendPoint1 = new google.maps.LatLng(
                    bounds.getNorthEast().lat() + 0.001,
                    bounds.getNorthEast().lng() + 0.001);
                var extendPoint2 = new google.maps.LatLng(
                    bounds.getNorthEast().lat() - 0.001,
                    bounds.getNorthEast().lng() - 0.001);
                bounds.extend(extendPoint1);
                bounds.extend(extendPoint2);
            }
            return bounds;
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
                    this.bounds = this.enlargeBounds(this.bounds);
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
        const url = WritLarge.baseUrl + 'api/site/';
        jQuery.getJSON(url, (data) => {
            this.sites = data;
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
        this.sites.forEach((site) => {
            const position = new google.maps.LatLng(
                site.latitude, site.longitude);
            const marker = new google.maps.Marker({
                position: position,
                map: this.map
            });
            site.marker = marker;
            google.maps.event.addListener(marker, 'click', (ev) => {
                this.clearNewPin();
                this.selectedSite = site;
            });
            if (!this.newPin) {
                this.map.fitBounds(this.bounds.extend(position));
            }
        });
    }
};
