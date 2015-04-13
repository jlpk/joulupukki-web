'use strict';

angular.module('joulupukki.main', ['joulupukki.filters',
                                   'joulupukki.live',
                                   'joulupukki.main.build',
                                   'joulupukki.history'
                                ])



    .controller('MainCtrl', ['$scope', '$rootScope', '$route', '$routeParams', '$sce',
                             '$location', '$anchorScroll',
                             '$interval', 'getProject', 'getBuild', 'getJob', 'getJobLog',
                             'getBuildOutput', 'postBuild',
        function ($scope, $rootScope, $route, $routeParams, $sce, $location, $anchorScroll, $interval, getProject, getBuild, getJob, getJobLog, getBuildOutput, postBuild) {
            var $username = $routeParams.user;
            var $project_name = $routeParams.project;

            var $build_id = $routeParams.build;
            var $job_id = $routeParams.job;
            var $controller_name = $route.current.controllerAs;
            if (! $controller_name){
                $controller_name = 'project';
            }
            $scope.selected_tab = $controller_name;

            $scope.restart = function() {
                postBuild($scope.build)
                   .success(function (data) {
                   });
            };
            
            // TODO split this in each controller
            $scope.$on('update_main', function() {
                if ( $username && $project_name ){
                    // history
                    if ( $controller_name == 'history') {
                        getProject($username, $project_name, false)
                            .success(function (data) {
                                $scope.selected_project = data;
                            });
                    } else {
                        // not history => project info
                        getProject($username, $project_name)
                            .success(function (data) {
                                $scope.selected_project = data;
                                if ( ! $build_id ) {
                                    $scope.build = data.builds[0];
                                    // set favicon
                                    var link = document.createElement('link');
                                    link.type = 'image/x-icon';
                                    link.rel = 'shortcut icon';
                                    if ($scope.build.status == 'succeeded') {
                                        link.href = 'assets/images/jlpk_logo_succeeded.png';
                                    } else if ($scope.build.status == 'failed') {
                                        link.href = 'assets/images/jlpk_logo_failed.png';
                                    }
                                    else {
                                        link.href = 'assets/images/jlpk_logo.png';
                                    }
                                    document.getElementsByTagName('head')[0].appendChild(link);
                                }
                            });
                    }
                    if ( $build_id ) {
                      getBuild($username, $project_name, $build_id)
                            .success(function (data) {
                                $scope.build = data;
                                // set favicon
                                var link = document.createElement('link');
                                link.type = 'image/x-icon';
                                link.rel = 'shortcut icon';
                                if ($scope.build.status == 'succeeded') {
                                    link.href = 'assets/images/jlpk_logo_succeeded.png';
                                } else if ($scope.build.status == 'failed') {
                                    link.href = 'assets/images/jlpk_logo_failed.png';
                                }
                                else {
                                    link.href = 'assets/images/jlpk_logo.png';
                                }
                                document.getElementsByTagName('head')[0].appendChild(link);
                            });
                    }
                    // log
                    if ( $job_id ) {
                        getJob($username, $project_name, $build_id, $job_id)
                            .success(function (data) {
                                $scope.job = data;
                                // set favicon
                                var link = document.createElement('link');
                                link.type = 'image/x-icon';
                                link.rel = 'shortcut icon';
                                if ($scope.job.status == 'succeeded') {
                                    link.href = 'assets/images/jlpk_logo_succeeded.png';
                                } else
                                if ($scope.job.status == 'failed') {
                                    link.href = 'assets/images/jlpk_logo_failed.png';
                                } else {
                                    link.href = 'assets/images/jlpk_logo.png';
                                }
                                document.getElementsByTagName('head')[0].appendChild(link);
                            });
                        getJobLog($username, $project_name, $build_id, $job_id)
                            .success(function (data) {
                                $scope.joblog = $sce.trustAsHtml(data);
                                //Set goto functions
                                $scope.gotoTop = function() {
                                    var old = $location.hash();
                                    $location.hash('');
                                    $anchorScroll();
                                    $location.hash(old);
                                };
                                $scope.gotoBot = function() {
                                    var old = $location.hash();
                                    $location.hash('logbottom');
                                    $anchorScroll();
                                    $location.hash(old);
                                };

                                // Handle log scrolling 
                                angular.element(document).bind("scroll", function() {
                                    var $pre_log = angular.element(document.querySelector('#prelog'))
                                    var logheight = $pre_log.prop('offsetHeight');
                                    var winheight = window.innerHeight;
                                    var yoffset = window.pageYOffset;
                                    var $top_btn = angular.element(document.querySelector('#to-top'))
                                    var $bot_btn = angular.element(document.querySelector('#to-bot'))
                                    if (yoffset > winheight - 500){
                                        var new_height =  logheight - winheight - yoffset + 500;
                                        if (new_height < 15) {
                                            new_height = 15;
                                        }
                                        $top_btn.css("bottom", new_height +"px");
                                        $top_btn.css("visibility", "visible");
                                        var new_height = yoffset - 460
                                        $bot_btn.css("top", new_height + "px");
                                        $bot_btn.css("visibility", "visible");
                                    }
                                    else {
                                        $bot_btn.css("visibility", "hidden");
                                    }
                                });
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
                        $username = $rootScope.latest_project.username;
                        $scope.username = $username;
                        $project_name = $rootScope.latest_project.name;
                        $scope.project_name = $project_name;
                        $scope.$emit('update_main');
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


