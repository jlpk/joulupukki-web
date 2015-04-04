"use strict";

angular.module("joulupukki.main.job.log", [ "joulupukki.live" ]).controller("MainJobLogCtrl", [ "$scope", "$route", "$routeParams", "$sce", "$location", "$anchorScroll", "getJob", "getJobLog", function($scope, $route, $routeParams, $sce, $location, $anchorScroll, getJob, getJobLog) {
    var $username = $routeParams.user, $project_name = $routeParams.project, $build_id = $routeParams.build, $job_id = $routeParams.job;
    getJobLog($username, $project_name, $build_id, $job_id).success(function(data) {
        $scope.joblog = $sce.trustAsHtml(data), $scope.gotoTop = function() {
            var old = $location.hash();
            $location.hash(""), $anchorScroll(), $location.hash(old);
        }, $scope.gotoBot = function() {
            var old = $location.hash();
            $location.hash("logbottom"), $anchorScroll(), $location.hash(old);
        }, angular.element(document).bind("scroll", function() {
            var $pre_log = angular.element(document.querySelector("#prelog")), logheight = $pre_log.prop("offsetHeight"), winheight = window.innerHeight, yoffset = window.pageYOffset, $top_btn = angular.element(document.querySelector("#to-top")), $bot_btn = angular.element(document.querySelector("#to-bot"));
            if (yoffset > winheight - 475) {
                var new_height = logheight - winheight - yoffset + 475;
                15 > new_height && (new_height = 15), $top_btn.css("bottom", new_height + "px"), 
                $top_btn.css("visibility", "visible");
                var new_height = yoffset - 460;
                $bot_btn.css("top", new_height + "px"), $bot_btn.css("visibility", "visible");
            } else $bot_btn.css("visibility", "hidden");
        });
    });
} ]).directive("jlpkMainJobLog", [ "$http", "$compile", function() {
    return {
        restrict: "E",
        templateUrl: "components/main/job/joblog/joblog.html"
    };
} ]);