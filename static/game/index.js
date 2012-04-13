


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
	window.chipCoor = 
		[	[$("#chip0").css("left"),$("#chip0").css("top")],
			[$("#chip1").css("left"),$("#chip1").css("top")],
			[$("#chip2").css("left"),$("#chip2").css("top")],
			[$("#chip3").css("left"),$("#chip3").css("top")],
			[$("#chip4").css("left"),$("#chip4").css("top")]
		];//left,top
	window.SeatList = [
	//carry_chips();
		SeatObj(0,"#seat0",0),
		SeatObj(0,"#seat1",1),
		SeatObj(0,"#seat2",2),
		SeatObj(0,"#seat3",3),
		SeatObj(0,"#seat4",4)
	];

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
				console.log(data[i]);
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
	$(seatID).click(function() {
		if(seatObj.getIsSat() == 0)
		{
			sit_dialog.show(seatID);
		}
		else {
			console.log(seatObj.getIsSat());
			//customer information
			alert("[IsSat == 1] Customer Information!");
		}
	});
};

var SeatObj = function(IsSat,id,pos) {
	var seatObj = {};
	seatObj.IsSat = IsSat;

	seatObj.getIsSat = function() {
		return seatObj.IsSat;
	};
	seatObj.setIsSat = function(newIsSat) {
		seatObj.IsSat = newIsSat;
	};
	seatObj.sit = function(_username,_stake) {	
		seatObj.username 	= _username;
		seatObj.stake 		= _stake;
		document.getElementById("name" + id.slice(-1)).innerHTML = _username
		document.getElementById("money" + id.slice(-1)).innerHTML = _stake;
		seatObj.setIsSat(1);
	};
	seatObj.setStake = function(seat_no, newstake) {
		document.getElementById("money" + seat_no).innerHTML = newstake;
	}

	seatObj.id = id;
	seatObj.pos = pos;

	return seatObj;
};

var send_first_card = function(first_seat_no) {
		var i = 0;
		$('#backpng1').animate(
		{
			"left": "-=60px", 
			"top": "+=240px",
			 width: "84px",
			 height: "116px"
		}, 
		{
			duration: "fast", 
			step: function() {
				i++;
				$("#backpng1").css("transform", "rotate(" + i + "deg)");
	            $("#backpng1").css("-moz-transform", "rotate(" + i + "deg)");
	            $("#backpng1").css("-webkit-transform", "rotate(" + i + "deg)");
	            $("#backpng1").css("-ms-transform", "rotate(" + i + "deg)");
	            $("#backpng1").css("-o-transform", "rotate(" + i + "deg)");
			},
			complete: function() {
				$("#backpng1").rotate3Di(90, "fast", 
					{
						complete: function() {
							console.log("Below is SeatList: ");
							console.log(SeatList);
							$('#cards_in_hand1').fadeIn("fast", function() {
								var j = 1;
								for(i = first_seat_no ,count = 0; count < SeatList.length ; count++, i = i +1 % SeatList.length){
									var seat = SeatList[i];
									if(seat.username == window.user_info.username || seat.getIsSat() == 0){
										return;
									}
									console.log(seat);
									console.log(seat.username);
									console.log(window.user_info.username);
									console.log(cardpos);
									console.log(seat.pos);
									var cur_cardpos = cardpos[seat.pos];
									send_back_card(cur_cardpos[0], cur_cardpos[1], "10", "#backshadow" + j+ "_1", undefined);
									j++;
								}
							});						
						}
					}
				);				
			}
		});
};

var send_second_card = function() {
		// send two cards to everyone  
		var i = 0;
		$('#backpng2').animate(
		{
			"left": "-=30px", 
			"top": "+=240px",
			width: "84px",
			height: "116px"
		}, 
		{
			duration: "fast", 
			step: function() {
				i++;
				$("#backpng2").css("-moz-transform", "rotate(" + i + "deg)" );
				$("#backpng2").css("-webkit-transform", "rotate(" + i + "deg)" );
				$("#backpng2").css("-ms-transform", "rotate(" + i + "deg)" );
				$("#backpng2").css("-o-transform", "rotate(" + i + "deg)" );
				$("#backpng2").css("transform", "rotate(" + i + "deg)" );
			},
			complete: function() {
				$("#backpng2").rotate3Di(90, "fast", 
					{
						complete: function() {
							$('#cards_in_hand2').fadeIn("fast", function() {
								/*send_back_card("300px", "70px", "-10", "#backshadow1", undefined);
								send_back_card("505px", "70px", "-10", "#backshadow2", undefined);
								send_back_card("710px", "70px", "-10", "#backshadow3", undefined);
								send_back_card("665px", "335px", "-10", "#backshadow4", undefined);*/
								if(SeatList[4].getIsSat() == 1 ) {
									send_back_card("300px", "70px", "-10", "#backshadow1", undefined);
								}
								if(SeatList[3].getIsSat() == 1 ) {
									send_back_card("505px", "70px", "-10", "#backshadow2", undefined);
								}
								if(SeatList[2].getIsSat() == 1 ) {
									send_back_card("710px", "70px", "-10", "#backshadow3", undefined);
								}								
								if(SeatList[1].getIsSat() == 1) {
									send_back_card("665px", "335px", "-10", "#backshadow4", undefined);
								}
							});
						}
					}
				);
			}
		});
};

var send_back_card = function(left_cor, top_cor, degree, id, callback) {
	var i = 0;
	$("#back").animate(
		{
			left: left_cor,
			top:  top_cor,
			width: "30px",
			height: "41px"
		}, 
		{
			duration: "normal",
			step: function() {
				i++;
				$("#back").css("-moz-transform", "rotate(" + i + "deg)" );
				$("#back").css("-webkit-transform", "rotate(" + i + "deg)" );
				$("#back").css("-ms-transform", "rotate(" + i + "deg)" );
				$("#back").css("-o-transform", "rotate(" + i + "deg)" );
				$("#back").css("transform", "rotate(" + i + "deg)" );
			},
			complete: function() {
				//set '#backshadow' the same with '#back' and display it...   width and height depand on ratio
				$(id).css({'top': top_cor,'left': left_cor,'width': '30px','height': '41px'});

				$(id).css("-moz-transform", "rotate(" + degree + "deg)" );
				$(id).css("-webkit-transform", "rotate(" + degree + "deg)" );
				$(id).css("-ms-transform", "rotate(" + degree + "deg)" );
				$(id).css("-o-transform", "rotate(" + degree + "deg)" );
				$(id).css("transform", "rotate(" + degree + "deg)" );
				//reset '#back'
				$("#back").css({'top': '120px', 'left': '450px', 'width': '0px', 'height': '0px'});

				if(callback)
				{
					callback();
				}

			}
		}
	);
};

var set_hand_cards = function(card0, card1) {
	var _suit1;
	var _rank1;
	var _suit2;
	var _rank2;
	
	if(card0.length == 2) {
		_suit1 = card0.charAt(1);
		_rank1 = card0.charAt(0);
	}
	if(card0.length == 3){
		_suit1 = card0.charAt(2);
		_rank1 = "10";
	}
	if(card1.length == 2) {
		_suit2 = card1.charAt(1);
		_rank2 = card1.charAt(0);
	}
	if(card1.length == 3) {
		_suit2 = card1.charAt(2);
		_rank2 = "10";
	}

	console.log(_suit1 + " " + _rank1);
	console.log(_suit2 + " " + _rank2);
	$('#cards_in_hand1')[0].src = poker_lib.getCard(_suit1, _rank1);
	$('#cards_in_hand2')[0].src = poker_lib.getCard(_suit2, _rank2);	
};

var send_chips = function(chipId, tstake, callback) {
	var _id = chipId;
	

	console.log("*************************");
	/*console.log($("#seat" + _id).css("left"));
	console.log($("#seat" + _id).css("top"));*/
	/*console.log(chipCoor[SeatList[_id].pos]);
	console.log($("#seat" + _id).css("width"));
	console.log($("#seat" + _id).css("left"));
	console.log($("#seat" + _id).css("top"));
	console.log( ($("#seat" + _id).css("left").substring(0, $("#seat" + _id).css("left").length - 2 )/1 
					+ $("#seat" + _id).css("width").substring(0, $("#seat" + _id).css("width").length - 2 )/2) + "px");
	console.log( $("#seat" + _id).css("width").substring(0, $("#seat" + _id).css("width").length - 2 )/1 );
	console.log($("#seat" + _id).css("top") + $("#seat" + _id).css("height")/2 );
*/

	//set the chips original top and left 
	$("#chip" + _id).css({
		left: ($("#seat" + _id).css("left").substring(0, $("#seat" + _id).css("left").length - 2 )/1 
					+ $("#seat" + _id).css("width").substring(0, $("#seat" + _id).css("width").length - 2 )/2) + "px",
		top: ($("#seat" + _id).css("top").substring(0, $("#seat" + _id).css("top").length - 2 )/1 
					+ $("#seat" + _id).css("height").substring(0, $("#seat" + _id).css("height").length - 2 )/2) + "px"
	});

	//show it and animate
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
	$("#tstake" + chipId).html(tstake);
	
};

/*  countdownID is number */
var time_bar = function(countdownID) {
	$("#countdown" + countdownID).addClass("countdown");
	$("#countdown" + countdownID).animate({	width: 0}, 30000, function() {
				$("#countdown" + countdownID).removeClass("countdown");
				$("#countdown" + countdownID).removeAttr("style");
			}
	);
};

//boardmsg.js--->>>msg_next()   //send call chips, change tstake collect chips and deal 3 PC
var roundone = function(seatNum, callStake) {
	//console.log(parseInt($("#tstake" + seatNum).html()) + parseInt(callStake));
	$("#money" + seatNum).html(parseInt($("#money" + seatNum).html()) - parseInt(callStake));
	$("#tstake" + seatNum).html(parseInt($("#tstake" + seatNum).html()) + parseInt(callStake));
};

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

var testFun = function() {
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
					window.flag = 1;
				},
				dataType:'json'
				}
			);
			//if(callback) { callback(); }
	});
	
};




			
			
