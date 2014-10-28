var module = angular.module('main', ['ionic'])
.controller('PopupCtrl',function($scope, $ionicPopup, $timeout) {
    $scope.showPopup =function() {
        var popup = $ionicPopup.show({
        template: '<form action="love2041.cgi?page=detail&user=$username" method="post"><textarea rows="5" name="message"></textarea><input class="button button-assertive button-block" type="submit" style="background:#E64274"></form>',
        buttons:[{text:"Cancel",type:"moveUp"}], 
        title: 'Send A Message!',
        })
    }
    });




