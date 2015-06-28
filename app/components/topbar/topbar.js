'use strict';

angular.module('joulupukki.topbar', ['joulupukki.live',
                                     'ngMaterial'
                                    ])


    .controller('TopBarCtrl', ['$scope', '$cookies', '$rootScope', 'getUser',
        function ($scope, $cookies, $rootScope, getUser) {

           $rootScope.$on('token_changed', function(){
                if($cookies.token){
                    getUser($cookies.username, $cookies.token).success(function(data) {
                        if (data){
                           $scope.username = data.username
                           $cookies.username = data.username
                        }
                        else {
                           delete $scope.username
                           delete $cookies.username
                        }
                       })
                }
                else {
                    delete $scope.username
                    delete $cookies.username
                }
            })

            if ($cookies.username) {
                $scope.username = $cookies.username
            }
            else {
                $rootScope.$emit('token_changed')
            }

        }])

    .directive('jlpkTopbar', function () {
        return {
            restrict: 'E',
            templateUrl: 'components/topbar/topbar.html'
        };
    });
