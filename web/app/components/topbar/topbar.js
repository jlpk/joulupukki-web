'use strict';

angular.module('joulupukki.topbar', ['joulupukki.live',
                                     'joulupukki.github'
                                    ])


    .controller('TopBarCtrl', ['$scope', '$cookies', '$rootScope', 'getCurrentUserInfo',
        function ($scope, $cookies, $rootScope, getCurrentUserInfo) {

            $rootScope.$on('token_changed', function(){
                //console.log('token_changed')
                var $getuserinfo = getCurrentUserInfo()
                if($getuserinfo){
                    $getuserinfo.success(function(data) {
                        if (data){
                           $scope.username = data.login
                           $cookies.username = data.login
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
