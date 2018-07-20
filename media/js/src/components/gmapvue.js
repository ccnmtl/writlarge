/* global google: true, enlargeBounds: true, lightGrayStyle: true */
/* global Promise */
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
            year: 'Present',
            searchResults: null
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
        siteIconUrl: function(site) {
            const icon = site.category.length > 0 ?
                site.category[0].group : 'other';
            return WritLarge.staticUrl + 'png/pin-' + icon + '.png';
        },
        clearNewPin: function(event) {
            if (!this.newPin) {
                return;
            }

            this.newPin.setMap(null);
            this.newPin = null;
            this.address = '';
            this.newTitle = '';
        },
        clearSearch: function() {
            this.searchResults = null;
            this.address = null;
            this.setPlacesOpacity(1);
        },
        clearSelectedPlace: function() {
            if (!this.selectedPlace) {
                return;
            }
            const url = this.siteIconUrl(this.selectedPlace);
            this.selectedPlace.marker.setIcon(url);
            this.selectedPlace = null;
        },
        clearAll: function() {
            this.clearNewPin();
            this.clearSearch();
            this.clearSelectedPlace();
        },
        setPlacesOpacity: function(opacity) {
            this.places.forEach((site) => {
                if (site.marker) {
                    site.marker.setOpacity(opacity);
                }
            });
        },
        selectPlace: function(site) {
            const OPTIMAL_ZOOM = 15;
            this.clearAll();

            site.marker.setIcon(); // show pointy red icon
            this.selectedPlace = site;
            this.address = this.selectedPlace.title;

            let bounds = this.map.getBounds();
            if (!bounds.contains(site.marker.getPosition()) ||
                    this.map.getZoom() < OPTIMAL_ZOOM) {
                // zoom in on the location, but not too close
                this.map.setZoom(OPTIMAL_ZOOM);
                this.map.panTo(site.marker.position);
            }
        },
        dropPin: function(event) {
            this.clearAll();

            this.newPin = new google.maps.Marker({
                position: event.latLng,
                map: this.map
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

            $.post(params, (site) => {
                site.marker = this.newPin;
                this.newPin = null;
                this.newTitle = '';

                site.iconUrl = this.siteIconUrl(site);
                google.maps.event.addListener(site.marker, 'click', (e) => {
                    this.selectPlace(site);
                });

                this.places.push(site);
                this.selectPlace(site);
            });
        },
        getAddress: function(event) {
            return this.address;
        },
        getPlace: function(event) {
            return this.selectedPlace || this.newPin;
        },
        searchForSite: function() {
            const url = WritLarge.baseUrl + 'api/site/?q=' + this.address;
            return $.getJSON(url);
        },
        searchForAddress: function() {
            const service = this.geocoder;
            const request = {
                query: this.address,
                fields: ['formatted_address', 'geometry', 'types']
            };

            return new Promise(function(resolve, reject) {
                service.findPlaceFromQuery(request, function(results) {
                    resolve(results);
                });
            });
        },
        geocode: function(event) {
            this.clearNewPin();
            this.clearSelectedPlace();

            $.when(this.searchForAddress())
                .done((addresses) => {
                    if (addresses) {
                        this.geocodeResults(addresses);
                    }
                });
        },
        search: function(event) {
            this.clearNewPin();
            this.clearSelectedPlace();
            this.searchResults = null;
            this.setPlacesOpacity(1);

            // Kick off a places search & a geocode search
            $.when(this.searchForSite(), this.searchForAddress())
                .done((places, addresses) => {
                    if (places[0].length === 1) {
                        this.singlePlaceResult(places[0][0]);
                    } else if (places[0].length > 1) {
                        this.placeResults(places[0]);
                    } else if (addresses) {
                        this.geocodeResults(addresses);
                    } else {
                        this.setPlacesOpacity(0.25);
                        this.searchResults = [];
                    }
                });
        },
        singlePlaceResult: function(result) {
            this.places.forEach((site) => {
                if (result.id === site.id) {
                    this.selectPlace(site);
                }
            });
        },
        placeResults: function(results) {
            this.bounds = new google.maps.LatLngBounds();
            this.searchResults = [];
            this.places.forEach((site) => {
                let opacity = 1;
                if (!results.find(function(obj) {
                    return obj.id === site.id;
                })) {
                    opacity = 0.25;
                } else {
                    this.searchResults.push(site);
                    this.bounds.extend(site.marker.position);
                    this.bounds = enlargeBounds(this.bounds);
                }
                site.marker.setOpacity(opacity);
            });
            this.map.fitBounds(this.bounds);
        },
        geocodeResults: function(results) {
            this.address = results[0].formatted_address;
            const position = results[0].geometry.location;

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
        },
        reverseGeocode: function(marker) {
            this.reverseGeocoder.geocode({
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
            const id = $(event.currentTarget).data('id');
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
            this.year = $(event.currentTarget).html();
        }
    },
    created: function() {
        if (this.showplaces === 'true') {
            const url = WritLarge.baseUrl + 'api/site/';
            $.getJSON(url, (data) => {
                this.places = data;
            });
        }
    },
    mounted: function() {
        const elt = document.getElementById(this.mapName);

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

        // initialize geocoder & places services
        this.reverseGeocoder = new google.maps.Geocoder();
        this.geocoder = new google.maps.places.PlacesService(this.map);

        // set initial marker if specified
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
                const marker = new google.maps.Marker({
                    position: position,
                    map: this.map,
                    icon: this.siteIconUrl(site)
                });
                site.marker = marker;
                site.iconUrl = this.siteIconUrl(site);
                google.maps.event.addListener(marker, 'click', (e) => {
                    this.selectPlace(site);
                });
            }
        });
    }
};
