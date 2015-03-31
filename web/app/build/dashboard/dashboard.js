"use strict";

angular.module("adagios.view.dashboard", [ "ngRoute", "adagios.tactical", "adagios.table", "joulupukki.live" ]).value("dashboardConfig", {}).config([ "$routeProvider", function($routeProvider) {
    $routeProvider.when("/dashboard", {
        templateUrl: "dashboard/dashboard.html",
        controller: "DashboardCtrl"
    });
} ]).controller("DashboardCtrl", [ "$scope", "$routeParams", "dashboardConfig", "getServices", "tableConfig", "TableConfigObj", "TacticalConfigObj", function($scope, $routeParams, dashboardConfig, getServices, tableConfig, TableConfigObj, TacticalConfigObj) {
    var component, config, viewName, fields = [ "state" ], filters = {
        isnot: {
            state: [ "0" ]
        }
    }, apiName = "hosts", components = [], i = 0;
    if (tableConfig.index = 0, !$routeParams.view) throw new Error("ERROR : 'view' GET parameter must be the custom view name");
    for (viewName = $routeParams.view, $scope.dashboardTitle = dashboardConfig[viewName].title, 
    $scope.dashboardTemplate = dashboardConfig[viewName].template, $scope.dashboardRefreshInterval = dashboardConfig[viewName].refreshInterval, 
    $scope.dashboardTactical = [], $scope.dashboardTables = [], components = dashboardConfig[viewName].components, 
    i = 0; i < components.length; i += 1) component = components[i], config = component.config, 
    "table" === component.type ? $scope.dashboardTables.push(new TableConfigObj(config)) : "tactical" === component.type && $scope.dashboardTactical.push(new TacticalConfigObj(config));
    getServices(fields, filters, apiName).success(function(data) {
        $scope.nbHostProblems = data.length;
    });
} ]).run([ "readConfig", "dashboardConfig", function(readConfig, dashboardConfig) {
    var viewsConfig = readConfig.data;
    angular.forEach(viewsConfig, function(config, view) {
        "dashboard" === config.template && (dashboardConfig[view] = config);
    });
} ]);