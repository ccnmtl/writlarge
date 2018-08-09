/* global google: true, enlargeBounds: true, lightGrayStyle: true */
/* global Promise, getVisibleContentHeight, sanitize */
/* exported GoogleMapVue */

const GoogleMapVue = {
    props: ['readonly', 'showsites', 'latitude',
        'longitude', 'title', 'icon', 'autodrop',
        'slidermin', 'slidermax'],
    template: '#google-map-template',
    data: function() {
        return {
            map: null,
            mapName: 'the-map',
            newPin: null,
            newTitle: '',
            selectedSite: null,
            sites: [],
            searchTerm: '',
            searchResults: null,
            searchResultHeight: 0,
            year: 'Present',
            sliderName: 'the-slider',
            startYear: null,
            endYear: null
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
        getSearchTerm: function() {
            return this.searchTerm;
        },
        getSelectedSite: function() {
            return this.selectedSite || this.newPin;
        },
        getSiteById: function(siteId) {
            let result;
            this.sites.forEach((site) => {
                if (site.id === siteId) {
                    result = site;
                }
            });
            return result;
        },
        isReadOnly: function() {
            return this.readonly === 'true';
        },
        isSearching: function() {
            return this.searchResults && this.searchResults.length > 0;
        },
        siteIconUrl: function(site) {
            const icon = site.category.length > 0 ?
                site.category[0].group : 'other';
            return WritLarge.staticUrl + 'png/pin-' + icon + '.png';
        },
        markerOpacity: function(opacity) {
            this.sites.forEach((site) => {
                if (site.marker) {
                    site.marker.setOpacity(opacity);
                }
            });
        },
        markerShow: function(marker) {
            const OPTIMAL_ZOOM = 15;

            let bounds = this.map.getBounds();
            if (!bounds.contains(marker.getPosition()) ||
                    this.map.getZoom() < OPTIMAL_ZOOM) {
                // zoom in on the location, but not too close
                this.map.setZoom(OPTIMAL_ZOOM);
                this.map.panTo(marker.position);
            }
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
        },
        clearSelectedSite: function() {
            if (!this.selectedSite) {
                return;
            }
            // reset the icon to the site's category
            const url = this.siteIconUrl(this.selectedSite);
            this.selectedSite.marker.setIcon(url);
            this.selectedSite = null;
        },
        clearAll: function() {
            this.clearNewPin();
            this.clearSearch();
            this.clearSelectedSite();
        },
        selectSite: function(site) {
            if (site.marker.getOpacity() < 1) {
                return; // dimmed sites aren't clickable
            }

            this.clearNewPin();
            this.clearSelectedSite();

            site.marker.setIcon(); // show pointy red icon
            this.selectedSite = site;
            this.markerShow(site.marker);

            if (!this.isSearching()) {
                this.searchTerm = this.selectedSite.title;
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
        searchForSite: function() {
            const url = WritLarge.baseUrl + 'api/site/?' +
                'q=' + sanitize(this.searchTerm) +
                '&start=' + sanitize(this.startYear) +
                '&end=' + sanitize(this.endYear);
            return $.getJSON(url);
        },
        searchForAddress: function() {
            if (!this.searchTerm) {
                return Promise.resolve();
            }

            const self = this;
            return new Promise(function(resolve, reject) {
                self.geocoder.findPlaceFromQuery({
                    query: self.searchTerm,
                    fields: ['formatted_address', 'geometry', 'types']
                }, function(results) {
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
        resetSearch: function(event) {
            this.searchTerm = '';
            this.search();
        },
        search: function(event) {
            this.clearNewPin();
            this.clearSelectedSite();
            this.searchResults = null;
            $('html').addClass('busy');

            // Kick off a sites search & a geocode search
            $.when(this.searchForSite(), this.searchForAddress())
                .done((sites, addresses) => {
                    if (!this.searchTerm) {
                        // filtering solely by year range
                        this.siteResults(sites[0]);
                    } else if (sites[0].length === 1) {
                        // single site found
                        const site = this.getSiteById(sites[0][0].id);
                        this.searchResults = [site];
                        this.selectSite(site);
                    } else if (sites[0].length > 1) {
                        // multiple sites found via keyword + year range
                        this.searchResults = [];
                        const bounds = this.siteResults(sites[0]);
                        this.map.fitBounds(bounds);
                        this.searchResultHeight = getVisibleContentHeight();
                    } else if (addresses) {
                        // no sites found, try to display geocode result
                        this.geocodeResults(addresses);
                    } else {
                        // no results at all
                        this.markerOpacity(0.25);
                        this.searchResults = [];
                    }
                    $('html').removeClass('busy');
                });
        },
        siteResults: function(results) {
            let bounds = new google.maps.LatLngBounds();
            this.sites.forEach((site) => {
                let opacity = 1;
                if (!results.find(function(obj) {
                    return obj.id === site.id;
                })) {
                    // dim the icon, this site is not in the results
                    opacity = .25;
                } else if (this.searchTerm) {
                    this.searchResults.push(site);
                    bounds.extend(site.marker.position);
                    bounds = enlargeBounds(bounds);
                }
                site.marker.setOpacity(opacity);
            });
            return bounds;
        },
        geocodeResults: function(results) {
            this.searchTerm = results[0].formatted_address;
            const position = results[0].geometry.location;

            // zoom in on the location, but not too far
            let bounds = new google.maps.LatLngBounds();
            bounds.extend(position);
            bounds = enlargeBounds(bounds);
            this.map.fitBounds(bounds);

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
        },
        resize: function(event) {
            this.searchResultHeight = getVisibleContentHeight();
        },
        searchDetail: function(siteId) {
            const site = this.getSiteById(siteId);
            this.selectSite(site);
        },
        searchList: function(event) {
            this.clearSelectedSite();
        },
        searchByTag: function(tag) {
            this.searchTerm += ' tag:' + tag;
            this.search();
        },
        searchByCategory: function(category) {
            this.searchTerm += ' category:' + category;
            this.search();
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
        let elt = document.getElementById(this.mapName);

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
                this.markerShow(marker);

                google.maps.event.removeListener(listener);
            });
        }

        // eslint-disable-next-line scanjs-rules/call_addEventListener
        window.addEventListener('resize', this.resize);
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

        // @todo - this should be a vue component
        // create the slider
        if (!this.slider && this.slidermin && this.slidermax) {
            const start = parseInt(this.slidermin, 10);
            const end = parseInt(this.slidermax, 10);
            let elt = document.getElementById(this.sliderName);
            this.slider = this.$parent.noUiSlider.create(elt, {
                start: [start, end],
                connect: true,
                step: 1,
                tooltips: false,
                range: {
                    'min': start,
                    'max': end
                }
            });
            this.startYear = start;
            this.endYear = end;

            // hook up events
            this.slider.on('slide', (values) => {
                this.startYear = parseInt(values[0], 10);
                this.endYear = parseInt(values[1], 10);
            });
            this.slider.on('set', (values) => {
                this.search();
            });
        }
    }
};
