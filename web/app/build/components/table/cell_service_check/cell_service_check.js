"use strict";

angular.module("adagios.table.cell_service_check", [ "adagios.table" ]).controller("CellServiceCheckCtrl", [ "$scope", function($scope) {
    $scope.state = 0 === $scope.entry.state ? "state--ok" : 1 === $scope.entry ? "state--warning" : "state--error";
} ]).run([ "tableConfig", function(tableConfig) {
    tableConfig.cellToFieldsMap.service_check = [ "state", "description", "plugin_output" ];
} ]);