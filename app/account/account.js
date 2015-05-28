'use strict';

angular.module('joulupukki.view.account', ['ngRoute',
                                           'ngCookies',
                                           'frapontillo.bootstrap-switch',
                                           'joulupukki.live'
                                           ])

    .config(['$routeProvider', function ($routeProvider) {
        $routeProvider.when('/account/:account/profile', {
            templateUrl: 'account/account.html',
            controller: 'accountCtrl'
        })
        $routeProvider.when('/account/:account/repositories', {
            templateUrl: 'account/repositories.html',
            controller: 'repositoriesCtrl'
        })
    }])

    .controller('repositoriesCtrl', ['$scope', '$rootScope', '$routeParams',
                                '$window', '$http', '$cookies',
                                'getUser', 'enableProject',
                                'SyncUserRepos', 'SyncUserOrgs',
        function ($scope, $rootScope, $routeParams, $window, $http, $cookies,
                  getUser, enableProject, SyncUserRepos, SyncUserOrgs) {
            $scope.username = $cookies.username
            // If not loggedin
            if (!$scope.username) {
                // go to auth page 
                var url = "#/auth/"
                $window.location.href = url;
            }
            if ($routeParams.account) {
                $scope.selected_username = $routeParams.account
            }
            else {
                // bad url should be not possible
                var url = "#/auth/"
                $window.location.href = url;
            }

            $scope.switchStatus = true
            $scope.enableProject = enableProject

            // TODO define this in a service
            $scope.sync_repos = function() {
                SyncUserRepos($scope.selected_username, $cookies.token)
                    .success(function(data, status, headers, config){
                        getUser($scope.selected_username, $cookies.token)
                            .success(function(data, status, headers, config){
                                $scope.projects = data.projects
                        })
                })
            };



            // Update organisations
            SyncUserOrgs($scope.username, $cookies.token)
                //.success(function(data, status, headers, config){
                //})

            // Get user orgs
            getUser($scope.username, $cookies.token)
                .success(function(data, status, headers, config){
                    $scope.orgs = data.orgs
                })
            // Get selected user/org projects
            getUser($scope.selected_username, $cookies.token)
                .success(function(data, status, headers, config){
                    $scope.projects = data.projects
                })

        }])

