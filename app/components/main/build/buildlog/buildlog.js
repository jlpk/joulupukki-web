'use strict';

angular.module('joulupukki.main.build.log', [ 'joulupukki.filters', 
                                    'joulupukki.live' ])

    .controller('MainBuildLogCtrl', [
        function () {
        }])

    .directive('jlpkMainBuildLog', ['$http', '$compile', function ($http, $compile) {
        return {
            restrict: 'E',
            templateUrl: "components/main/build/buildlog/buildlog.html"
        };
    }])


