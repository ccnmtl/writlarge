/* global google: true */
/* exported GoogleMapVue */

var GoogleMapVue = {
    props: ['name'],
    template: '<div class="google-map" :id="mapName"></div>',
    data: function() {
        return {
            mapName: 'the-map',
            markerCoordinates: [{
                latitude: 40.7128,
                longitude: -74.0060
            }],
            map: null,
            markers: [],
            bounds: null
        };
    },
    mounted: function() {
        this.bounds = new google.maps.LatLngBounds();
        const elt = document.getElementById(this.mapName);
        this.map = new google.maps.Map(elt);
        this.markerCoordinates.forEach((coord) => {
            const position = new google.maps.LatLng(
                coord.latitude, coord.longitude);
            const marker = new google.maps.Marker({
                position,
                map: this.map
            });
            this.markers.push(marker);
            this.map.fitBounds(this.bounds.extend(position));
        });
    }
};
