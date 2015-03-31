'use strict';

angular.module('joulupukki.topbar', ['joulupukki.live'])
/*
    .controller('TopBarCtrl', ['$scope', 'getProblems', function ($scope, getProblems) {
        $scope.notifications = getProblems;
    }])
*/
    .controller('TopBarCtrl', ['$scope', function ($scope, getProblems) {
    }])

    .directive('jlpkTopbar', function () {
        return {
            restrict: 'E',
            templateUrl: 'components/topbar/topbar.html'
        };
    });
