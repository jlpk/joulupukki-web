'use strict';

angular.module('joulupukki.view.account', ['ngRoute',
                                           'ngCookies',
                                           'frapontillo.bootstrap-switch',
                                           'joulupukki.github'
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
                                'getUserInfo', 'getUserRepos', 'getUserOrgs',
                                'toggleProject',
        function ($scope, $rootScope, $routeParams, $window, $http, $cookies,
                  getUserInfo, getUserRepos, getUserOrgs, toggleProject) {
            $scope.username = $cookies.username
            $scope.switchStatus = true
            $scope.toggle_project = toggleProject()
            if ($routeParams.githubaccount) {
                $scope.github_username = $routeParams.githubaccount
            }
            else {
                $scope.github_username = $scope.username
            }
            getUserInfo($scope.username)
            .success(function(data, status, headers, config){
                $scope.name = data.name
                })
            getUserInfo($scope.github_username)
                .success(function(data, status, headers, config){
                    $scope.github_name = data.name
                })
            getUserRepos($scope.github_username)
                .success(function(data, status, headers, config){
                    $scope.github_repos = data
                })
            getUserOrgs($scope.username)
                .success(function(data, status, headers, config){
                    $scope.orgs = data
                })
        }])

