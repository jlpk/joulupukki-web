'use strict';

angular.module('joulupukki.live')

 
    .service('getProject', ['$http', 
        function ($http) {
            return function ($user, $project_name, $get_last_build) {
                var $url = '/v3/users/' + $user + '/' + $project_name + '?get_last_build=1';
                if ( $get_last_build == false ) {
                    $url = '/v3/users/' + $user + '/' + $project_name;
                }
                return $http.get($url)
                    .error(function () {
                        throw new Error('getProject : GET Request failed');
                    });
            };
        }])


    .service('getLatestProjects', ['$http',
        function ($http) {
            return function (username, pattern) {
                var url = '/v3/projects?limit=30&get_last_build=1'
                if (username) {
                    url = '/v3/projects?limit=30&get_last_build=1&username=' + username
                }
                else {
                    if (pattern){
                        url = '/v3/projects?limit=30&get_last_build=1&pattern=' + pattern
                    }
                }
                return $http.get(url)
                    .error(function () {
                        throw new Error('getLatestProjects : GET Request failed');
                    });
            };
        }])


    .service('toggleProject', ['$http',
        function ($http) {
            return function (username, project_name, state) {
                var url = '/v3/users' + username + '/' + project_name + '?';
                return $http.post($url)
                    .error(function () {
                        throw new Error('getProject : GET Request failed');
                });
            };
    }]);

