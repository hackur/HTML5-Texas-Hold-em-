


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

}
var table_init = function() {
	decide_event();

	document.ontouchmove = function(e) {
		e.preventDefault();
	};

	//window.cardpos = [["300px", "70px"],["505px", "70px"],["710px", "70px"],["665px","335px"]];	//clockwise #seat4,#seat3,#seat2,#seat1
	
	//TODO GET cardpos from css. not hard code here
	window.cardpos = [["390px","360px"],["665px","360px"],["710px", "70px"],["505px", "70px"],["300px", "70px"]];
	/*window.chipCoor = 
		[	[$("#chip0").css("left"),$("#chip0").css("top")],
			[$("#chip1").css("left"),$("#chip1").css("top")],
			[$("#chip2").css("left"),$("#chip2").css("top")],
			[$("#chip3").css("left"),$("#chip3").css("top")],
			[$("#chip4").css("left"),$("#chip4").css("top")]
		];//left,top
	*/
	/*window.SeatList = [
	//carry_chips();
		SeatObj(0,"#seat0",0),
		SeatObj(0,"#seat1",1),
		SeatObj(0,"#seat2",2),
		SeatObj(0,"#seat3",3),
		SeatObj(0,"#seat4",4)
	];*/
	seatInit();

	/*for(var i = 0; i < 5; i++) { 
			$("#chip" + i).hide();
	}//hide the chip first*/

	//carry_stakes();

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
				console.log(data.room.seats);
				for(var i = 0; i < data.room.seats.length; i++ ) {
					if(i < SeatList.length){
						if(data.room.seats[i] == null ) {							
							SeatList[i].setIsSat(0);							
						}
						else {
							SeatList[i].sit(data.room.seats[i].user,
									data.room.seats[i].player_stake);
						}
					}
				}
				console.log(SeatList);


				window.room_info = {};
				window.room_info.max_stake = data.room.max_stake;
				window.room_info.min_stake = data.room.min_stake;
				window.room_info.blind 	   = data.room.blind;
				window.room_info.timestamp = data.room.timestamp;


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
		if(seatObj.getIsSat() == 0)
		{
			sit_dialog.show(seatObj);
		}
		else {
			console.log(seatObj.getIsSat());
			//customer information
			alert("[IsSat == 1] Customer Information!");
		}
	});
};


/*var set_card = function(card, cardDivId) {
	var _suit;
	var _rank;

	console.log(card);
	if (card.length == 2) {
		_suit = card.charAt(1);
		_rank = card.charAt(0);
	}
	if (card.length == 3) {
		_suit = card.charAt(2);
		_rank = "10";
	}
	if (card.length != 2 && card.length != 3) {
		console.log("ERROR!!!");
		return;
	}
	console.log(_suit + " " + _rank);
	$(cardDivId)[0].src = poker_lib.getCard(_suit, _rank);
};*/

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
	//.appendTo($("#send_cards"));
	/*
	$("#chip" + _id).show();
	$("#chip" + _id).animate( 
		{
			left: chipCoor[SeatList[_id].pos][0],
			top: chipCoor[SeatList[_id].pos][1]
		},
		{
			duration: 'slow',
			complete: function() {
				if(callback) { callback(); }
			}
		}
	);
	*/
	$("#tstake" + chipId).html(tstake);
	
};

/*  ctPos is number */
var time_bar = function(ctPos) {
	SeatList[ctPos].setCountdown(ctPos);
	
};

//boardmsg.js--->>>msg_next()   //send call chips, change tstake collect chips and deal 3 PC
/*var roundone = function(seatNum, callStake) {
	//console.log(parseInt($("#tstake" + seatNum).html()) + parseInt(callStake));
	$("#money" + seatNum).html(parseInt($("#money" + seatNum).html()) - parseInt(callStake));
	$("#tstake" + seatNum).html(parseInt($("#tstake" + seatNum).html()) + parseInt(callStake));
};*/

var collect_chips = function() {
	for(var i = 0; i <= 4; i++) {
		if($("#tstake" + i).html() != "0") {
			$("#chip" + i ).animate(
				{
					left: "750px",
					top: "180px"
				},
				{
					duration: "5000"
				}
			);
		}
	}
};

var roundOne = function() {
	$("#card0").fadeIn("fast", function() {
		$("#card1").fadeIn("fast", function() {
			$("#card2").fadeIn("fast");
		});
	});
};
var roundTwo = function() {
	$("#card3").fadeIn("fast");	
};

var roundThree = function() {
	$("#card4").fadeIn("fast");
};

var btCallFun = function() {
	$("#btCall").click(function() {
			//console.log(data.amount_limits[2]);
			//roundone(data.seat_no, data.amount_limits[2]);
			var message = { action: 2 };
			var msg = JSON.stringify(message);
			console.log(msg);
			$.ajax({
				type:'post',
				url:"/post-board-message",
				data:{message:msg},
				success:function(data){
					console.log("######################");
					console.log(data);
					//collect_chips();
					//roundone(data.seat_no, data.amount_limits[2]);
					//window.flag = 1;
				},
				dataType:'json'
				}
			);
			//if(callback) { callback(); }
	});
	
};




			
			
