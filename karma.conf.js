'use strict';

module.exports = function (config) {
    config.set({

        basePath : './',

        files : [
            'app/bower_components/jquery/dist/jquery.min.js',
            'app/bower_components/angular/angular.js',
            'app/bower_components/angular-route/angular-route.js',
            'app/bower_components/angular-mocks/angular-mocks.js',
            'app/bower_components/angular-mocks/angular-cookies.js',
            'app/components/live/live.js',
            'app/components/**/*.js',
            'app/topbar/**/*.js',
            'app/sidebar/**/*.js',
            'app/tactical/**/*.js',
            'app/table/**/*.js'
        ],

        autoWatch : true,

        frameworks: ['jasmine'],

        browsers : ['Chrome'],

        plugins : [
            'karma-chrome-launcher',
            'karma-firefox-launcher',
            'karma-jasmine',
            'karma-junit-reporter'
        ],

        junitReporter : {
            outputFile: 'test_out/unit.xml',
            suite: 'unit'
        }

    });
};
