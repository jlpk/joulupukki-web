'use strict';

angular.module('joulupukki.live')

 
    .service('getActiveAuth', ['$http', 
        function ($http) {
            return function () {
                return $http.get('/v3/auth/active')
                    .error(function () {
                        throw new Error('getActiveAuth: GET Request failed');
                    });
            };
        }])


    .service('getActiveAuthId', ['$http',
        function ($http) {
            return function () {
                return $http.get('/v3/externalservice/clientid')
                    .error(function () {
                        throw new Error('getActiveAuthId: GET Request failed');
                    });
            };
        }])


    .service('getUser', ['$http', 
        function ($http) {
            return function (username, access_token) {
                return $http.get('/v3/users/' + username + "?access_token=" + access_token)
                    .error(function () {
                        throw new Error('getUser: GET Request failed');
                    });
            };
        }])



    .service('SyncUserRepos', ['$http', '$cookies',
        function ($http, $cookies) {
            return function (username, access_token) {
                $http.get('/v3/externalservice/syncuserrepos/' + username + "?access_token=" + access_token)
            }
        }])

    .service('SyncUserOrgs', ['$http', '$cookies',
        function ($http, $cookies) {
            return function (username, access_token) {
                $http.get('/v3/externalservice/syncuserorgs/' + username + "?access_token=" + access_token)
            }
        }])
    
    

    .service('postUser', ['$http', 
        function ($http) {
            return function ($build, $job) {
                var $data = {}
                var $username = $build.username;
                var $project_name = $build.project_name;
                $data.source_url = $build.source_url;
                $data.source_type = $build.source_type;
                if ($build.branch) {
                    $data.branch = $build.branch;
                }
                if ($build.commit) {
                    $data.commit = $build.commit;
                }
                if ($build.forced_distro) {
                    $data.forced_distro = $build.forced_distro
                }
                return $http.post('/v3/users/' + $username + '/' + $project_name + '/build', $data)
                    .error(function () {
                        throw new Error('postUser: POST Request failed');
                    });
            };
        }])


