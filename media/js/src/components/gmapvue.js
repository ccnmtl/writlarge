/* global google: true, enlargeBounds: true, lightGrayStyle: true */
/* global Promise */
/* exported GoogleMapVue */

const GoogleMapVue = {
    props: ['readonly', 'showsites', 'latitude',
        'longitude', 'title', 'icon', 'autodrop'],
    template: '#google-map-template',
    data: function() {
        return {
            mapName: 'the-map',
            sites: [],
            map: null,
            bounds: null,
            searchTerm: '',
            newPin: null,
            newTitle: '',
            newType: '',
            selectedSite: null,
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
            this.searchTerm = '';
            this.newTitle = '';
        },
        clearSearch: function() {
            this.searchResults = null;
            this.searchTerm = null;
            this.setMarkerOpacity(1);
        },
        clearSelectedSite: function() {
            if (!this.selectedSite) {
                return;
            }
            const url = this.siteIconUrl(this.selectedSite);
            this.selectedSite.marker.setIcon(url);
            this.selectedSite = null;
        },
        clearAll: function() {
            this.clearNewPin();
            this.clearSearch();
            this.clearSelectedSite();
        },
        setMarkerOpacity: function(opacity) {
            this.sites.forEach((site) => {
                if (site.marker) {
                    site.marker.setOpacity(opacity);
                }
            });
        },
        selectSite: function(site) {
            this.clearAll();

            site.marker.setIcon(); // show pointy red icon
            this.selectedSite = site;
            this.searchTerm = this.selectedSite.title;

            this.showMarker(site.marker);
        },
        showMarker: function(marker) {
            const OPTIMAL_ZOOM = 15;

            let bounds = this.map.getBounds();
            if (!bounds.contains(marker.getPosition()) ||
                    this.map.getZoom() < OPTIMAL_ZOOM) {
                // zoom in on the location, but not too close
                this.map.setZoom(OPTIMAL_ZOOM);
                this.map.panTo(marker.position);
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
                    'title': this.searchTerm,
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
                    this.selectSite(site);
                });

                this.sites.push(site);
                this.selectSite(site);
            });
        },
        getAddress: function(event) {
            return this.searchTerm;
        },
        getSelectedSite: function(event) {
            return this.selectedSite || this.newPin;
        },
        searchForSite: function() {
            const url = WritLarge.baseUrl + 'api/site/?q=' + this.searchTerm;
            return $.getJSON(url);
        },
        searchForAddress: function() {
            const service = this.geocoder;
            const request = {
                query: this.searchTerm,
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
            this.clearSelectedSite();

            $.when(this.searchForAddress())
                .done((addresses) => {
                    if (addresses) {
                        this.geocodeResults(addresses);
                    }
                });
        },
        search: function(event) {
            this.clearNewPin();
            this.clearSelectedSite();
            this.searchResults = null;
            this.setMarkerOpacity(1);

            // Kick off a sites search & a geocode search
            $.when(this.searchForSite(), this.searchForAddress())
                .done((sites, addresses) => {
                    if (sites[0].length === 1) {
                        this.singleSiteResult(sites[0][0]);
                    } else if (sites[0].length > 1) {
                        this.siteResults(sites[0]);
                    } else if (addresses) {
                        this.geocodeResults(addresses);
                    } else {
                        this.setMarkerOpacity(0.25);
                        this.searchResults = [];
                    }
                });
        },
        singleSiteResult: function(result) {
            this.sites.forEach((site) => {
                if (result.id === site.id) {
                    this.selectSite(site);
                }
            });
        },
        siteResults: function(results) {
            this.bounds = new google.maps.LatLngBounds();
            this.searchResults = [];
            this.sites.forEach((site) => {
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
            this.searchTerm = results[0].formatted_address;
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
                    this.searchTerm = responses[0].formatted_address;
                } else {
                    this.searchTerm = '';
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
        if (this.showsites === 'true') {
            const url = WritLarge.baseUrl + 'api/site/';
            $.getJSON(url, (data) => {
                this.sites = data;
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

        // initialize geocoder & Google's places services
        this.reverseGeocoder = new google.maps.Geocoder();
        this.geocoder = new google.maps.places.PlacesService(this.map);

        // set initial address marker if specified in properties
        if (this.latitude && this.longitude) {
            const listener = this.map.addListener('idle', (ev) => {
                const position = new google.maps.LatLng(
                    this.latitude, this.longitude);
                const marker = new google.maps.Marker({
                    position: position,
                    map: this.map,
                    icon: WritLarge.staticUrl + 'png/pin-' +
                        this.icon + '.png'
                });
                this.newPin = marker;
                this.searchTerm = this.title;
                this.showMarker(marker);

                google.maps.event.removeListener(listener);
            });
        }
    },
    updated: function() {
        this.sites.forEach((site) => {
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
                    this.selectSite(site);
                });
            }
        });
    }
};
