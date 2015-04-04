"use strict";

angular.module("joulupukki.main.job", [ "joulupukki.live", "joulupukki.main.job.log" ]).controller("MainJobCtrl", [ "$scope", "$route", "$routeParams", "$sce", "$location", "$anchorScroll", "getJob", "getJobLog", function($scope, $route, $routeParams, $sce, $location, $anchorScroll, getJob) {
    var $username = $routeParams.user, $project_name = $routeParams.project, $build_id = $routeParams.build, $job_id = $routeParams.job, $controller_name = $route.current.controllerAs;
    $controller_name || ($controller_name = "project"), $scope.selected_tab = $controller_name, 
    getJob($username, $project_name, $build_id, $job_id).success(function(data) {
        $scope.job = data;
        var link = document.createElement("link");
        link.type = "image/x-icon", link.rel = "shortcut icon", link.href = "succeeded" == $scope.job.status ? "assets/images/jlpk_logo_succeeded.png" : "failed" == $scope.job.status ? "assets/images/jlpk_logo_failed.png" : "assets/images/jlpk_logo.png", 
        document.getElementsByTagName("head")[0].appendChild(link);
    });
} ]).directive("jlpkMainJob", [ "$http", "$compile", function() {
    return {
        restrict: "E",
        templateUrl: "components/main/job/job.html"
    };
} ]);