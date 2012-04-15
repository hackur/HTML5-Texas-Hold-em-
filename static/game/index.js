


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
var table_init = function() {
	decide_event();

	document.ontouchmove = function(e) {
		e.preventDefault();
	};

	//window.cardpos = [["300px", "70px"],["505px", "70px"],["710px", "70px"],["665px","335px"]];	//clockwise #seat4,#seat3,#seat2,#seat1
	
	//TODO GET cardpos from css. not hard code here
	window.cardpos = [["390px","360px"],["665px","360px"],["710px", "70px"],["505px", "70px"],["300px", "70px"]];

	seatInit();

	actionButton.disable_all();


	$.each(SeatList,function(index,seat){
		take_place(seat.id, seat);
	});
	
	
	//game_control.deal();
};

var fetch_user_info = function(){
	$.get(
		"/userinfo",
		{},
		function(data){
			console.log("Below is user data:");
			console.log(data);
			window.user_info = {};
			user_info.username = data.n;
			user_info.asset = data.s;
			user_info.level = data.l;
			console.log(window.user_info);
			enter();
		},
		'json'
	);
};
var enter = function(){
	var room = 1;
	$.post(
		"/enter",
		{room_id:room},
		function(data){
			console.log("Below is enter data:");
			console.log(data);
			if( data.status == "success" ) {
				console.log("enter success!");
				listenBoardMessage();
				//console.log(data.room.seats);
				for(var i = 0; i < data.room.seats.length; i++ ) {
					if(i < SeatList.length){
						if(data.room.seats[i] == null ) {							
							SeatList[i].setIsSat(0);							
						}
						else {
							SeatList[i].sit(data.room.seats[i].user,
									data.room.seats[i].player_stake,
									data.room.seats[i].uid
							);
							
							if( SeatList[i].username == window.user_info.username ) {
								sit_transit.transit(i);
								console.log("-----------------------" + i);
								window.user_info.userIsSat = true;
							}
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
var listenBoardMessage = function(timestamp) {
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

			listenBoardMessage(timestamp);
		},
		error: function(XMLHttpRequest, textStatus, errorThrown) {
			console.log("listen board message replay error!!!");
			console.log(textStatus);
			if(index < 6) {
				listenBoardMessage();
			}
			index++;
		},
		dataType: "json"
	});
};



var take_place = function(seatID, seatObj) {
	seatObj.getSeatDIV().click(function() {
		if(!seatObj.getIsSat() && !window.user_info.userIsSat)
		{
			sit_dialog.show(seatObj);
		}
		else if(seatObj.getIsSat()) {
			console.log(seatObj.getIsSat());
			//customer information
			alert("[IsSat == 1] Customer Information!");
		}
	});
};

var send_chips = function(chipId, tstake, callback) {
	var _id = chipId;
	

	console.log("*************************");
	var seatid = "#seat" + _id;
	var pos = SeatList[_id].pos;
	var chipPos = windows.cardpos[SeatList[_id].pos];
	//set the chips original top and left 
	
	//show it and animate
	var chip = $('<img class="chip5"/>');
	chip.css("top",chipPos[1]);
	chip.css("left",chipPos[0]);
	var chipClass = "chip" + pos;
	chip.appendTo("#gametable");
	chip.addClass(chipClass + " chip" );
	$("#tstake" + chipId).html(tstake);
	
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
