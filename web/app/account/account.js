'use strict';

angular.module('joulupukki.view.account', ['ngRoute',
                                           'ngCookies',
                                           'frapontillo.bootstrap-switch',
                                           'joulupukki.live'
                                           ])

    .config(['$routeProvider', function ($routeProvider) {
        $routeProvider.when('/account', {
            templateUrl: 'account/account.html',
            controller: 'accountCtrl'
        })
        $routeProvider.when('/account/:githubaccount', {
            templateUrl: 'account/account.html',
            controller: 'accountCtrl'
        })
    }])

    .controller('accountCtrl', ['$scope', '$rootScope', '$routeParams',
                                '$window', '$http', '$cookies',
                                'getUser', 
                                'enableProject',
        function ($scope, $rootScope, $routeParams, $window, $http, $cookies,
                  getUser, enableProject) {
            $scope.username = $cookies.username
            $scope.switchStatus = true
            $scope.enableProject = enableProject

$scope.toto = function() {
        console.log("TOT")
      };
            if ($routeParams.githubaccount) {
                $scope.selected_username = $routeParams.githubaccount
            }
            else {
                $scope.selected_username = $scope.username
            }

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

