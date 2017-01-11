var app = angular.module('campaignMonitor', ['ui.bootstrap']);

app.factory('common',function(){
  var variables = {
    filepath:'/output/intro.html',
    outfile1:'',
    outfile2:'',
    outfile3:'',
    jsonData:''
  };
  var paginate = function($scope){
    $scope.itemsPerPage = $scope.objs.length>5? 5:$scope.objs.length;
    $scope.currentPage = 0;
    $scope.range = function() {
      var rangeSize = $scope.pageCount()>5 ? 5:$scope.pageCount();
      var ret = [];
      var start;
      start = $scope.currentPage;
      if ( start > $scope.pageCount()-rangeSize ) {
        start = $scope.pageCount()-rangeSize;
      }
      for (var i=start; i<start+rangeSize; i++) {
        ret.push(i);
      }
      return ret;
    };
    $scope.prevPage = function() {
      if ($scope.currentPage > 0) {
        $scope.currentPage--;
      }
    };
    $scope.prevPageDisabled = function() {
      return $scope.currentPage === 0 ? "disabled" : "";
    };
    $scope.pageCount = function() {
      pc = Math.ceil($scope.objs.length/$scope.itemsPerPage);
      return pc<1 ? 1:pc;
    };
    $scope.nextPage = function() {
      if ($scope.currentPage < $scope.pageCount()-1) {
        $scope.currentPage++;
      }
    };
    $scope.nextPageDisabled = function() {
      return $scope.currentPage === $scope.pageCount()-1 ? "disabled" : "";
    };
    $scope.setPage = function(n) {
      $scope.currentPage = n;
    };
  };
  return {variables: variables, paginate: paginate};
});

app.controller('searchCtrl', function($scope, $http, common){
  $scope.keyword='';
  $scope.search = function(keyword){
    $scope.keyword=keyword;
    $http.get('/cgi-bin/search.py?q='+keyword).success(function(response){
        common.variables.jsonData = response;
        common.variables.filepath = '';
    });
  };
});

app.controller('frontPage', function($scope, common, $location, $anchorScroll) {
  $scope.filepath = common.variables.filepath;
  $scope.outfile1 = common.variables.outfile1;
  $scope.outfile2 = common.variables.outfile2;
  $scope.outfile3 = common.variables.outfile3;
  $scope.optionsTab = false;
  $scope.active = false;

  $scope.$watch(function(){
    $scope.filepath = common.variables.filepath;
    $scope.outfile1 = common.variables.outfile1;
    $scope.outfile2 = common.variables.outfile2;
    $scope.outfile3 = common.variables.outfile3;

    if(common.variables.filepath!='/output/intro.html' && common.variables.filepath!=''){
      $scope.active = true;
      $scope.optionsTab = true;
    }else if(common.variables.filepath==''){
      $scope.active = false;
      $scope.optionsTab = true;
      if($scope.objs!=common.variables.jsonData){
        $scope.objs = common.variables.jsonData;
        if($scope.objs.length!=0){
          common.paginate($scope);
        }else{
          $scope.objs=undefined;
        }
      }
    }
    if($scope.optionsTab){
      $location.hash();
      $anchorScroll();
    }
  });
  $scope.backToMain = function(){
    common.variables.filepath = '/output/intro.html';
    $scope.active = false;
    $scope.optionsTab = false;
    $location.hash();
    $anchorScroll();
  };
});

app.controller('listOfReports', function($scope, $http, $interval, common, $location, $anchorScroll){
    $scope.refresh = function(){
      $http.get('/cgi-bin/databases.py').success(function(response) {
          $scope.objs = response;
          common.paginate($scope);
      });
    };
    $scope.refresh();
    $interval( function(){ $scope.refresh(); }, 60000);


    $scope.load = function(obj){
      common.variables.filepath = '/output/'+obj.dbname+'/'+obj.dbname+'.html';
      common.variables.outfile1 = '/output/'+obj.dbname+'/'+obj.dbname+'.xlsx';
      common.variables.outfile2 = '/output/'+obj.dbname+'/'+obj.dbname+'_clean.xlsx';
      common.variables.outfile3 = '/output/'+obj.dbname+'/'+obj.dbname+'.pdf';
      common.variables.jsonData = '';
      $location.hash();
      $anchorScroll();
    };
});

app.filter('offset', function() {
  return function(input, start) {
    return (input instanceof Array) ? input.slice(+start) : input
  };
});

app.controller('GenerateNewReport', function($scope, $http) {
    $scope.countries = [];
    $http.get('/cgi-bin/countries.py').success(function(response) {
        for(country in response){
           $scope.countries.push(country);
        }
        $scope.countries.sort();
    });
    //---------------------------------------
    //             VALIDATION
    //---------------------------------------
    $scope.report = { fromDate : new Date(), toDate : new Date() };
    $scope.submit = function(report){
      if($scope.myForm.$valid){
        $http.get('/cgi-bin/process.py?'+$.param(report)).success(function(response){
          if(response.message=='True'){
            $scope.showSuccessAlert = true;
            $scope.showErrorAlert = false;
          }else{
            $scope.message = response.message;
            $scope.showSuccessAlert = false;
            $scope.showErrorAlert = true;
          }
        });
      }
    };
    $scope.switchBool = function(value) {
       $scope[value] = !$scope[value];
    };
    //---------------------------------------
    //             DATE PICKER
    //---------------------------------------
    $scope.today = function() {
      $scope.report.fromDate = new Date();
      $scope.report.toDate = new Date();
    };
    $scope.today();
    $scope.clear = function() {
      $scope.report.fromDate = null;
      $scope.report.toDate = null;
    };

    $scope.inlineOptions = {
      maxDate: new Date(2020, 7, 15),
      minDate: new Date(2006, 7, 15)
    };

    $scope.dateOptions = {
      maxDate: new Date(2020, 7, 15),
      minDate: new Date(2006, 7, 15)
    };

    $scope.open1 = function(){ $scope.popup1.opened = true; };
    $scope.open2 = function(){ $scope.popup2.opened = true; };

    $scope.setFromDate = function(){
      if($scope.report.fromDate>$scope.report.toDate){
        $scope.report.fromDate = $scope.report.toDate;
      }
    };
    $scope.setToDate = function(){
      if($scope.report.fromDate>$scope.report.toDate){
        $scope.report.toDate = $scope.report.fromDate;
      }
    };

    $scope.format = 'yyyy-MM-dd';
    $scope.popup1 = { opened: false };
    $scope.popup2 = { opened: false };
});
app.directive('dbnameAvailableValidator', ['$http', function($http) {
    return {
      require : 'ngModel',
      link : function($scope, element, attrs, ngModel) {
        $scope.$watch(attrs.ngModel, function(value) {
          $http.get('/cgi-bin/available.py?db='+ value).success(function(response){
            ngModel.$setValidity('dbnameAvailable', response.available);
          });
        });
      }
    }
}]);
