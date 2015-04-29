'use strict';

angular.module('joulupukki.view.404', ['ngRoute',
                                       ])

    .config(['$routeProvider', function ($routeProvider) {
        $routeProvider.when('/404', {
            templateUrl: '404/404.html',
            controller: '404Ctrl'
        })
    }])

    .controller('404Ctrl', ['$scope', '$rootScope', '$routeParams',
        function ($scope, $rootScope, $routeParams) {
        }])

   
