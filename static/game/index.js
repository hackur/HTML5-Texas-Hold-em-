var table_init = function() {
	decide_event();

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
				listenBoardMessage();
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
		if(!seatObj.getIsSat() && !window.user_info.userIsSat){

			console.log(seatObj);
			console.log(this);
			console.log("sliderbaris clicked");
			$.mobile.showPageLoadingMsg();
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
					$.mobile.hidePageLoadingMsg()
					sit_down_dialog.show(seatObj);
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
			console.log(".............");
			console.log(seatObj.player);
			for (key in seatObj.player) {
				if (seatObj.player[key] == undefined) {
					seatObj.player[key] = "N/A";
				}
			}
			seatObj.player.show(seatObj.player);
			var info_hide = function(e) {
				var infoWindow = $("#player-info-content");
				var infoWindowPosition = infoWindow.offset();
				var infoWindowSize = {"width": infoWindow.width(), "height": infoWindow.height()};
				pos = get_event_position(e);
				console.log(infoWindowSize["width"]);
				console.log(pos[0]);
				if(pos[0] < infoWindowPosition["left"] || pos[0] > infoWindowPosition["left"]+infoWindowSize["width"]) {
					console.log("I'm hiding my self!");
					seatObj.player.hide();	
					window.removeEventListener("click", info_hide, true);
				}
				e.stopPropagation();
			}
			window.addEventListener("click", info_hide, true);
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
