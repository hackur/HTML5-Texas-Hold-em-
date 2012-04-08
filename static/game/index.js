


var table_init = function() {
	document.ontouchmove = function(e) {
		e.preventDefault();
	};

	var SeatList = {
		seat0: SeatObj(0),
		seat1: SeatObj(0),
		seat2: SeatObj(0),
		seat3: SeatObj(0),
		seat4: SeatObj(0)
	};

	carry_chips();

	console.log(username);

	
	take_place("#seat0", SeatList.seat0);
	take_place("#seat1", SeatList.seat1);
	take_place("#seat3", SeatList.seat3);
	take_place("#seat2", SeatList.seat2);
	take_place("#seat4", SeatList.seat4);

	game_control.deal();
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
				listenBoardMessage();
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
				if( data[i].msgType == "sit") {
					//display name and shake
					var _seatID = data[i].seat_no;
					var _username = data[i].info.user;
					var _stake = data[i].info.player_stake;
					display_name_and_stake(_seatID, _username, _stake);
				}
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

var display_name_and_stake = function(seatID, username, stake) {
	document.getElementById("name" + seatID).innerHTML = username
	document.getElementById("money" + seatID).innerHTML = stake;
	sit_transit.transit(seatID);
}

var carry_chips = function() {
	document.getElementById("carry_chips_view").style.display = "block";
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
		document.getElementById("carry_chips_view").style.display = "none";
	});
};

var take_place = function(seatID, seatObj) {
	$(seatID).click(function() {
		if(seatObj.getIsSat() == 0)
		{
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
		}
		else {
			console.log(seatObj.getIsSat());
			//customer information
			alert("[IsSat == 1] Customer Information!");
		}
	});
};

var SeatObj = function(IsSat) {
	var seatObj = {};
	seatObj.IsSat = IsSat;

	seatObj.getIsSat = function() {
		return seatObj.IsSat;
	};
	seatObj.setIsSat = function(newIsSat) {
		seatObj.IsSat = newIsSat;
	};

	return seatObj;
};

var send_first_card = function() {
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
							/* should be modified to get cards from pokers lib */
							//console.log($('#cards_in_hand1')[0].src);
							//$('#cards_in_hand1')[0].src = poker_lib.getCard("S","5");

							$('#cards_in_hand1').fadeIn("fast", function() {
								send_back_card("300px", "70px", "10", "#backshadow1_1", undefined);
								send_back_card("505px", "70px", "10", "#backshadow2_1", undefined);
								send_back_card("710px", "70px", "10", "#backshadow3_1", undefined);
								send_back_card("665px", "335px", "10", "#backshadow4_1", function() {
									send_second_card();
								});
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
								send_back_card("300px", "70px", "-10", "#backshadow1", undefined);
								send_back_card("505px", "70px", "-10", "#backshadow2", undefined);
								send_back_card("710px", "70px", "-10", "#backshadow3", undefined);
								send_back_card("665px", "335px", "-10", "#backshadow4", undefined);
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






/*var sit_transit = function(sit) {
					var _seatID = ["#seat0","#seat1","#seat2","#seat3",
						"#seat4"];

					var transit_id = sit , transit_temp = -1;
					for (var i = transit_id; i < _seatID.length; i++) {
						transit(_seatID[++transit_temp], _seatID[i]);
					}
					for (var i = 0; i < transit_id; i++) {
						transit(_seatID[++transit_temp], _seatID[i]);
					}
			};

			var transit = function(transit_to, transit_from) {
				$(transit_from).transition({
					x: $(transit_to).position().left - $(transit_from).position().left,
					y: $(transit_to).position().top - $(transit_from).position().top,
					duration: 10000,
					rotate: 0,
					easing: 'snap'
				});
			};*/



			


			
			
