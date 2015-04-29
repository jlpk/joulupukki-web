'use strict';

angular.module('joulupukki.history', ['joulupukki.filters',
                                      'joulupukki.live'
                                      ])


    .controller('MainHistoryCtrl', [
        function () {
        }])

    .directive('jlpkHistory', ['$http', '$compile', function ($http, $compile) {
        return {
            restrict: 'E',
            templateUrl: "components/main/history/history.html"
        };
    }])


