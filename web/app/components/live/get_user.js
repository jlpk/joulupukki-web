'use strict';

angular.module('joulupukki.live')

 
    .service('getUser', ['$http', 
        function ($http) {
            return function ($username, $project_name, $build_id) {
                return $http.get('/v3/users/' + $username + '/' + $project_name + '/builds/' + $build_id)
                    .error(function () {
                        throw new Error('getBuild: GET Request failed');
                    });
            };
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
                        throw new Error('getBuild: GET Request failed');
                    });
            };
        }])


