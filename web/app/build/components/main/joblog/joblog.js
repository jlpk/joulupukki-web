"use strict";

angular.module("joulupukki.main.joblog", [ "joulupukki.filters", "joulupukki.live" ]).controller("MainJobLogCtrl", [ "$scope", "$route", "$routeParams", "getBuildOutput", function($scope, $route, $routeParams, getBuildOutput) {
    var $username = $routeParams.user, $project_name = $routeParams.project, $build_id = $routeParams.build, $controller_name = ($routeParams.job, 
    $route.current.controllerAs);
    $controller_name || ($controller_name = "project"), $scope.selected_tab = $controller_name, 
    getBuildOutput($username, $project_name, $build_id).success(function(data) {
        $scope.output = "null" != data ? data : !1;
    });
} ]).directive("jlpkMainJobLog", [ "$http", "$compile", function() {
    return {
        restrict: "E",
        templateUrl: "components/main/job/joblog/joglog.html"
    };
} ]);