'use strict';

angular.module('joulupukki.topbar', ['joulupukki.live',
                                     'joulupukki.github'
                                    ])


    .controller('TopBarCtrl', ['$scope', '$routeParams', 'getUserInfo',
                function ($scope, $routeParams, getUserInfo) {
            var username = $routeParams.user;
            var username = 'titilambert'
            getUserInfo(username)
                .success(function(data) {
                        console.log(data)
                        $scope.username = data.login
                    })
            }])

    .directive('jlpkTopbar', function () {
        return {
            restrict: 'E',
            templateUrl: 'components/topbar/topbar.html'
        };
    });
