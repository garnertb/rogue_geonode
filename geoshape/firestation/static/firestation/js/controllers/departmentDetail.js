'use strict';

(function() {
    angular.module('fireStation.departmentDetailController', [])

    .controller('jurisdictionController', function($scope, $http, FireStation, map) {
          var departmentMap = map.initMap('map');
          var showStations = true;
          var stationIcon = L.FireCARESMarkers.firestationmarker();
          var headquartersIcon = L.FireCARESMarkers.headquartersmarker();
          var fitBoundsOptions = {};
          $scope.stations = [];

          function onResize() {
              var height = $(window).height();
              $('.content-height').css('height', (height - $('.navbar').height()).toString() + 'px');
            }

            onResize();
            $(window).resize(onResize);

          if (showStations) {
              FireStation.query({department: config.id}).$promise.then(function(data) {
                 $scope.stations = data.objects;

                  var stationMarkers = [];
                  for (var i = 0; i < $scope.stations.length; i++) {
                      var station = $scope.stations[i];
                      var marker = L.marker(station.geom.coordinates.reverse(), {icon: stationIcon});
                      marker.bindPopup('<b>' + station.name + '</b><br/>' + station.address + ', ' + station.city + ' ' +
                          station.state);
                      stationMarkers.push(marker);
                  }

                  var stationLayer = L.featureGroup(stationMarkers);
                  stationLayer.addTo(departmentMap);

                  if (config.geom === null) {
                    departmentMap.fitBounds(stationLayer.getBounds(), fitBoundsOptions);
                  }
              });
          }

          if (config.centroid != null) {
           L.marker(config.centroid, {icon: headquartersIcon}).addTo(departmentMap);
          };

          if (config.geom != null) {
           var countyBoundary = L.geoJson(config.geom, {
                                  style: function (feature) {
                                      return {color: '#0074D9', fillOpacity: .05, opacity:.8, weight:2};
                                  }
                              }).addTo(departmentMap);
            departmentMap.fitBounds(countyBoundary.getBounds(), fitBoundsOptions);
          } else {
              departmentMap.setView(config.centroid, 13);
          }
      })
})();
