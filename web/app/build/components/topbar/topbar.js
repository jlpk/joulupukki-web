"use strict";

angular.module("joulupukki.topbar", [ "joulupukki.live" ]).controller("TopBarCtrl", [ "$scope", function() {} ]).directive("jlpkTopbar", function() {
    return {
        restrict: "E",
        templateUrl: "components/topbar/topbar.html"
    };
});