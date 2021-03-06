(function($){
	var awardDialog = {};
	awardDialog.show = function() {
		$(".awardDialog").show();
		$("#screen-overlay").addClass("screen-cover");
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
	$("#screen-overlay").removeClass("screen-cover");
	//$(".awardDialog").fadeOut()
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
	$("#confirmBtn").click(confirmBtnClicked);
	$("#cancelBtn").click(cancelBtnClicked);
	$("#closeButton").click(function(){
		$(".settingNickDialog").hide();
		history.go(-1);});
	function confirmBtnClicked() {
		update_user_info();
		//alert($(".name").val() + "\n" + gender);
	
	}
	function cancelBtnClicked() {
		$(".settingNickDialog").hide();
		history.go(-1);
	}
	var update_user_info = function() {
		var genderText	= -1;
		var nickname	= '-1';
		if (gender==0){
			genderText = 'F';
		}else{
			genderText = 'M';
		}
		nickname = $('#nickname-input').val();
		if(nickname == "")
			return;
		$(".settingNickDialog").hide();
		$.ajax({
			type: "post",
			url:  "/userinfo",
			data: {nickname:nickname, gender:genderText},
			success: function(data) {
				console.log(data);
				if(data.status == 'success'){
					console.log("success");
					info_init();
				}else{
					console.log("failed");		
				}
			},
			dataType: "json"
		});
	};
});
