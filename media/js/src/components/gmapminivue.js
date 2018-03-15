/* global google: true, enlargeBounds: true */
/* global lightGrayStyle: true */
/* exported GoogleMiniMapVue */

var GoogleMiniMapVue = {
    props: ['latitude', 'longitude'],
    template: '#google-mini-map-template',
    data: function() {
        return {
            mapName: 'the-map',
        };
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

        const position = new google.maps.LatLng(
            parseFloat(this.latitude), parseFloat(this.longitude));
        this.marker = new google.maps.Marker({
            position: position,
            map: this.map
        });

        let bounds = new google.maps.LatLngBounds();
        bounds.extend(this.marker.position);
        bounds = enlargeBounds(bounds);
        this.map.fitBounds(bounds);
    }
};
