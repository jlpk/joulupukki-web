"use strict";

angular.module("adagios.table.cell_host_status", [ "adagios.table" ]).controller("CellHostStatusCtrl", [ "$scope", function($scope) {
    $scope.entry.host_status = "", $scope.alert_level = "", 0 === $scope.entry.last_check ? ($scope.alert_level = "alert alert-info", 
    $scope.entry.host_status = "Pending") : 0 === $scope.entry.state ? ($scope.alert_level = "alert alert-success", 
    $scope.entry.host_status = "Host UP") : ($scope.alert_level = "alert alert-danger", 
    $scope.entry.host_status = 0 !== $scope.entry.childs.length ? "Network outage" : "Host down");
} ]).run([ "tableConfig", function(tableConfig) {
    tableConfig.cellToFieldsMap.host_status = [ "state", "last_check", "childs" ];
} ]);