'use strict';

angular.module('joulupukki.sidebar', [])

    .controller('SideBarCtrl', ['$scope', '$rootScope', 'getLatestProjects', function ($scope, $rootScope, getLatestProjects) {
        $scope.search_project = '';
        $scope.$watch('search_project', function(){
            getLatestProjects($scope.search_project)
                .success(function (data) {
                    $scope.projects = data;
                    $rootScope.latest_project = data[0];
                });
        });
    }])

    .directive('jlpkSidebar', function () {
        return {
            restrict: 'E',
            templateUrl: "components/sidebar/sidebar.html"
        };
    });
