'use strict';

angular.module('joulupukki.github')

 
    .service('getUserInfo', ['$http', '$cookies',
        function ($http, $cookies) {
            return function ($username) {
                if ($username) {
                    var token = $cookies.token
                    var url = 'http://api.github.com/users/' + $username + "?access_token=" + token
                    return $http.get(url)
                        .error(function () {
                            throw new Error('getBuild: GET Request failed');
                        });
                }
            };
        }])

