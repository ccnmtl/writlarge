/* global google: true */
/* exported csrfSafeMethod, enlargeBounds */

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function enlargeBounds(bounds) {
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
}