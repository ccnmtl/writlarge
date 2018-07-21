/* global google: true */
/* exported csrfSafeMethod, enlargeBounds, lightGrayStyle */
/* exported getVisibleContentHeight */


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


// Sourced from https://snazzymaps.com/style/151/ultra-light-with-labels
// Creator: http://www.haveasign.pl/, hawsan
// All SnazzyMap styles are offered under a
// Creative Commons CC0 1.0 Universal Public Domain Dedication
const lightGrayStyle = new google.maps.StyledMapType([
    {
        'featureType': 'water',
        'elementType': 'geometry',
        'stylers': [
            {
                'color': '#e9e9e9'
            },
            {
                'lightness': 17
            }
        ]
    },
    {
        'featureType': 'landscape',
        'elementType': 'geometry',
        'stylers': [
            {
                'color': '#f5f5f5'
            },
            {
                'lightness': 20
            }
        ]
    },
    {
        'featureType': 'road.highway',
        'elementType': 'geometry.fill',
        'stylers': [
            {
                'color': '#ffffff'
            },
            {
                'lightness': 17
            }
        ]
    },
    {
        'featureType': 'road.highway',
        'elementType': 'geometry.stroke',
        'stylers': [
            {
                'color': '#ffffff'
            },
            {
                'lightness': 29
            },
            {
                'weight': 0.2
            }
        ]
    },
    {
        'featureType': 'road.arterial',
        'elementType': 'geometry',
        'stylers': [
            {
                'color': '#ffffff'
            },
            {
                'lightness': 18
            }
        ]
    },
    {
        'featureType': 'road.local',
        'elementType': 'geometry',
        'stylers': [
            {
                'color': '#ffffff'
            },
            {
                'lightness': 16
            }
        ]
    },
    {
        'featureType': 'poi',
        'elementType': 'geometry',
        'stylers': [
            {
                'color': '#f5f5f5'
            },
            {
                'lightness': 21
            }
        ]
    },
    {
        'featureType': 'poi.park',
        'elementType': 'geometry',
        'stylers': [
            {
                'color': '#dedede'
            },
            {
                'lightness': 21
            }
        ]
    },
    {
        'elementType': 'labels.text.stroke',
        'stylers': [
            {
                'visibility': 'on'
            },
            {
                'color': '#ffffff'
            },
            {
                'lightness': 16
            }
        ]
    },
    {
        'elementType': 'labels.text.fill',
        'stylers': [
            {
                'saturation': 36
            },
            {
                'color': '#333333'
            },
            {
                'lightness': 40
            }
        ]
    },
    {
        'elementType': 'labels.icon',
        'stylers': [
            {
                'visibility': 'off'
            }
        ]
    },
    {
        'featureType': 'transit',
        'elementType': 'geometry',
        'stylers': [
            {
                'color': '#f2f2f2'
            },
            {
                'lightness': 19
            }
        ]
    },
    {
        'featureType': 'administrative',
        'elementType': 'geometry.fill',
        'stylers': [
            {
                'color': '#fefefe'
            },
            {
                'lightness': 20
            }
        ]
    },
    {
        'featureType': 'administrative',
        'elementType': 'geometry.stroke',
        'stylers': [
            {
                'color': '#fefefe'
            },
            {
                'lightness': 17
            },
            {
                'weight': 1.2
            }
        ]
    }
]);

function getVisibleContentHeight() {
    var viewportheight;

    // the more standards compliant browsers (mozilla/netscape/opera/IE7
    // use window.innerWidth and window.innerHeight
    if (typeof window.innerWidth !== 'undefined') {
        viewportheight = window.innerHeight;
    } else if (typeof document.documentElement !== 'undefined' &&
        typeof document.documentElement.clientWidth !== 'undefined' &&
            document.documentElement.clientWidth !== 0) {
        // IE6 in standards compliant mode (i.e. with a valid doctype
        // as the first line in the document)
        viewportheight = document.documentElement.clientHeight;
    } else {
        // older versions of IE
        viewportheight = document.getElementsByTagName('body')[0].clientHeight;
    }

    return viewportheight -
        (100 + $('header').outerHeight() +  $('.search-bar').outerHeight());
}