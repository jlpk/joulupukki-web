"use strict";

angular.module("ngJustGage", []).directive("justGage", [ "$timeout", function($timeout) {
    return {
        restrict: "EA",
        scope: {
            id: "@",
            "class": "@",
            min: "=",
            max: "=",
            title: "@",
            value: "=",
            options: "="
        },
        template: '<div id="{{id}}-justgage" class="{{class}}"></div>',
        link: function(scope) {
            $timeout(function() {
                var options, key, graph;
                if (options = {
                    id: scope.id + "-justgage",
                    min: scope.min,
                    max: scope.max,
                    title: scope.title,
                    value: scope.value
                }, scope.options) for (key in scope.options) scope.options.hasOwnProperty(key) && (options[key] = scope.options[key]);
                graph = new JustGage(options), scope.$watch("max", function(updatedMax) {
                    void 0 !== updatedMax && graph.refresh(scope.value, updatedMax);
                }, !0), scope.$watch("value", function(updatedValue) {
                    void 0 !== updatedValue && graph.refresh(updatedValue);
                }, !0);
            });
        }
    };
} ]);