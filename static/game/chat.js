(function ($){
	var obj		= {};
	obj.message = [];

	function sendMsg(){
		console.log("click start");
		obj.send();
		$('#chat-input').val('');
		console.log("click end");
	}
	obj.init = function (){
		console.log("init sit dialog start");
		$("#chat-send-btn").bind(event_click,sendMsg);

		$(window).keypress(function(e) {
			if(e.keyCode == 13){
				sendMsg();
			}
		});
		$("input:text:visible:first").focus();
		$('#chat-history-btn').bind(event_click,function(){
			obj.maximize();
		});
		console.log("init sit dialog end");
	}
	obj.display	= function(){
		$('#chat-dialog').css("display","block");
	};
	obj.hide	= function(){
		$('#chat-dialog').css("display","none");
	}
	obj.maximize= function(){
		$('#chat-history').removeClass("chat-history-collapse");
		$('#chat-history').addClass("chat-history-expand");
		$('#chat-history-btn').text("C");
		$("#chat-history-btn").unbind(event_click);
		$('#chat-history-btn').bind(event_click,function(){
			obj.minimize();
		});
	}
	obj.minimize= function(){
		$('#chat-history').removeClass("chat-history-expand");
		$('#chat-history').addClass("chat-history-collapse");
		$('#chat-history-btn').text("E");
		$("#chat-history-btn").unbind(event_click);
		$('#chat-history-btn').bind(event_click,function(){
			obj.maximize();
		});
	}
	obj.send	= function(content){
		var message = $('#chat-input').val();
		$.ajax({
			type:'post',
			url:'/send-chat',
			data:{seat:window.user_info.sit_no, message:message},
			success:function(data){
				console.log(data);
			},
			dataType:'json'
		});
	}
	obj.receive	= function(data){
		var username		= SeatList[data.seat].username;
		var temp_msg_id		= "temp-message-" + data.timestamp;
		var temp_message	= $("<div class='temp-message' id='"+temp_msg_id+"'>" + data.content + "</div>"); 
		$('#chat-history').append("<div class='chat-message'>" + username + ": " + data.content + "</div>");
		//console.log(data);
		//console.log(SeatList[data.seat])
		SeatList[data.seat].appendMessage(temp_message);
		setTimeout(
			function(){
				temp_message.addClass("temp-message-in");
			},
			100
		);
		setTimeout(
			function(){
				temp_message.addClass("temp-message-out");
			}, 
			2000
		);
		setTimeout(
			function(){
				temp_message.remove();
			}, 
			3000
		);

	}
	window.chat_dialog = obj;	
})($);
