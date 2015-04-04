"use strict";

angular.module("joulupukki.main.buildjobs", [ "joulupukki.filters", "joulupukki.live" ]).controller("MainOutputCtrl", [ "$scope", "$route", "$routeParams", "getBuildOutput", function($scope, $route, $routeParams, getBuildOutput) {
    var $username = $routeParams.user, $project_name = $routeParams.project, $build_id = $routeParams.build, $controller_name = ($routeParams.job, 
    $route.current.controllerAs);
    $controller_name || ($controller_name = "project"), $scope.selected_tab = $controller_name, 
    getBuildOutput($username, $project_name, $build_id).success(function(data) {
        $scope.output = "null" != data ? data : !1;
    });
} ]).directive("jlpkMainOutput", [ "$http", "$compile", function() {
    return {
        restrict: "E",
        templateUrl: "components/main/output/output.html"
    };
} ]);