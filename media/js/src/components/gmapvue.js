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
            bounds: null
        };
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
        this.map = new google.maps.Map(elt);
    },
    updated: function() {
        this.sites.forEach((site) => {
            const position = new google.maps.LatLng(
                site.latitude, site.longitude);
            const marker = new google.maps.Marker({
                position,
                map: this.map
            });
            this.markers.push(marker);
            this.map.fitBounds(this.bounds.extend(position));
        });
    }
};
