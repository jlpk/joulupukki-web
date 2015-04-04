"use strict";

angular.module("joulupukki.main", [ "joulupukki.live" ]).controller("MainCtrl", [ "$scope", "$rootScope", "$route", "$routeParams", "$sce", "$location", "$anchorScroll", "$interval", "getProject", "getBuild", "getJob", "getJobLog", "getBuildOutput", "postBuild", function($scope, $rootScope, $route, $routeParams, $sce, $location, $anchorScroll, $interval, getProject, getBuild, getJob, getJobLog, getBuildOutput, postBuild) {
    var $username = $routeParams.user, $project_name = $routeParams.project, $build_id = $routeParams.build, $job_id = $routeParams.job, $controller_name = $route.current.controllerAs;
    $controller_name || ($controller_name = "project"), $scope.selected_tab = $controller_name, 
    $scope.restart = function() {
        postBuild($scope.build).success(function() {});
    }, $scope.$on("update_main", function() {
        $username && $project_name && ("history" == $controller_name ? getProject($username, $project_name, !1).success(function(data) {
            $scope.selected_project = data;
        }) : getProject($username, $project_name).success(function(data) {
            if ($scope.selected_project = data, !$build_id) {
                $scope.build = data.builds[0];
                var link = document.createElement("link");
                link.type = "image/x-icon", link.rel = "shortcut icon", link.href = "succeeded" == $scope.build.status ? "assets/images/jlpk_logo_succeeded.png" : "failed" == $scope.build.status ? "assets/images/jlpk_logo_failed.png" : "assets/images/jlpk_logo.png", 
                document.getElementsByTagName("head")[0].appendChild(link);
            }
        }), $build_id && getBuild($username, $project_name, $build_id).success(function(data) {
            $scope.build = data;
            var link = document.createElement("link");
            link.type = "image/x-icon", link.rel = "shortcut icon", link.href = "succeeded" == $scope.build.status ? "assets/images/jlpk_logo_succeeded.png" : "failed" == $scope.build.status ? "assets/images/jlpk_logo_failed.png" : "assets/images/jlpk_logo.png", 
            document.getElementsByTagName("head")[0].appendChild(link);
        }), $job_id && (getJob($username, $project_name, $build_id, $job_id).success(function(data) {
            $scope.job = data;
            var link = document.createElement("link");
            link.type = "image/x-icon", link.rel = "shortcut icon", link.href = "succeeded" == $scope.job.status ? "assets/images/jlpk_logo_succeeded.png" : "failed" == $scope.job.status ? "assets/images/jlpk_logo_failed.png" : "assets/images/jlpk_logo.png", 
            console.log("DDD"), document.getElementsByTagName("head")[0].appendChild(link);
        }), getJobLog($username, $project_name, $build_id, $job_id).success(function(data) {
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
        })), "output" == $controller_name && getBuildOutput($username, $project_name, $build_id).success(function(data) {
            $scope.output = "null" != data ? data : !1;
        }));
    }), $username && $project_name ? $scope.$emit("update_main") : $rootScope.$watch("latest_project", function() {
        $rootScope.latest_project && ($username = $rootScope.latest_project.username, $scope.username = $username, 
        $project_name = $rootScope.latest_project.name, $scope.project_name = $project_name, 
        $scope.$emit("update_main"));
    });
} ]).directive("jlpkMain", [ "$http", "$compile", function() {
    return {
        restrict: "E",
        templateUrl: "components/main/main.html"
    };
} ]);