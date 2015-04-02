'use strict';

angular.module('joulupukki.main', ['joulupukki.live'
                                ])


    .controller('MainCtrl', ['$scope', '$rootScope', '$route', '$routeParams',
                             '$interval', 'getProject', 'getBuild', 'getJob', 'getJobLog',
                             'getBuildOutput',
        function ($scope, $rootScope, $route, $routeParams, $interval, getProject, getBuild, getJob, getJobLog, getBuildOutput) {
            var $username = $routeParams.user;
            var $project_name = $routeParams.project;

            var $build_id = $routeParams.build;
            var $job_id = $routeParams.job;
            var $controller_name = $route.current.controllerAs;
            if (! $controller_name){
                $controller_name = 'project';
            }
            $scope.selected_tab = $controller_name;
            

            $scope.$on('update_main', function() {
                if ( $username && $project_name ){
                    // history
                    if ( $controller_name == 'history') {
                        getProject($username, $project_name, false)
                            .success(function (data) {
                                $scope.selected_project = data;
                            });
                    } else {
                        getProject($username, $project_name)
                            .success(function (data) {
                                $scope.selected_project = data;
                                if ( ! $build_id ) {
                                    $scope.build = data.builds[0];
                                }
                            });
                    }
                    if ( $build_id ) {
                      getBuild($username, $project_name, $build_id)
                            .success(function (data) {
                                $scope.build = data;
                            });
                    }
                    // log
                    if ( $job_id ) {
                      getJob($username, $project_name, $build_id, $job_id)
                            .success(function (data) {
                                $scope.job = data;
                            });
                      getJobLog($username, $project_name, $build_id, $job_id)
                            .success(function (data) {
                                $scope.joblog = data;
                            });
                    }
                    // output
                    if ( $controller_name == 'output' ){
                      getBuildOutput($username, $project_name, $build_id)
                            .success(function (data) {
                                if (data != "null") {
                                    $scope.output = data;
                                }
                                else {
                                    $scope.output = false;
                                }
                            });
                    }
                }
            })
            if ( ! $username || ! $project_name ){
                $rootScope.$watch('latest_project', function(){
                    if ( $rootScope.latest_project ){
                        $username = $rootScope.latest_project.username
                        $project_name = $rootScope.latest_project.name
                        $scope.$emit('update_main')
                    }
                })
            }
            else{
                $scope.$emit('update_main')
            }
        }])

    .directive('jlpkMain', ['$http', '$compile', function ($http, $compile) {
        return {
            restrict: 'E',
            templateUrl: "components/main/main.html"
        };
    }])

