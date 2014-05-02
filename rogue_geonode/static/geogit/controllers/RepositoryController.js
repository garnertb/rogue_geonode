GeoGit.geogitApp.controller("GeogitRepositoryController", function($scope, $http, $window){
    $scope.test = 'testsdf';


    $scope.toggleDivs = function(){
		$('.geogit-commit-wrapper').toggle();
        $window.alert('here');
	};

});
