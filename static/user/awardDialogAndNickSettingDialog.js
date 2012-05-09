(function($){
	var awardDialog = {};
	awardDialog.show = function() {
		$(".awardDialog").show();
	}
	window.awardDialog = awardDialog;
})($);
(function($){
	var settingNickDialog = {};
	settingNickDialog.show = function() {
		$(".settingNickDialog").show();
	}
	window.settingNickDialog = settingNickDialog;
})($);

$(function(){
$(".awardDialog").click(function(){
	$(".awardDialog").hide();
	});
});

$(function() {
	$(".femaleCheck").click(femaleClick);
	$(".maleCheck").click(maleClick);
	var gender = 1;
	function femaleClick() {
		gender = 0;
		$(".femaleCheck").css("background","url(./image/check.png)");
		$(".maleCheck").css("background","url(./image/nocheck.png)");
	}
	function maleClick() {
		gender = 1;
		$(".maleCheck").css("background","url(./image/check.png)");
		$(".femaleCheck").css("background","url(./image/nocheck.png)");
	}
	$(".confirmBtn").click(confirmBtnClicked);
	$(".cancelBtn").click(cancelBtnClicked);
	function confirmBtnClicked() {
		$(".settingNickDialog").hide();
		//alert($(".name").val() + "\n" + gender);
	
	}
	function cancelBtnClicked() {
		$(".settingNickDialog").hide();
		history.go(-1);
	}
});