/* global google: true, enlargeBounds: true */
/* global lightGrayStyle: true */
/* exported GoogleMiniMapVue */

var GoogleMiniMapVue = {
    props: ['placeid'],
    template: '#google-mini-map-template',
    data: function() {
        return {
            mapName: 'the-map',
            place: null,
            address: null
        };
    },
    mounted: function() {
        const elt = document.getElementById(this.mapName);
        this.map = new google.maps.Map(elt, {
            mapTypeControl: false,
            clickableIcons: false,
            mapTypeControlOptions: {
                mapTypeIds: ['styled_map']
            }
        });
        this.map.mapTypes.set('styled_map', lightGrayStyle);
        this.map.setMapTypeId('styled_map');

        const url = WritLarge.baseUrl + 'api/site/' + this.placeid + '/';
        jQuery.getJSON(url, (data) => {
            this.place = data;

            const position = new google.maps.LatLng(
                this.place.place[0].latitude, this.place.place[0].longitude);
            const marker = new google.maps.Marker({
                position: position,
                map: this.map
            });
            this.place.marker = marker;
            this.address = this.place.place[0].title;
        });
    },
    updated: function() {
        this.bounds = new google.maps.LatLngBounds();

        // zoom in on the pin, but not too far
        this.bounds = new google.maps.LatLngBounds();
        this.bounds.extend(this.place.marker.position);
        this.bounds = enlargeBounds(this.bounds);
        this.map.fitBounds(this.bounds);
    }
};
