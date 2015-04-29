'use strict';

angular.module('joulupukki.main.build.output', ['joulupukki.filters',
                                   'joulupukki.live',
                                ])

    .controller('MainBuildOutputCtrl', [
        function () {
        }])

    .directive('jlpkMainBuildOutput', ['$http', '$compile', function ($http, $compile) {
        return {
            restrict: 'E',
            templateUrl: "components/main/build/output/output.html"
        };
    }])


