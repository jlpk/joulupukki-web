'use strict';

angular.module('joulupukki.view.account', ['ngRoute',
                                           'ngCookies',
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
        function ($scope, $rootScope, $routeParams, $window, $http, $cookies,
                  getUserInfo, getUserRepos, getUserOrgs) {
            if ($routeParams.githubaccount) {
                $scope.username = $routeParams.githubaccount
            }
            else {
                $scope.username = $cookies.username
            }
            getUserInfo($scope.username)
                .success(function(data, status, headers, config){
                    $scope.name = data.name
                })
            getUserRepos($scope.username)
                .success(function(data, status, headers, config){
                    $scope.repos = data
                })
            getUserOrgs($cookies.username)
                .success(function(data, status, headers, config){
                    $scope.orgs = data
                })
        }])

