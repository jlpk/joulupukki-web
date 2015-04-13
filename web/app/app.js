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
    'joulupukki.topbar',
    'joulupukki.config',
    'joulupukki.view.repositories',
    'joulupukki.view.404',
    'joulupukki.view.login',
    'joulupukki.view.account',
])

    .config(['$routeProvider', function ($routeProvider) {
        $routeProvider.when('/', {
            redirectTo: '/repositories'
        })

        $routeProvider.otherwise({redirectTo: '/404'});
    }])



