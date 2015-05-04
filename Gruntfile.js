'use strict';

module.exports = function (grunt) {

    grunt.initConfig({

        pkg: grunt.file.readJSON('package.json'),

        project: {
            app: ['app'],
            assets: ['<%= project.app %>/assets'],
            css: ['<%= project.assets %>/sass/app.scss'],
            build: ['<%= project.app %>/build/']
        },

        sass: {
            dev: {
                options: {
                    style: 'expanded',
                    compass: false
                },
                files: {
                    '<%= project.assets %>/css/app.css' : '<%= project.css %>'
                }
            }
        },

        watch: {
            sass: {
                files: [
                    '<%= project.assets %>/sass/{,*/}*.{scss,sass}',
                    '<%= project.app %>/{,*/}*/{,*/}*.{scss,sass}'
                ],
                tasks: ['sass:dev']
            },
            uglify: {
                files: [
                    '<%= project.app %>/**/*.js',
                    '<%= project.app %>/**/*_test.js',
                    '!<%= project.app %>/bower_components/**',
                    '!<%= project.build %>/**',
                    '!<%= project.assets %>/**'
                ],
                tasks: ['uglify:dev']
            }
        },

        jslint: { // configure the task

            client: {
                src: [
                    'karma.conf.js',
                    'Gruntfile.js',
                    '<%= project.app %>/app.js',
                    '<%= project.app %>/**/*.js'
                ],
                exclude: [
                    '<%= project.app %>/bower_components/**/*.js',
                    '<%= project.assets %>/**',
                    '<%= project.build %>/**'
                ],
                directives: {
                    node: true,
                    nomen: true,
                    unparam: true,
                    predef: [ // Global variables
                        'document', '$', '$get',
                        'angular', 'inject', 'JustGage',
                        'describe', 'beforeEach', 'it', 'expect',
                        'moment'
                    ]
                },
                options: {
                    edition: 'latest', // specify an edition of jslint or use 'dir/mycustom-jslint.js' for own path
                    junit: 'out/client-junit.xml', // write the output to a JUnit XML
                    log: 'out/client-lint.log',
                    jslintXml: 'out/client-jslint.xml',
                    errorsOnly: true, // only display errors
                    failOnError: false, // defaults to true
                    checkstyle: 'out/client-checkstyle.xml' // write a checkstyle-XML
                }
            }
        },

        // Minify and concatenate joulupukki in one file
        uglify: {
            compress: {
                files: [{
                    '<%= project.build %>/js/joulupukki.min.js' : [
                        '<%= project.app %>/app.js',
                        '<%= project.app %>/components/config/config.js',
                        '<%= project.app %>/components/github/github.js',
                        '<%= project.app %>/components/github/auth.js',
                        '<%= project.app %>/components/live/live.js',
                        '<%= project.app %>/components/live/get_project.js',
                        '<%= project.app %>/components/live/get_build.js',
                        '<%= project.app %>/components/live/get_job.js',
                        '<%= project.app %>/components/live/get_user.js',
                        '<%= project.app %>/components/filters/filters.js',
                        '<%= project.app %>/components/sidebar/sidebar.js',
                        '<%= project.app %>/components/topbar/topbar.js',
                        '<%= project.app %>/components/main/main.js',
                        '<%= project.app %>/components/main/history/history.js',
                        '<%= project.app %>/components/main/build/build.js',
                        '<%= project.app %>/components/main/build/jobs/jobs.js',
                        '<%= project.app %>/components/main/build/output/output.js',
                        '<%= project.app %>/components/main/build/buildlog/buildlog.js',
                        '<%= project.app %>/components/main/build/job/job.js',
                        '<%= project.app %>/components/main/build/job/joblog/joblog.js',
                        '<%= project.app %>/repositories/repositories.js',
                        '<%= project.app %>/404/404.js',
                        '<%= project.app %>/login/login.js',
                        '<%= project.app %>/account/account.js'
                    ]
                }],
                options: {
                    mangle: true
                }
            },
            dev: {
                files: [
                    {
                        '<%= project.build %>/app.js': '<%= project.app %>/app.js',
                        '<%= project.build %>/components/config/config.js': '<%= project.app %>/components/config/config.js',
                        '<%= project.build %>/components/github/github.js': '<%= project.app %>/components/github/github.js',
                        '<%= project.build %>/components/github/auth.js': '<%= project.app %>/components/github/auth.js',
                        '<%= project.build %>/components/live/live.js': '<%= project.app %>/components/live/live.js',
                        '<%= project.build %>/components/live/get_project.js': '<%= project.app %>/components/live/get_project.js',
                        '<%= project.build %>/components/live/get_build.js': '<%= project.app %>/components/live/get_build.js',
                        '<%= project.build %>/components/live/get_job.js': '<%= project.app %>/components/live/get_job.js',
                        '<%= project.build %>/components/live/get_user.js': '<%= project.app %>/components/live/get_user.js',
                        '<%= project.build %>/components/filters/filters.js': '<%= project.app %>/components/filters/filters.js',
                        '<%= project.build %>/components/sidebar/sidebar.js': '<%= project.app %>/components/sidebar/sidebar.js',
                        '<%= project.build %>/components/topbar/topbar.js': '<%= project.app %>/components/topbar/topbar.js',
                        '<%= project.build %>/components/main/main.js': '<%= project.app %>/components/main/main.js',
                        '<%= project.build %>/components/main/history/history.js': '<%= project.app %>/components/main/history/history.js',
                        '<%= project.build %>/components/main/build/build.js': '<%= project.app %>/components/main/build/build.js',
                        '<%= project.build %>/components/main/build/jobs/jobs.js': '<%= project.app %>/components/main/build/jobs/jobs.js',
                        '<%= project.build %>/components/main/build/output/output.js': '<%= project.app %>/components/main/build/output/output.js',
                        '<%= project.build %>/components/main/build/buildlog/buildlog.js': '<%= project.app %>/components/main/build/buildlog/buildlog.js',
                        '<%= project.build %>/components/main/build/job/job.js': '<%= project.app %>/components/main/build/job/job.js',
                        '<%= project.build %>/components/main/build/job/joblog/joblog.js': '<%= project.app %>/components/main/build/job/joblog/joblog.js',
                        '<%= project.build %>/repositories/repositories.js': '<%= project.app %>/repositories/repositories.js',
                        '<%= project.build %>/404/404.js': '<%= project.app %>/404/404.js',
                        '<%= project.build %>/login/login.js': '<%= project.app %>/login/login.js',
                        '<%= project.build %>/account/account.js': '<%= project.app %>/account/account.js'
                    },
                    {
                        '<%= project.build %>/js/joulupukki.min.js' : [
                            '<%= project.build %>/app.js',
                            '<%= project.build %>/components/config/config.js',
                            '<%= project.build %>/components/github/github.js',
                            '<%= project.build %>/components/github/auth.js',
                            '<%= project.build %>/components/live/live.js',
                            '<%= project.build %>/components/live/get_project.js',
                            '<%= project.build %>/components/live/get_build.js',
                            '<%= project.build %>/components/live/get_job.js',
                            '<%= project.build %>/components/live/get_user.js',
                            '<%= project.build %>/components/filters/filters.js',
                            '<%= project.build %>/components/sidebar/sidebar.js',
                            '<%= project.build %>/components/topbar/topbar.js',
                            '<%= project.build %>/components/main/main.js',
                            '<%= project.build %>/components/main/history/history.js',
                            '<%= project.build %>/components/main/build/build.js',
                            '<%= project.build %>/components/main/build/jobs/jobs.js',
                            '<%= project.build %>/components/main/build/output/output.js',
                            '<%= project.build %>/components/main/build/buildlog/buildlog.js',
                            '<%= project.build %>/components/main/build/job/job.js',
                            '<%= project.build %>/components/main/build/job/joblog/joblog.js',
                            '<%= project.build %>/repositories/repositories.js',
                            '<%= project.build %>/404/404.js',
                            '<%= project.build %>/login/login.js',
                            '<%= project.build %>/account/account.js'
                        ]
                    }
                ],
                options: {
                    mangle: false,
                    beautify: true
                }
            }
        }
    });

    grunt.loadNpmTasks('grunt-contrib-sass');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-jslint');

    grunt.registerTask('default', ['watch', 'jslint', 'uglify']);
};
