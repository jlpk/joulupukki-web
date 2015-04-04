"use strict";

angular.module("joulupukki.main.build.job", [ "joulupukki.live", "joulupukki.main.build.job.log" ]).controller("MainBuildJobCtrl", [ function() {} ]).directive("jlpkMainBuildJob", [ "$http", "$compile", function() {
    return {
        restrict: "E",
        templateUrl: "components/main/build/job/job.html"
    };
} ]);