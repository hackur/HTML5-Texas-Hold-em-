(function ($){
	var obj		= {};
	obj.message = [];

	obj.init = function (){
		console.log("init sit dialog start");
		$("#chat-sent-btn").click(function(){
			console.log("click start");
			obj.send();
			$('#chat-input').val('');
			console.log("click end");
		});
		console.log("init sit dialog end");
	}
	obj.maximize= function(){

	}
	obj.minimize= function(){
	
	}
	obj.send	= function(content){
		var message = $('#chat-input').val();
		$.ajax({
			type:'post',
			url:'../../send-chat',
			data:{seat:window.user_info.sit_no, message:message},
			success:function(data){
				console.log(data);
			},
			dataType:'json'
		});
	}
	obj.receive	= function(data){
		console.log(data);
		var username = SeatList[data.seat].username;
		$('#chat-history').append("<div class='chat-message'>" + 
									username + ": " + data.content + "</div>");	
	}
	window.chat_dialog = obj;	
})($);
