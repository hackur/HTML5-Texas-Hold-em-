

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
function decide_event(){
	window.event_up = "touchend";
	window.event_down = "touchstart"; 
	window.event_move = "touchmove";
	if(navigator.userAgent.match(/iPhone/i) ||
	 		navigator.userAgent.match(/Android/i) ||
			navigator.userAgent.match(/iPad/i) ||
			navigator.userAgent.match(/iPod/i) ||
			navigator.userAgent.match(/webOS/i) ||
			navigator.userAgent.match(/BlackBerry/)
	){
		event_up = "touchend";
		event_down = "touchstart"; 
		event_move = "touchmove";
		window.touch_enable = true;
	}
	else{
		event_up = "mouseup"; 
		event_down = "mousedown"; 
		event_move = "mousemove";
		window.touch_enable = false;
	}

	if( $.browser.webkit ) {
			eventTransitionEnd = "webkitTransitionEnd";
	} else if( $.browser.mozilla ) {
			eventTransitionEnd = "transitionend";
	} else if ($.browser.opera) {
			eventTransitionEnd = "oTransitionEnd";
	}
}

var info_init = function() {
	decide_event();

	window.bigframe = ["#info","#email","#market","#recharge","#friend"];

	document.getElementById('bigFrame1').style.display = "block";
	$("#info")[0].style.backgroundImage = "url(./image/left.png)";
	$("#portrait_box").click(function() {
		$("#change_por")[0].style.display = "block";
		uploadImage();
		$("#icancel").click(function() {
			$("#change_por")[0].style.display = "none";
		});
	});
	$("#reply").click(function() {
		$("#replyFrame")[0].style.display = "block";
		sendEmail();
	});

	for(var i = 0; i <= bigframe.length; i++) {
		frameControl(bigframe[i], i);
	}
	recharge.drag();

};

var frameControl = function(frame, i) {
	$(frame).click(function() {	
		document.getElementById('bigFrame' + (i+1)).style.display = "block";
		for(var j = 0; j <= 4; j++) {
			if( j != i) {
				document.getElementById('bigFrame' + (j+1)).style.display = "none";
				$(bigframe[j])[0].style.backgroundImage = "";		//not "url()"
			}
		}
		if( i == 0) {
			$(frame)[0].style.backgroundImage = "url(./image/left.png)";
		}
		if( i == 4) {
			$(frame)[0].style.backgroundImage = "url(./image/right.png)";	
		}
		if( i > 0 && i < 4) {
			$(frame)[0].style.backgroundImage = "url(./image/middle.png)";	
		}
	});
};

var uploadImage = function() {
	var status = $('#status');
	$('form').ajaxForm({
		complete: function(xhr) {
			var data = JSON.parse(xhr.responseText);
			console.log(data);
			if(data.status == "success") {
				var url = "../." + data.url;
				console.log(url);
				status.html("upload success");
				var image = $('<img id="image1" src=' + url + ' />').appendTo($("#portrait_box"));
				$("#image1").css({'width': 102, 'height': 126, 'top': 6, 'left': 8, 'position': 'absolute'});
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
			var url = "../." + data.head_portrait;
			var image = $('<img id="image2" src=' + url + ' />').appendTo($("#portrait_box"));
			$("#image2").css({'width': 102, 'height': 126, 'top': 6, 'left': 8, 'position': 'absolute'});
			
			$("#property").html($("#property").html() + data.asset);
			$("#family").html($("#family").html() + data.family);
			$("#rank").html($("#rank").html() + data.level);
			$("#ID").html($("#ID").html() + data.name);
			$("#winRate").html($("#winRate").html() + data.percentage);
			$("#winBiggestStake").html($("#winBiggestStake").html() + data.max_reward);
			$("#pos").html($("#pos").html() + data.position);
			$("#idiograph").html($("#idiograph").html() + data.signature);
			$("#totalInnings").html($("#totalInnings").html() + data.total_games);
			$("#victoryInnings").html($("#victoryInnings").html() + data.won_games);
			$("#latestOnline").html($("#latestOnline").html() + data.last_login);
		},
		dataType: "json"
	});
};

var getEmailInfo = function() {
	$.ajax({
		type: "post",
		url:  "/list-email",
		data: {},
		success: function(data) {
			console.log(data);			
		},
		dataType: "json"
	});
};

var sendEmail = function() {
	$("#sureButton").click(function() {
		var msg = $("#text1").html();
		var des = 1;
		console.log(msg);
		$.ajax({
			type: "post",
			url:  "/send-email",
			data: {content: msg, destination: des},
			success: function(data) {
				console.log(data);
				alert("send success...");
				$("#replyFrame")[0].style.display = "none";	
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