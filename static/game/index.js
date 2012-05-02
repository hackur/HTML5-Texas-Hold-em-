var table_init = function() {

	document.ontouchmove = function(e) {
		e.preventDefault();
	};

	seatInit();

	actionButton.disable_all();


	$.each(SeatList,function(index,seat){
		take_place(seat.id, seat);
	});
	
	
	//game_control.deal();
};

var fetch_user_info = function(){
	$.ajax({
		type:'get',
		url:"/userinfo",
		data:{},
		success:function(data){
			console.log("Below is user data:");
			console.log(data);
			window.user_info = {};
			user_info.username = data.n;
			user_info.asset = data.s;
			user_info.level = data.l;
			user_info.id	=data.id;
			enter();
		},
		dataType:'json',
		cache:false
	});
};

$(function(){
	$("#backBtn").bind("vclick",function(){
		if(window.user_info.userIsSat){
			actionButton.send_action_stand();
			setTimeout(function(){
				history.go(-1);
			},500);
		}
		else{
			history.go(-1);
		}
	});
});

var enter = function(){
	var room = localStorage["current_room_id"];
	$.post(
		"/enter",
		{room_id:room},
		function(data){
			console.log("Below is enter data:");
			console.log(data);
			if( data.status == "success" ) {
				console.log("enter success!");
				listenBoardMessage(data.room.timestamp); // TODO Add timestamp
				console.log([data.room.seats, "++++++___________++++++++"]);
				for(var i = 0; i < data.room.seats.length; i++ ) {
					if(i < SeatList.length){
						if(data.room.seats[i] == null ) {						
							SeatList[i].setIsSat(false);
						}
						else {

							SeatList[i].sit(data.room.seats[i].user,
									data.room.seats[i].player_stake,
									data.room.seats[i].uid
							);
							
							if( SeatList[i].userid == window.user_info.id) {
								sit_transit.transit(i);
								SeatList[i].showStand();
								console.log("-----------------------" + i);
								window.user_info.userIsSat = true;
								window.user_info.sit_no = i;
							}
						}
					}
				}

				if (!window.user_info.userIsSat) {
					for(var i = 0; i < data.room.seats.length; i++ ) {
						if (data.room.seats[i] == null ) {
							SeatList[i].showSeatdownbg();
						}
					}
				}

				if(data.room.publicCard){
					dealCard.send_public_card(data.room.publicCard);
				}
				//console.log(SeatList);


				window.room_info = data.room;
				//max_stake;
				//min_stake;
				//blind;
				//timestamp;

			}
						
		},
		'json'
	);
};

var index = 1;

var curtimestamp = 0;
function listenBoardMessageSocket(timestamp){
	curtimestamp = timestamp;
	var ws = 0;
	var retry = 0 ;
	var success = 0;
	function onopen(evt){
		var msg = JSON.stringify({timestamp:timestamp});
		window.ws = ws;
		ws.send(msg);
		success = true;
	}
	function onmessage(evt) {
		var data = JSON.parse(evt.data);
		var timestamp = 0;
		retry = 0;
		for(var i = 0; i < data.length; i++) {
			timestamp = data[i].timestamp;
			if(timestamp <= curtimestamp){
				continue;
			}
			curtimestamp = timestamp;
			//console.log(data[i]);
			console.log(timestamp);
			board_msg_handler.process(data[i]);
		}
		console.log(timestamp);
		var msg = JSON.stringify({timestamp:timestamp});
		ws.send(msg);
	};
	function onclose(evt){
		message_box.showMessage("WebSocket closed",5);
		if(!success){
			listenBoardMessage(timestamp,true);
			return;
		}
		setTimeout(function(){
			message_box.showMessage("Retrying",5);
			setup_ws();
			retry += 1;
			if (retry > 10){
				window.location.reload();
			}
		},1000);
	}
	function setup_ws(){
		var host = window.location.host;
		ws = new WebSocket("ws://" + host +"/sk");
		ws.onerror = onclose;
		ws.onclose = onclose;
		ws.onmessage = onmessage;
		ws.onopen = onopen;
	}
	setup_ws();

}
var listenBoardMessage = function(timestamp,nowebsocket) {
	if(!nowebsocket){
		try{
			listenBoardMessageSocket(timestamp);
			return;
		}catch(err){
			message_box.showMessage("Seems your browser doesn't support WebSocket...");
		}
	}
	if(!timestamp) timestamp = -1;

	$.ajax({
		type: "post",
		url: "/listen-board-message",
		data: { timestamp: timestamp },
		success: function(data) {
			console.log("Below is listen-board-message:");
			console.log(data);
			//data = JSON.parse(data);

			for(var i = 0; i < data.length; i++) {
				timestamp =data[i].timestamp;
				//console.log(data[i]);
				board_msg_handler.process(data[i]);
			}

			listenBoardMessage(timestamp,nowebsocket);
		},
		error: function(XMLHttpRequest, textStatus, errorThrown) {
			console.log("listen board message replay error!!!");
			console.log(textStatus);
			if(index < 6) {
				listenBoardMessage(timestamp,nowebsocket);
			}
			index++;
		},
		dataType: "json"
	});
};



var take_place = function(seatID, seatObj) {
	seatObj.getSeatDIV().click(function() {
		if(!seatObj.getIsSat() && !window.user_info.userIsSat){

			console.log(seatObj);
			console.log(this);
			console.log("sliderbaris clicked");
			show_loading();
			$.ajax({
				type:'get',
				url:"/userinfo",
				data:{},
				success:function(data){
					console.log("Below is user data:");
					console.log(data);
					window.user_info = {};
					user_info.username = data.n;
					user_info.asset = data.s;
					user_info.level = data.l;
					user_info.id	=data.id;
					hide_loading();
					if(user_info.asset < window.room_info.min_stake){
						message_box.showMessage("您只有:" +user_info.asset,2);
						message_box.showMessage("最少携带:" + room_info.min_stake,2);
						message_box.showMessage("你木有足够的钱'_'",2);
					}
					else{
						sit_down_dialog.show(seatObj);
					}
				},
				dataType:'json',
				cache:false
			});

			//sit_dialog.show();
		}
		else if(seatObj.getIsSat()) {
			console.log(seatObj.getIsSat());
			//customer information
			// alert("[IsSat == 1] Customer Information!");
			console.log(seatObj.player);
			for (key in seatObj.player) {
				if (seatObj.player[key] == undefined) {
					seatObj.player[key] = "#";
				}
			}
			window.SelectedSeat = seatObj;
			seatObj.player.show(seatObj.player);
			console.log(".............");
			console.log(window.SelectedSeat);
			var info_hide = function(e) {
				var infoWindow = $("#player-info-content");
				var infoWindowPosition = infoWindow.offset();
				var infoWindowSize = {"width": infoWindow.width(), "height": infoWindow.height()};
				pos = get_event_position(e);
				console.log(infoWindowSize["width"]);
				console.log(pos[0]);
				if(pos[0] < infoWindowPosition["left"] || pos[0] > infoWindowPosition["left"]+infoWindowSize["width"]) {
					console.log("I'm hiding myself!");
					seatObj.player.hide();	
			e.stopPropagation();
					window.removeEventListener("click", info_hide,true);
				}
//				$("#stand").bind("click", window.actionButton.send_action_stand());
//				$("#backBtn").bind("click");
			}
			window.addEventListener("click", info_hide, true);
//			$("#stand").unbind("click");
//			$("#backBtn").unbind("click");
		}
	});
};


/*  ctPos is number */
var time_bar = function(ctPos) {
	SeatList[ctPos].setCountdown(ctPos);
	
};


function getSeatById(userid){
	for(var i = 0; i < SeatList.length; i++){
		var seat = SeatList[i];
		if(seat.getIsSat() && seat.userid == userid){
			return seat;
		}
	}
}
