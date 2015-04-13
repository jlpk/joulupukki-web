'use strict';

angular.module('joulupukki.github')

 
    .service('getUserInfo', ['$http', '$cookies',
        function ($http, $cookies) {
            return function (username) {
                if (username) {
                    if ($cookies.token) {
                        var url = 'http://api.github.com/users/' + username + '?access_token=' + $cookies.token
                        return $http.get(url)
                            .error(function () {
                                throw new Error('getUserInfo: GET Request failed');
                            });
                    }
                }
            };
        }])

    .service('getCurrentUserInfo', ['$http', '$cookies',
        function ($http, $cookies) {
            return function () {
                if ($cookies.token) {
                    var url = 'http://api.github.com/user?access_token=' + $cookies.token
                    return $http.get(url)
                        .error(function () {
                            throw new Error('getCurrentUserInfo: GET Request failed');
                        });
                }
            };
        }])

    .service('getUserRepos', ['$http', '$cookies',
        function ($http, $cookies) {
            return function (username) {
                if ($cookies.token) {
                    var url = 'http://api.github.com/users/' + username + '/repos?access_token=' + $cookies.token
                    return $http.get(url)
                        .error(function () {
                            throw new Error('getUserRepos: GET Request failed');
                        });
                }
            };
        }])


    .service('getUserOrgs', ['$http', '$cookies',
        function ($http, $cookies) {
            return function (username) {
                if ($cookies.token) {
                    var url = 'http://api.github.com/users/' + username + '/orgs?access_token=' + $cookies.token
                    return $http.get(url)
                        .error(function () {
                            throw new Error('getUserOrgs: GET Request failed');
                        });
                }
            };
        }])
