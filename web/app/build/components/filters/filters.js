"use strict";

angular.module("adagios.filters", []).filter("timeElapsed", [ function() {
    return function(start, end) {
        return console.log(end), null == end ? moment.unix(start).fromNow() : moment.unix(start).from(moment.unix(end), !0);
    };
} ]);