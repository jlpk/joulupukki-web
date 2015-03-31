"use strict";

angular.module("adagios.table.cell_hosts_host", [ "adagios.table" ]).controller("CellHostsHostCtrl", [ "$scope", function($scope) {
    $scope.state = 0 === $scope.entry.state ? "state--ok" : 1 === $scope.entry.state ? "state--warning" : "" === $scope.entry.state ? "" : "state--error";
} ]).run([ "tableConfig", function(tableConfig) {
    tableConfig.cellToFieldsMap.hosts_host = [ "name", "state" ];
} ]);