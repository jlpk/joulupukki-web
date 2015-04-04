"use strict";

angular.element(document).ready(function() {
    $.get("components/config/config.json", function(data) {
        angular.module("adagios.config").config([ "readConfigProvider", function(readConfigProvider) {
            readConfigProvider.loadJSON(data);
        } ]), angular.bootstrap(document, [ "adagios" ]);
    }, "json");
}), angular.module("adagios", [ "ngRoute", "joulupukki.sidebar", "joulupukki.topbar", "adagios.config", "joulupukki.view.home" ]).config([ "$routeProvider", function($routeProvider) {
    $routeProvider.otherwise({
        redirectTo: "/"
    });
} ]);