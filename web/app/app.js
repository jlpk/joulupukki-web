'use strict';

angular.element(document).ready(function () {

    $.get('components/config/config.json', function (data) {

        angular.module('joulupukki.config').config(['readConfigProvider', function (readConfigProvider) {
            readConfigProvider.loadJSON(data);
        }]);

        angular.bootstrap(document, ['joulupukki']);
    }, "json");

});

angular.module('joulupukki', [
    'ngRoute',
    'joulupukki.sidebar',
    'joulupukki.topbar',
    'joulupukki.config',
    'joulupukki.view.home',
])

    .config(['$routeProvider', function ($routeProvider) {
        $routeProvider.otherwise({redirectTo: '/'});
    }]);
