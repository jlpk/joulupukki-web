"use strict";

angular.module("joulupukki.live").service("getBuild", [ "$http", function($http) {
    return function($username, $project_name, $build_id) {
        return $http.get("/v3/users/" + $username + "/" + $project_name + "/builds/" + $build_id).error(function() {
            throw new Error("getBuild: GET Request failed");
        });
    };
} ]).service("getLatestBuilds", [ "$http", function($http) {
    return function() {
        return $http.get("/v3/titilambert").error(function() {
            throw new Error("getLatestBuilds : GET Request failed");
        });
    };
} ]).service("getBuildOutput", [ "$http", function($http) {
    return function($username, $project_name, $build_id) {
        return $http.get("/v3/users/" + $username + "/" + $project_name + "/builds/" + $build_id + "/output").error(function() {
            throw new Error("getBuildOutput : GET Request failed");
        });
    };
} ]).service("postBuild", [ "$http", function($http) {
    return function($build) {
        var $data = {}, $username = $build.username, $project_name = $build.project_name;
        return $data.source_url = $build.source_url, $data.source_type = $build.source_type, 
        $build.branch && ($data.branch = $build.branch), $build.commit && ($data.commit = $build.commit), 
        $build.forced_distro && ($data.forced_distro = $build.forced_distro), $http.post("/v3/users/" + $username + "/" + $project_name + "/build", $data).error(function() {
            throw new Error("getBuild: GET Request failed");
        });
    };
} ]);