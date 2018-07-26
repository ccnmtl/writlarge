/* global google: true, enlargeBounds: true */
/* global lightGrayStyle: true */
/* exported GoogleMiniMapVue */

var GoogleMiniMapVue = {
    props: ['latitude', 'longitude', 'icon', 'siteid'],
    template: '#google-mini-map-template',
    data: function() {
        return {
            mapName: 'the-map',
            site: null
        };
    },
    methods: {
        iconUrl: function() {
            return WritLarge.staticUrl + 'png/pin-' + this.icon + '.png';
        }
    },
    created: function() {
        if (this.siteid) {
            const url = WritLarge.baseUrl + 'api/site/' +  this.siteid + '/';
            jQuery.getJSON(url, (data) => {
                this.site = data;
            });
        }
    },
    mounted: function() {
        const elt = document.getElementById(this.mapName);
        this.map = new google.maps.Map(elt, {
            mapTypeControl: false,
            clickableIcons: false,
            mapTypeControlOptions: {
                mapTypeIds: ['styled_map']
            },
        });
        this.map.mapTypes.set('styled_map', lightGrayStyle);
        this.map.setMapTypeId('styled_map');

        if (this.latitude && this.longitude) {
            const position = new google.maps.LatLng(
                parseFloat(this.latitude), parseFloat(this.longitude));
            this.marker = new google.maps.Marker({
                position: position,
                map: this.map,
                icon: this.iconUrl()
            });

            let bounds = new google.maps.LatLngBounds();
            bounds.extend(this.marker.position);
            bounds = enlargeBounds(bounds);
            this.map.fitBounds(bounds);
        }
    },
    updated: function() {
        if (this.site) {
            let bounds = new google.maps.LatLngBounds();
            this.site.place.forEach((place) => {
                const position = new google.maps.LatLng(
                    place.latitude, place.longitude);
                const marker = new google.maps.Marker({
                    position: position,
                    map: this.map,
                    icon: this.iconUrl()
                });
                bounds.extend(marker.position);
                bounds = enlargeBounds(bounds);
            });
            this.map.fitBounds(bounds);
        }
    }
};
