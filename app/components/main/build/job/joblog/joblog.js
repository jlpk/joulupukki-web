'use strict';

angular.module('joulupukki.main.build.job.log', [ 'joulupukki.live' ])

    .controller('MainBuildJobLogCtrl', [
        function () {
        }])

    .directive('jlpkMainBuildJobLog', ['$http', '$compile', function ($http, $compile) {
        return {
            restrict: 'E',
            templateUrl: "components/main/build/job/joblog/joblog.html"
        };
    }])


