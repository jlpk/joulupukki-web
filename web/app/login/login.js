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
                              '$window', '$http', '$cookies',
        function ($scope, $rootScope, $routeParams, $window, $http, $cookies) {
        }])

    .controller('loginCtrl', ['$scope', '$rootScope', '$routeParams',
                              '$window', '$http', '$cookies',
                              'postUser',
        function ($scope, $rootScope, $routeParams, $window, $http, $cookies, postUser) {
            // Test if the user is authenticated
            if (!$cookies.token) {
                // User not authenticated
                // Test we have already ask github authorization
                if (!$routeParams.code) {
                    // We don't have github authorizations
                    // So go ask them !
                    var url = "https://github.com/login/oauth/authorize?client_id=666ff51d51afc14ab79c&scope=user:email,read:org,repo:status,repo_deployment,write:repo_hook&redirect_uri=http://jlpk.org/app/#/auth/login"
                    // Go to github
                    $window.location.href = url; 
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
                                // login APi return token
                                $cookies.token = data.access_token
                                $cookies.username = data.username
                                $rootScope.$emit('token_changed')
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
