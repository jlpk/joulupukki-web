"use strict";

angular.module("joulupukki.filters", []).filter("timeElapsed", [ function() {
    return function(start, end) {
        return null == end ? moment.unix(start).fromNow() : moment.unix(start).from(moment.unix(end), !0);
    };
} ]);