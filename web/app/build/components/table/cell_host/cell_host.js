"use strict";

angular.module("adagios.table.cell_host", [ "adagios.table" ]).controller("CellHostCtrl", [ "$scope", function($scope) {
    $scope.cell_name = "host", $scope.state = 0 === $scope.entry.host_state ? "state--ok" : 1 === $scope.entry.host_state ? "state--warning" : "" === $scope.entry.host_state ? "" : "state--error";
} ]).run([ "tableConfig", function(tableConfig) {
    tableConfig.cellToFieldsMap.host = [ "host_state", "host_name" ], tableConfig.cellWrappableField.host = "host_name";
} ]);