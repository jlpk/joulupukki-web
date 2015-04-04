'use strict';

angular.module('joulupukki.view.home', ['ngRoute',
//                                          'adagios.tactical',
                                          'joulupukki.main',
                                          'joulupukki.live'
                                         ])

    .value('dashboardConfig', {})

    .config(['$routeProvider', function ($routeProvider) {
        $routeProvider.when('/home/', {
            templateUrl: 'home/home.html',
            controller: 'HomeCtrl'
        })
        $routeProvider.when('/home/:user', {
            templateUrl: 'home/home.html',
            controller: 'HomeCtrl'
        })
        $routeProvider.when('/home/:user/:project', {
            templateUrl: 'home/home.html',
            controller: 'HomeCtrl',
            controllerAs: 'project'
        })
        $routeProvider.when('/home/:user/:project/builds/', {
            templateUrl: 'home/home.html',
            controller: 'HomeCtrl',
            controllerAs: 'history'
        })
        $routeProvider.when('/home/:user/:project/builds/:build', {
            templateUrl: 'home/home.html',
            controller: 'HomeCtrl',
            controllerAs: 'build'
        })
        $routeProvider.when('/home/:user/:project/builds/:build/output', {
            templateUrl: 'home/home.html',
            controller: 'HomeCtrl',
            controllerAs: 'output'
        })
        $routeProvider.when('/home/:user/:project/builds/:build/jobs/:job', {
            templateUrl: 'home/home.html',
            controller: 'HomeCtrl',
            controllerAs: 'job'
        })
    }])

    .controller('HomeCtrl', ['$scope', '$rootScope', '$routeParams', 'dashboardConfig', 'getLatestProjects',
        function ($scope, $rootScope, $routeParams, dashboardConfig, getLatestProjects) {
        }])
    .run(['readConfig', 'dashboardConfig', function (readConfig, dashboardConfig) {
        var viewsConfig = readConfig.data;

        angular.forEach(viewsConfig, function (config, view) {
            if (config.template === 'dashboard') {
                dashboardConfig[view] = config;
            }
        });
    }]);
