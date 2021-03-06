'use strict';

angular.module('joulupukki.view.login', ['ngRoute',
                                         'ngCookies',
                                         'joulupukki.live'
                                       ])

    .config(['$routeProvider', function ($routeProvider) {
        $routeProvider.when('/auth', {
            templateUrl: 'login/login.html',
            controller: 'authCtrl'
        })
        $routeProvider.when('/auth/login', {
            template: '<div ng-controller="loginCtrl"></div>'
        })
        $routeProvider.when('/auth/logout', {
            template: '<div ng-controller="logoutCtrl"></div>'
        })
    }])

    .controller('authCtrl', ['$scope', '$rootScope', '$routeParams',
                              '$window', '$http', '$cookies', 'getActiveAuth',
        function ($scope, $rootScope, $routeParams, $window, $http, $cookies, getActiveAuth) {
            $scope.jlpk_web_url = window.location.protocol + "//" + $window.location.hostname + $window.location.pathname;
            $scope.active_auth = new Array();
            getActiveAuth()
                .success(function(data, status, headers, config){
                    $scope.active_auth = data.result.active_auth;
                    if ($scope.active_auth == 'github') {
                        getActiveAuthId()
                            .success(function(data){
                                $scope.active_auth_id = data.result.github_id
                            })
                    }
                });
        }])

    .controller('loginCtrl', ['$scope', '$rootScope', '$routeParams',
                              '$window', '$http', '$cookies',
                              'postUser',
        function ($scope, $rootScope, $routeParams, $window, $http, $cookies, postUser) {
            $scope.jlpk_web_url = window.location.protocol + "//" + $window.location.hostname + $window.location.pathname;
            // Test if the user is authenticated
            if (!$cookies.token) {
                // User not authenticated
                // Test we have already ask github authorization
                if (!$routeParams.code) {
                    // We don't have github authorizations
                    // So go ask them !
                    getActiveAuthId()
                        .success(function(data){
                            var url = "https://github.com/login/oauth/authorize?client_id=" + data.result.github_id + "&scope=user:email,read:org,repo:status,repo_deployment,write:repo_hook&redirect_uri=" + $scope.jlpk_web_url + "#/auth/login";
                            // Go to github
                            $window.location.href = url;
                        })
                }
                else {
                    // Here is the return from github
                    // (github give us the "code" params"
                    var code = $routeParams.code;
                    var data = {code: code }
                    var url = "/v3/auth/login"
                    // Try to login in joulupukki api
                    $http.post(url, data)
                        // Login success
                        .success(function(data, status, headers, config){
                            if (data != 'null'){ 
                                // login API return token
                                $cookies.token = data.access_token
                                $cookies.username = data.username
                                $rootScope.$emit('token_changed')
                                // Launch user update
                                // go to repo page
                                var url = "#/repositories"
                                $window.location.href = url; 
                            }
                            else {
                                // go to auth page 
                                var url = "#/auth/"
                                $window.location.href = url; 
                            }
                        })
                        // Login error
                        .error(function(data, status, headers, config){
                            // go to auth page 
                            var url = "#/auth/"
                            $window.location.href = url; 
                        })

                }
            }
           
        }])


    .controller('logoutCtrl', ['$scope', '$rootScope', '$routeParams',
                              '$window', '$http', '$cookies',
        function ($scope, $rootScope, $routeParams, $window, $http, $cookies) {
            // Delete cookies
            delete $cookies.token;
            delete $cookies.username;
            $rootScope.$emit('token_changed')
            // go to auth page 
            var url = "#/auth/"
            $window.location.href = url; 
        }])
