'use strict';

angular.module('adagios.filters', [])

    .filter('timeElapsed', [function () {
        return function (start, end) {
            if (end == null) {
                return moment.unix(start).fromNow();
            }
            return moment.unix(start).from(moment.unix(end), true);
        };
    }])


