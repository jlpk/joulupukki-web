'use strict';

angular.module('joulupukki.view.login.gitlab', ['ngRoute',
                                                'ngCookies',
                                                'joulupukki.live'
                                                ])

    .config(['$routeProvider', function ($routeProvider) {
        $routeProvider.when('/auth/login/gitlab', {
            templateUrl: 'login/gitlab/login.html',
            controller: 'GitlabLoginCtrl'
        })
    }])

    .controller('GitlabLoginCtrl', ['$scope', '$rootScope', '$routeParams',
                                    '$window', '$http', '$cookies',
                                    'postUser',
        function ($scope, $rootScope, $routeParams, $window, $http, $cookies, postUser) {
            // Test if the user is authenticated
            $scope.login = function(credential) {
                if (! credential.username || ! credential.password) {
                    // TODO error
                }
                var data = {"username": credential.username,
                            "password": credential.password}
                $http.post("/v3/auth/login", data)
                    .success(function(data, status, headers, config){
                        console.log("SSS")
                    })
                    .error(function(data, status, headers, config){
                         console.log("EEE")
                    })                   
            }

            

            if (!$cookies.token) {
                // User not authenticated
                var code = $routeParams.code;
                var data = {code: code }
                var url = "/v3/auth/login"
                // Try to login in joulupukki api
/*
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
*/
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
