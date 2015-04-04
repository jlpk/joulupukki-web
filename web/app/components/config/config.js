'use strict';


function JoulupukkiConfig(data) {
    this.data = data;
}

angular.module('joulupukki.config', [])

    .provider('readConfig', function ReadConfigProvider() {

        var data = {};

        this.loadJSON = function (value) {
            data = value;
        };

        this.$get = [function getConfigFactory() {
            return new JoulupukkiConfig(data);
        }];
    });
