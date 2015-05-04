'use strict';

angular.module('joulupukki.view.repositories', ['ngRoute',
                                        'joulupukki.live',
                                        'joulupukki.sidebar',
                                        'joulupukki.main'
                                        ])

    .value('dashboardConfig', {})

    .config(['$routeProvider', function ($routeProvider) {
        $routeProvider.when('/repositories/', {
            templateUrl: 'repositories/repositories.html',
            controller: 'RepositoriesCtrl'
        })
        $routeProvider.when('/repositories/:user', {
            templateUrl: 'repositories/repositories.html',
            controller: 'RepositoriesCtrl'
        })
        $routeProvider.when('/repositories/:user/:project', {
            templateUrl: 'repositories/repositories.html',
            controller: 'RepositoriesCtrl',
            controllerAs: 'project'
        })
        $routeProvider.when('/repositories/:user/:project/builds/', {
            templateUrl: 'repositories/repositories.html',
            controller: 'RepositoriesCtrl',
            controllerAs: 'history'
        })
        $routeProvider.when('/repositories/:user/:project/builds/:build', {
            templateUrl: 'repositories/repositories.html',
            controller: 'RepositoriesCtrl',
            controllerAs: 'build'
        })
        $routeProvider.when('/repositories/:user/:project/builds/:build/output', {
            templateUrl: 'repositories/repositories.html',
            controller: 'RepositoriesCtrl',
            controllerAs: 'output'
        })
        $routeProvider.when('/repositories/:user/:project/builds/:build/log', {
            templateUrl: 'repositories/repositories.html',
            controller: 'RepositoriesCtrl',
            controllerAs: 'buildlog'
        })
        $routeProvider.when('/repositories/:user/:project/builds/:build/jobs/:job', {
            templateUrl: 'repositories/repositories.html',
            controller: 'RepositoriesCtrl',
            controllerAs: 'job'
        })
    }])

    .controller('RepositoriesCtrl', ['$scope', '$rootScope', '$routeParams', 'dashboardConfig', 'getLatestProjects',
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
