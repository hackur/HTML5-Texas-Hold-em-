


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
	window.cardpos = [undefined,["665px","335px"],["710px", "70px"],["505px", "70px"],["300px", "70px"]];

	window.SeatList = [
	//carry_chips();
		SeatObj(0,"#seat0",0),
		SeatObj(0,"#seat1",1),
		SeatObj(0,"#seat2",2),
		SeatObj(0,"#seat3",3),
		SeatObj(0,"#seat4",4)
	];

	for(var i = 0; i < 5; i++) { 
			$("#chip" + i).hide();
	}//hide the chip first

	//carry_stakes();

	actionButton.disable_all();

	console.log(username);

	$.each(SeatList,function(index,seat){
		take_place(seat.id, seat);
	});
	
	//game_control.deal();
};


var carry_stakes = function() {
	document.getElementById("carry_stakes_view").style.display = "block";
	$(function() {
		$("#slider").slider({
			value: 200,
			min: 0,
			max: 500,
			step: 50,
			slide: function(event, ui) {
				$("#amount").val("$" + ui.value);
			}
		});
		$("#amount").val("$" + $("#slider").slider("value"));
	});
	$("#submitButton").click(function() {
		//console.log($("#amount")[0].value);
		window.carry_stake = $("#amount")[0].value;
		document.getElementById("carry_stakes_view").style.display = "none";
	});
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
		},
		'json'
	);
};
var enter = function(){
	console.log("enter success!");
	var room = 1;
	$.post(
		"/enter",
		{room_id:room},
		function(data){
			console.log("Below is enter data:");
			console.log(data);
			if( data.status == "success" ) {
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
				console.log("data[i] ++++++++++");
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
			/*
			//console.log(seatID.slice(-1));
			var id = seatID.slice(-1);
			var stake = carry_stake.substring(1, carry_stake.length);
			//console.log(stake);
			$.ajax({
				type: "post",
				url: "/sit-down",
				data: {seat: id, stake: stake},
				success: function(data) {
					console.log("Below is sit-down data:");
					console.log(data);
					if(data.status != "success"){

					}
				},
				dataType: "json"
			});
			seatObj.setIsSat(1);
			send_first_card();
			//sit_transit(id);
			*/
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
							console.log("PPPPPPPPPPPPPPPPPPPPPPPPP");
							console.log(SeatList);
							$('#cards_in_hand1').fadeIn("fast", function() {
								var j = 1;
								for(i = first_seat_no ,count = 0; count < SeatList.length ; count++, i = i +1 % SeatList.length){
									var seat = SeatList[i];
									if(seat.username == window.username || seat.getIsSat() == 0){
										return;
									}
									console.log(seat);
									console.log(seat.username);
									console.log(window.username);
									console.log(cardpos);
									console.log(seat.pos);
									var cur_cardpos = cardpos[seat.pos];
									send_back_card(cur_cardpos[0], cur_cardpos[1], "10", "#backshadow" + j+ "_1", undefined);
									j++;
								}
						
								/*
								if(SeatList[4].getIsSat() == 1 ) {
									
								}
								if(SeatList[3].getIsSat() == 1 ) {
									send_back_card("505px", "70px", "10", "#backshadow2_1", undefined);
								}
								if(SeatList[2].getIsSat() == 1 ) {
									send_back_card("710px", "70px", "10", "#backshadow3_1", undefined);
								}								
								if(SeatList[1].getIsSat() == 1) {
									send_back_card("665px", "335px", "10", "#backshadow4_1", undefined);
								}
								send_second_card();
								*/
								/*send_back_card("300px", "70px", "10", "#backshadow1", undefined);
								send_back_card("505px", "70px", "10", "#backshadow2", undefined);
								send_back_card("710px", "70px", "10", "#backshadow3", undefined);
								send_back_card("665px", "335px", "10", "#backshadow4", function() {
									send_second_card();
								});*/
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




			
			
