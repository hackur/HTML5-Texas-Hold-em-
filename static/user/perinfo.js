

window.get_event_position = function(e){
	if(window.touch_enable && e.touches){
		if(e.touches[0]){
			e.clientX =  e.touches[0].pageX;
			e.clientY =  e.touches[0].pageY;
		}
		else{
			e.clientX =  e.changedTouches[0].pageX;
			e.clientY =  e.changedTouches[0].pageY;
		}
	}
	return [e.clientX,e.clientY]
}

var info_init = function() {
	dailyBonus();
	getUserImage();
	listEmail(1);
	buddyInfo();
	initCommodity();
	/* viewEmail(); */
	bindSendFriendEmail();
	window.bigframe = [	
    {header:"#info",	content:"#info_frame", background:      "url(/static/user/image/left.png)"},
    {header:"#email",	content:"#mail_list_frame", background: "url(/static/user/image/middle.png)"},
    {header:"#market",	content:"#market_frame", background:    "url(/static/user/image/middle.png)"},
    {header:"#recharge",content:"#recharge_frame", background:  "url(/static/user/image/middle.png)"},
    {header:"#friend",	content:"#friend_frame", background:    "url(/static/user/image/right.png)"}];

	$(bigframe[0].content).css("display", "block");
	$(bigframe[0].header).css("background-image", "url(/static/user/image/left.png)");
    /*
	$("#portrait_box").bind("vclick", function() {
		$("#change_por")[0].style.display = "block";
		uploadImage();
		$("#icancel").bind("vclick", function() {
			$("#change_por")[0].style.display = "none";
		});
	});
    */
	$("#reply").bind("vclick", function() {
		$("#receiver").text("收件人ID："+window.SelectedEmail.senderName);
		$("#replyFrame textarea").unbind("keyup");
		$("#replyFrame").css("display","block");
		sendEmail();
	});
	$('#replay-cancel-btn').bind('vclick', function(){
		$("#replyFrame").css("display","none"); 
	});
	$("#delete").bind("vclick",function(){
		var emailId = window.SelectedEmail.id;
		$.ajax({
			type: "post",
			url:  "/delete-email",
			data: {email_id:emailId},
			success: function(data) {
				listEmail();
				$('#email').click();
			},
			dataType: "json"
		});
	});
	$('#mail_page_last').bind("vclick",function(){
		listEmail(window.EmailCurrentPage - 1);	
	});
	$('#mail_page_next').bind("vclick",function(){
		listEmail(window.EmailCurrentPage + 1);	
	});
	$('#mail_page_btn').bind("vclick",function(){
		listEmail($('#mail_page_input').val()); 
	});

	for(var i = 0; i < bigframe.length; i++) {
		frameControl(bigframe[i], i);
	}
	//recharge.drag();
	$("#lobby").bind("vclick",function(){
		window.location = "/static/room/room.html";
	});
	$("#quick_acc").bind("vclick",function(){
		$.ajax({
			type:"get",
			url:"/fast_enter",
			success:function(data){
				localStorage["current_room_id"] = data;
				window.location = "/static/game/game.html";
			}
		});
	});

	$("#logout").bind("vclick",function(){
		window.location="/static/facebook.html";
		/*
		$.post("/logout",function(){
			window.location="/";
		});
		*/

	});
};

var frameControl = function(frame, i) {
	$(frame.header).bind("vclick", function() {
		$('.bigFrame').css("display", "none");
		$('.frame-header').css("background-image", "none");
		$(frame.content).css("display","block");
		$(frame.header).css("background-image",frame.background);
	});
};

var uploadImage = function() {
	var status = $('#status');
	$('form').ajaxForm({
		complete: function(xhr) {
			var data = JSON.parse(xhr.responseText);
			console.log(data);
			if(data.status == "success") {
				var url = data.url;
				console.log(data.url);
				console.log(url);
				status.html("upload success");
				$("#image1").attr("src", url);
			}
		}
	});
};
var getUserImage = function() {
	$.ajax({
		type: "post",
		url:  "/personal-archive",
		data: {},
		success: function(data) {
			console.log(data);
			var url = data.head_portrait;
			$("#image1").attr("src", url);
			$("#ID").html(textDict["id"] + " : " + data.name);
			$("#rank").html(textDict["rank"] + " : "+ data.level);
			$("#property").html(textDict["property"] + " : "+ data.asset);
		//	$("#family").html(textDict["family"] + data.family);
			$("#winRate").html(textDict["winRate"] + " : "+ data.percentage);
			$("#winBiggestStake").html(textDict["winBiggestStake"] + " : "+ data.max_reward);
		//	$("#pos").html(textDict["pos"] + data.position);
			$("#idiograph").html(textDict["idiograph"] + " : "+ data.signature);
			$("#totalInnings").html(textDict["totalInnings"] + " : "+ data.total_games);
			$("#victoryInnings").html(textDict["victoryInnings"] + " : "+ data.won_games);
			$("#latestOnline").html(textDict["latestOnline"]+ " : " + data.last_login);
                /*
			if(data.gender == 'N/A'){
				window.settingNickDialog.show();
			}
                */
		},
		dataType: "json"
	});
};

var listEmail = function(page) {
	$.ajax({
		type: "post",
		url:  "/list-email",
		data: {page:page},
		success: function(data) {
			$('#mail_list').html('');
			for(var k = 0; k < data.emails.length; k++){
				var email = Email(data.emails[k]);
				$('#mail_list').append(email.toHTML());
				window.EmailList.push(email);
			}
			window.EmailCurrentPage = data.current;
			window.EmailTotal		= data.total;
			window.EmailTotalPages	= data.pages;
			console.log(data);
		},
		dataType: "json"
	});
};

var sendEmail = function() {
	$("#sureButton").unbind("vclick");
	$("#sureButton").bind("vclick",function() {
		var reply_to_id = window.SelectedEmail.id
		var msg = $("#text1").val();
		var des = window.SelectedEmail.senderId;
		$.ajax({
			type: "post",
			url:  "/send-email",
			data: {content: msg, destination: des, reply_to:reply_to_id},
			success: function(data) {
				console.log(data);
				$("#replyFrame").css("display", "none");
				window.SelectedEmail = null;
			},
			dataType: "json"
		});
	});
};

var viewEmail = function() {
	var email = 1;
	$.ajax({
		type: "post",
		url:  "/view-email",
		data: {email: email},
		success: function(data) {
			console.log(data);
		},
		dataType: "json"
	});
};

var buddyInfo = function() {
	$.ajax({
		type: "post",
		url:  "/buddy-info/",
		data: {},
		success: function(data) {
			console.log(data);
			//console.log(data.leftfriendId)
			for(var i = 0; i < data.friends.length; i++) {
				$("#name" + i).html(data.friends[i].name);
				view_friend(data.friends[i], i);
			}
		},
		dataType: "json"
	});
};
var dailyBonus = function() {
	$.ajax({
		type: "get",
		url:  "/dailybonus",
		data: {},
		success: function(data) {
			if(data.status == 'success'){
				window.awardDialog.show();
			}else{
				console.log("failed");
			
			}
		},
		dataType: "json"
	});
	
};
var view_friend = function(friend, i) {
	$("#name" + i).click(function() {

		$("#fID").html("昵称：");
		$("#ffamily").html("家族：");
		$("#fpos").html("职位：");
		$("#frank").html("等级：");
		$("#fpro").html("资产：");
		
		$("#fID").html($("#fID").html() + friend.name);
		$("#ffamily").html($("#ffamily").html() + friend.family);
		$("#fpos").html($("#fpos").html() + friend.position);
		$("#frank").html($("#frank").html() + friend.level);
		$("#fpro").html($("#fpro").html() + friend.asset);
		var url = friend.head_portrait;
		$("#image3")[0].src = url;
		$("#image3").css({'width': 102, 'height': 126, 'top': 6, 'left': 8, 'position': 'absolute'});

		window.SelectedFriend = friend;
	});
};
var bindSendFriendEmail = function(){
	$('#fsend').bind("vclick",function(){
		console.log("fsend start");
		$('#email').click();
		$("#receiver").text("收件人ID："+window.SelectedFriend.name);
		$("#replyFrame textarea").unbind("keyup");
		$("#replyFrame").css("display","block");
		$("#replyFrame").css("display","block"); 
		$("#sureButton").unbind("vclick");
		$("#sureButton").bind("vclick",function() {
			var des = window.SelectedFriend.id
			var msg = $("#text1").val();
			$.ajax({
				type: "post",
				url:  "/send-email",
				data: {content: msg, destination: des},
				success: function(data) {
					$("#replyFrame").css("display", "none");	
					window.SelectedFriend = null;
				},
				dataType: "json"
			});
		});
		console.log("fsend end");
	});
}
window.reloadUserInfo = getUserImage;
