"use strict";

angular.module("joulupukki.main.build", [ "joulupukki.filters", "joulupukki.live", "joulupukki.main.build.job", "joulupukki.main.build.jobs", "joulupukki.main.build.output" ]).controller("MainBuildCtrl", [ function() {} ]).directive("jlpkMainBuild", [ "$http", "$compile", function() {
    return {
        restrict: "E",
        templateUrl: "components/main/build/build.html"
    };
} ]);