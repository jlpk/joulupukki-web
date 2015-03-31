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

    .controller('HomeCtrl', ['$scope', '$routeParams', 'dashboardConfig', 'getLatestProjects',
        function ($scope, $routeParams, dashboardConfig, getLatestProjects) {

            //console.log($routeParams.user);

            /*$scope.$on('set_project', function(event, args) {
                console.log("DDDDDDDDDDDDD");
                console.log(event);
                console.log(args);
            });

/*
            var fields = ['state'],
                filters = {'isnot' : { 'state' : ['0'] }},
                apiName = 'hosts',
                components = [],
                component,
                config,
                viewName,
                i = 0;

            tableConfig.index = 0;

            if (!!$routeParams.view) {
                viewName = $routeParams.view;
            } else {
                throw new Error("ERROR : 'view' GET parameter must be the custom view name");
            }

            $scope.dashboardTitle = dashboardConfig[viewName].title;
            $scope.dashboardTemplate = dashboardConfig[viewName].template;
            $scope.dashboardRefreshInterval = dashboardConfig[viewName].refreshInterval;

            $scope.dashboardTactical = [];
            $scope.dashboardTables = [];

            components = dashboardConfig[viewName].components;

            for (i = 0; i < components.length; i += 1) {
                component = components[i];
                config = component.config;

                if (component.type === 'table') {
                    $scope.dashboardTables.push(new TableConfigObj(config));
                } else if (component.type === 'tactical') {
                    $scope.dashboardTactical.push(new TacticalConfigObj(config));
                }
            }

            getLatestProjects()
                .success(function (data) {
                    $scope.projects = data;
                });
*/
        }])
    .run(['readConfig', 'dashboardConfig', function (readConfig, dashboardConfig) {
        var viewsConfig = readConfig.data;

        angular.forEach(viewsConfig, function (config, view) {
            if (config.template === 'dashboard') {
                dashboardConfig[view] = config;
            }
        });
    }]);
