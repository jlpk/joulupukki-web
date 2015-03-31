"use strict";

angular.module("adagios.table.actionbar", []).factory("actionbarFilters", function() {
    var actionbarFilters = {
        activeFilter: {},
        possibleFilters: [ {
            text: "All",
            name: "all"
        }, {
            text: "All OK",
            name: "all_ok"
        }, {
            text: "All Acknowledged",
            name: "all_acknowledged"
        }, {
            text: "All in Downtime",
            name: "all_downtime"
        } ]
    };
    return actionbarFilters;
}).controller("TableActionbarCtrl", [ "$scope", "actionbarFilters", function($scope, actionbarFilters) {
    $scope.actionbarFilters = actionbarFilters, $scope.actionbarFilters.activeFilter = $scope.actionbarFilters.possibleFilters[0], 
    $scope.activateFilter = function(item) {
        $scope.actionbarFilters.activeFilter = $scope.actionbarFilters.possibleFilters[item];
    };
} ]).filter("actionbarSelectFilter", function() {
    return function(items, activeFilter) {
        var i, out = [];
        if (activeFilter) return items;
        if (items) if ("all" === activeFilter.name) for (i = 0; i < items.length; i += 1) out.push(items[i]); else if ("all_ok" === activeFilter.name) for (i = 0; i < items.length; i += 1) 0 === items[i].state && out.push(items[i]); else "all_acknowledged" === activeFilter.name ? console.log("This filter is not yet implemented") : "all_downtime" === activeFilter.name && console.log("This filter is not yet implemented");
        return out;
    };
}).directive("adgTableActionbar", function() {
    return {
        restrict: "E",
        templateUrl: "components/table/actionbar/actionbar.html"
    };
});