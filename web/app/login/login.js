'use strict';

angular.module('joulupukki.view.login', ['ngRoute',
                                         'ngCookies'
                                       ])

    .config(['$routeProvider', function ($routeProvider) {
/*        $routeProvider.when('/', {
            templateUrl: 'login/login.html',
            controller: 'loginCtrl'
        })*/
        $routeProvider.when('/login', {
            templateUrl: 'login/login.html',
            controller: 'loginCtrl'
        })
        $routeProvider.when('/login/github', {
            templateUrl: 'login/login.html',
            controller: 'loginCtrl'
        })
    }])

    .controller('loginCtrl', ['$scope', '$rootScope', '$routeParams',
                              '$location', '$http', '$cookies',
        function ($scope, $rootScope, $routeParams, $location, $http, $cookies) {
            // TODO found why this controller is called twice
            if ($routeParams.code) {
                var code = $routeParams.code;
                var data = {code: code }
                var url = "/v3/auth/login"
                $http.post(url, data)
                    .success(function(data, status, headers, config){
                        // TODO store access token
                        if (data != 'null'){ 
                            $cookies.token = data
                        }
                    })
            }

           
        }])

   
