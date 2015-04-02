"use strict";

angular.module("joulupukki.main", [ "joulupukki.live" ]).controller("MainCtrl", [ "$scope", "$rootScope", "$route", "$routeParams", "$interval", "getProject", "getBuild", "getJob", "getJobLog", "getBuildOutput", function($scope, $rootScope, $route, $routeParams, $interval, getProject, getBuild, getJob, getJobLog, getBuildOutput) {
    var $username = $routeParams.user, $project_name = $routeParams.project, $build_id = $routeParams.build, $job_id = $routeParams.job, $controller_name = $route.current.controllerAs;
    $controller_name || ($controller_name = "project"), $scope.selected_tab = $controller_name, 
    $scope.$on("update_main", function() {
        $username && $project_name && ("history" == $controller_name ? getProject($username, $project_name, !1).success(function(data) {
            $scope.selected_project = data;
        }) : getProject($username, $project_name).success(function(data) {
            $scope.selected_project = data, $build_id || ($scope.build = data.builds[0]);
        }), $build_id && getBuild($username, $project_name, $build_id).success(function(data) {
            $scope.build = data;
        }), $job_id && (getJob($username, $project_name, $build_id, $job_id).success(function(data) {
            $scope.job = data;
        }), getJobLog($username, $project_name, $build_id, $job_id).success(function(data) {
            $scope.joblog = data;
        })), "output" == $controller_name && getBuildOutput($username, $project_name, $build_id).success(function(data) {
            $scope.output = "null" != data ? data : !1;
        }));
    }), $username && $project_name ? $scope.$emit("update_main") : $rootScope.$watch("latest_project", function() {
        $rootScope.latest_project && ($username = $rootScope.latest_project.username, $project_name = $rootScope.latest_project.name, 
        $scope.$emit("update_main"));
    });
} ]).directive("jlpkMain", [ "$http", "$compile", function() {
    return {
        restrict: "E",
        templateUrl: "components/main/main.html"
    };
} ]);