'use strict';

angular.module('joulupukki.main.build.jobs', [])

    .controller('MainBuildJobsCtrl', [ function () {
    }])

    .directive('jlpkMainBuildJobs', ['$http', '$compile', function ($http, $compile) {
        return {
            restrict: 'E',
            templateUrl: "components/main/build/jobs/jobs.html"
        };
    }])


