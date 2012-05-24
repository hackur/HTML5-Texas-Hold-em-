var table_init = function() {

	document.ontouchmove = function(e) {
		e.preventDefault();
	};

	seatInit();

	actionButton.disable_all();
	actionButton.disable_AutoButtons();


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
				//history.go(-1);
				window.location = "http://" + document.domain + ":" + window.location.port + "/static/room/room.html"

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
			console.log(data);
			if( data.status == "success" ) {
				console.log("enter success!");
				window.user_info.userIsPlay = false;
				window.room_info = data.room;
				if(data.room.pot){
					board_msg_handler.process(data.room.pot);
				}
				if(data.room.start){
					board_msg_handler.process(data.room.start);
				}
				listenBoardMessage(data.room.timestamp); 
				for(var i = 0; i < data.room.seats.length; i++ ) {
					var seatData = data.room.seats[i] ;
					var seatObj = SeatList[i];
					if(data.room.seats[i] == null ) {						
						SeatList[i].setIsSat(false);
					}
					else {
						SeatList[i].sit(data.room.seats[i].user,
							data.room.seats[i].player_stake,
							data.room.seats[i].uid
							);
						console.log("SET STAKE!!!");
						console.log(seatData.status);
						if(seatData.status > 1){
						/*(SEAT_EMPTY,SEAT_WAITING,SEAT_PLAYING,SEAT_ALL_IN) = (0,1,2,3) */
							seatObj.setStake(seatData.player_stake,
									seatData.table_amount);
							
						}

						if( SeatList[i].userid == window.user_info.id) {
							sit_transit.transit(i);
							SeatList[i].showStand();
							window.user_info.userIsSat = true;
							window.user_info.sit_no = i;
						}
						else{
							if(seatData.status > 1){
								dealCard.show_back_card(i);
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
					window.public_card = data.room.publicCard;
					dealCard.send_public_card(data.room.publicCard);
				}
				if(data.room.hc){
					poker_lib.setCard(data.room.hc[0], '#cards_in_hand1');
					poker_lib.setCard(data.room.hc[1], '#cards_in_hand2');
					$("#cards_in_hand1").fadeIn();
					$("#cards_in_hand2").fadeIn();
				}
				if(data.room.next){
					board_msg_handler.process(data.room.next);
				}

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
		console.log("=============================data==========================")
		console.log(data);
		console.log("===========================================================")
		console.log("current time stamp =>"+curtimestamp)
		console.log("time stamp =>"+data[0].timestamp)
		for(var i = 0; i < data.length; i++) {
			timestamp = data[i].timestamp;
			if(timestamp <= curtimestamp && data[i].resend != 1){
				continue;
			}
			curtimestamp = timestamp;
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
			nowebsocket = true;
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
			var closeBtn = $(".closeBtn");
			closeBtn.click(function(e) {
				seatObj.player.hide();	
			});
//			var info_hide = function(e) {
//				var infoWindow = $(".closeBtn");
//				var infoWindowPosition = infoWindow.offset();
//				var infoWindowSize = {"width": infoWindow.width(), "height": infoWindow.height()};
//				pos = get_event_position(e);
//				console.log(infoWindowSize["width"]);
//				console.log(pos[0]);
//				if(pos[0] < infoWindowPosition["left"] || pos[0] > infoWindowPosition["left"]+infoWindowSize["width"]) {
//					console.log("I'm hiding myself!");
//					seatObj.player.hide();	
//			e.stopPropagation();
//					window.removeEventListener("click", info_hide,true);
//				}
////				$("#stand").bind("click", window.actionButton.send_action_stand());
////				$("#backBtn").bind("click");
//			}
//			window.addEventListener("click", info_hide, true);
////			$("#stand").unbind("click");
////			$("#backBtn").unbind("click");
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
