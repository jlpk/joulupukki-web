"use strict";

angular.module("joulupukki.live").service("getJob", [ "$http", function($http) {
    return function($username, $project_name, $build_id, $job_id) {
        return $http.get("/v3/users/" + $username + "/" + $project_name + "/builds/" + $build_id + "/jobs/" + $job_id).error(function() {
            throw new Error("getBuild: GET Request failed");
        });
    };
} ]).service("getJobLog", [ "$http", function($http) {
    return function($username, $project_name, $build_id, $job_id) {
        return $http.get("/v3/users/" + $username + "/" + $project_name + "/builds/" + $build_id + "/jobs/" + $job_id + "/log?html=1").error(function() {
            throw new Error("getBuild: GET Request failed");
        });
    };
} ]);