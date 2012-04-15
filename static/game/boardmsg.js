
(function(board_msg_handler,$){
/**
 * MSG Type: (in game_room.py)
 *
(MSG_SIT,MSG_BHC,MSG_PHC,MSG_WINNER,MSG_NEXT,MSG_ACTION,MSG_PUBLIC_CARD) \
				= ('sit','bhc','phc','winner','next','action','public')
 *
 */
function msg_sit(data){
	/** Someone sat down
	 *
	 **/
	var seatID = data.seat_no;
	var username = data.info.user;
	var stake = data.info.player_stake;
	var userid = data.info.uid;
	SeatList[seatID].sit(username,stake,userid);
	if(username == window.user_info.username){
		window.user_info.sit_no = seatID;
	}
}
function msg_bhc(data){ 
	/*
	 * Broadcast some one got hand card
	 * The "some one" may be you. Message should
	 * be ignored in that case
	 * */
	console.log("msg_bhc =================================");
	console.log(data);
	dealCard.deal(data.seat_list);
}
function msg_phc(data){ 
	//Private message: you got hand card
	console.log("msg_phc is ----------------------------------------------:");
	console.log(data);

	//set_hand_cards(data.cards[0], data.cards[1]);
	poker_lib.setCard(data.cards[0], '#cards_in_hand1');
	poker_lib.setCard(data.cards[1], '#cards_in_hand2');

	dealCard.set_hc(['#cards_in_hand1','#cards_in_hand2']);

/*
	dealCard.deal(window.user_info.sit_no,
				["#cards_in_hand1","#cards_in_hand2"]);
	*/
}
function msg_winner(data){
	//We have a winner in this game
	message_box.showMessage("We have a winner! ",5)
	$.each(data,function(userid,info){
		console.log(info);
		if(info.isWin == undefined){
			return;
		}
		var seat = getSeatById(userid);
		if(info.isWin){
			seat.setStake(info.stake,0);
			$.each(info.pot,function(index,pid){
				pot_manager.distribute(userid,pid);
			});
		}
		else{
			seat.setStake(info.stake,0);
			$.each(seat.getChips(),function(index,chip){
				chip.remove();
			});
			seat.cleanChips();
		}
	});
	setTimeout(function(){
		pot_manager.reset();
	 	var cards = ["#card0","#card1","#card2","#card3","#card4"];
		 for(var i = 0; i < cards.length; i++){
			$(cards[i]).fadeOut("fast");
		 }
		$("#cards_in_hand1").fadeOut("fast");
		$("#cards_in_hand2").fadeOut("fast");
	},2500);
}
function msg_next(data){
	/**
	 * Telling who is the next person should make decision 
	 * Rights ( whether user can  call, check,...) will included
	 * Also amount limits is included ( How much user can put in action)
	 * */
	console.log("msg_next=========================================");
	console.log(data);
	//time_bar(data.seat_no);
	SeatList[data.seat_no].setCountdown(data.seat_no);

	console.log(window.user_info.username);
	console.log(SeatList[data.seat_no].username);
	if( SeatList[data.seat_no].username == window.user_info.username )
	{ 
		actionButton.enable_buttons(data.rights,data.amount_limits);
	}
	//collect_chips();
}
function msg_action(data){
	/***
	 * Some one did an action,
	 * Also, this one can be current user
	 * */
	console.log("msg_action=====================================");
	console.log(data);
	//*document.getElementById("money" + data.seat_no).innerHTML = data.stake;*/
	SeatList[data.seat_no].setStake(data.stake,data.table);
	SeatList[data.seat_no].removeCountdown(data.seat_no);
	//send_chips(data.seat_no, data.table);

}
function msg_public_card(data){
	/***
	 * Public cards is updated
	 * */
	 console.log("msg_public_card ==================================");
	 console.log(data);
	 
	 
	 dealCard.send_public_card(data.cards);

}
function msg_start_game(data){
	console.log("msg_start_game================================");
	console.log(data);
	var seconds = parseInt(data.to);
	var contentDIV = window.message_box.showMessage("",seconds);

	var countDown = function(){
		contentDIV.html(
				"Game start in " +  seconds + " seconds");
		if(seconds > 0){
			setTimeout(countDown,1000);
		}
		seconds--;
	};
	countDown();
	
}
function msg_pot(data){
	pot_manager.update(data.pot);
}
function msg_standup(data){
	console.log("Stand up");
	console.log(data);
}
var funs = {
	'sit':		msg_sit,
	'bhc':		msg_bhc,
	'phc':		msg_phc,
	'winner':	msg_winner,
	'next':		msg_next,
	'action':	msg_action,
	'public':	msg_public_card,
	'start':    msg_start_game,
	'pot':  	msg_pot,
	'standup':	msg_standup
};

function _board_msg_handler(data){
	
	funs[data.msgType](data);
}
board_msg_handler.process = _board_msg_handler;

}(window.board_msg_handler = window.board_msg_handler || {} ,jQuery));
