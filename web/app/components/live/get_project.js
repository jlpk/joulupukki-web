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
