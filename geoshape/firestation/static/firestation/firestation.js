'use strict';

(function() {
  angular.module('fireStation', [])

  .config(function($interpolateProvider, $httpProvider) {
    $interpolateProvider.startSymbol('{[');
    $interpolateProvider.endSymbol(']}');
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';

  })

  .controller('jurisdictionController', function($scope) {
          var options = {
              boxZoom: true,
              zoom: 15,
              zoomControl: true,
              attributionControl: false,
              scrollWheelZoom: false,
              doubleClickZoom: false,
              fullscreenControl: false
          };
          $scope.map = L.map('map', options);
          if (config.geom != null) {
           var countyBoundary = L.geoJson(config.geom, {
                                  style: function (feature) {
                                      return {color: '#0000ff'};
                                  }
                              }).addTo($scope.map);
          $scope.map.fitBounds(countyBoundary.getBounds());
          } else {
              L.marker(config.centroid).addTo($scope.map);
              $scope.map.setView(config.centroid, 13);
          }

          L.tileLayer('https://{s}.tiles.mapbox.com/v3/examples.map-i87786ca/{z}/{x}/{y}.png',
              {'attribution': '© Mapbox'}).addTo($scope.map);
      })

  .controller('fireStationController', function($scope, $window, $http) {

          var thisFirestation = '/api/v1/firestations/' + config.id + '/';
          var options = {
              boxZoom: true,
              zoom: 15,
              zoomControl: true,
              attributionControl: false,
              scrollWheelZoom: false,
              doubleClickZoom: false,
              fullscreenControl: false
          };

          $scope.choices = ['Engine', 'Ladder/Truck/Aerial', 'Quint', 'Ambulance/ALS', 'Ambulance/BLS', 'Heavy Rescue',
              'Boat', 'Hazmat', 'Chief', 'Other'];

          $scope.forms = [];
          $scope.message = {};

          var getUrl = '/api/v1/staffing/?firestation=' + config.id + '&format=json';
          $http.get(getUrl).success(function(data) {
              for (var iForm = 0; iForm < data.meta.total_count; iForm++) {
                  data.objects[iForm].name = data.objects[iForm].apparatus + data.objects[iForm].id;
              }
              $scope.forms = data.objects;
          });

          $scope.map = L.map('map', options).setView(config.centroid, 15);
          L.marker(config.centroid).addTo($scope.map);

          L.tileLayer('https://{s}.tiles.mapbox.com/v3/examples.map-i87786ca/{z}/{x}/{y}.png',
              {'attribution': '© Mapbox'}).addTo($scope.map);


          $scope.ClearForm = function(form) {
              form.apparatus = 'Engine';
              form.firefighter = 0;
              form.firefighter_emt = 0;
              form.firefighter_paramedic = 0;
              form.ems_emt = 0;
              form.ems_paramedic = 0;
              form.officer = 0;
              form.officer_paramedic = 0;
              form.ems_supervisor = 0;
              form.chief = 0;
          };

          $scope.AddForm = function() {
              var newForm = {'apparatus': 'Engine',
                  'chief_officer': 0,
                  'ems_emt': 0,
                  'ems_paramedic': 0,
                  'ems_supervisor': 0,
                  'firefighter': 0,
                  'firefighter_emt': 0,
                  'firefighter_paramedic': 0,
                  'firestation': thisFirestation,
                  'officer': 0,
                  'officer_paramedic': 0
              };

              var postUrl = '/api/v1/staffing/?format=json';
              $http.post(postUrl, newForm).success(function(data, status, headers) {
                  $http.get(headers('Location') + '?format=json').success(function(data) {
                      data.name = data.apparatus + data.id;
                      $scope.forms.push(data);
                      $scope.showLastTab();
                  }).error(function(data, status) {
                      $scope.showMessage('There was a problem adding the new record.', 'error');
                  });
              }).error(function(data, status) {
                  $scope.showMessage('There was a problem adding the new record.', 'error');
              });
          };

          $scope.UpdateForm = function(form) {
              var updateUrl = '/api/v1/staffing/' + form.id + '/?format=json';
              $http.put(updateUrl, form).success(function(data) {
                  form.name = form.apparatus + form.id;
                  $scope.showMessage(form.apparatus + ' staffing has been updated.');
              }).error(function(data, status) {
                  $scope.showMessage('There was a problem updating the ' + form.apparatus + ' staffing.', 'error');
              });
          };

          $scope.showLastTab = function() {
              $('.apparatus-tabs li a:last').tab('show');
          };

          $scope.DeleteForm = function(form) {

              $http.delete('/api/v1/staffing/' + form.id + '/?format=json').success(function(data) {
                  $scope.forms.splice($scope.forms.indexOf(form), 1);
                  $scope.showMessage(form.apparatus + ' staffing has been deleted.');
                  $scope.showLastTab();
              }).error(function(data, status) {
                  $scope.showMessage('There was an error deleting the staffing for ' + form.apparatus + '.', 'error');
              });
          };

          $scope.ClearForm = function(form) {
              form.apparatus = 'Engine';
              form.firefighter = 0;
              form.firefighter_emt = 0;
              form.firefighter_paramedic = 0;
              form.ems_emt = 0;
              form.ems_paramedic = 0;
              form.officer = 0;
              form.officer_paramedic = 0;
              form.ems_supervisor = 0;
              form.chief = 0;
          };

          $scope.showMessage = function(message, message_type) {
              /*
               message_type should be one of the bootstrap alert classes (error, success, info, warning, etc.)
               */
              var message_class = message_type || 'success';

              $scope.message = {message: message, message_class: message_class};
              $('#response-capability-message').show();

              setTimeout(function() {
                  $('#response-capability-message').fadeOut('slow');
                  $scope.message = {};
              }, 4000);
          };
      });
})();
