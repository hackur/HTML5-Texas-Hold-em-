
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
	SeatList[seatID].sit(username,stake);
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
	dealCard.deal(data.seat_list);
}
function msg_phc(data){ 
	//Private message: you got hand card
	console.log("msg_phc is ----------------------------------------------:");
	console.log(data);
	console.log(data.cards[0] + "  " + data.cards[1]);
	var _suit1;
	var _rank1;
	var _suit2;
	var _rank2;
	
	if(data.cards[0].length == 2) {
		_suit1 = data.cards[0].charAt(1);
		_rank1 = data.cards[0].charAt(0);
	}
	else if(data.cards[0].length == 3){
		_suit1 = data.cards[0].charAt(2);
		_rank1 = "10";
	}
	
	if(data.cards[1].length == 2) {
		_suit2 = data.cards[1].charAt(1);
		_rank2 = data.cards[1].charAt(0);
	}
	else if(data.cards[1].length == 3) {
		_suit2 = data.cards[1].charAt(2);
		_rank2 = "10";
	}

	console.log(_suit1 + " " + _rank1);
	console.log(_suit2 + " " + _rank2);
	$('#cards_in_hand1')[0].src = poker_lib.getCard(_suit1, _rank1);
	$('#cards_in_hand2')[0].src = poker_lib.getCard(_suit2, _rank2);
	dealCard.set_hc(['#cards_in_hand1','#cards_in_hand2']);

/*
	dealCard.deal(window.user_info.sit_no,
				["#cards_in_hand1","#cards_in_hand2"]);
	*/
	//actionButton.enable_buttons();
}
function msg_winner(data){
	//We have a winner in this game
}
function msg_next(data){
	/**
	 * Telling who is the next person should make decision 
	 * Rights ( whether user can  call, check,...) will included
	 * Also amount limits is included ( How much user can put in action)
	 * */
	 console.log("msg_next=========================================");
	console.log(data);
	actionButton.enable_buttons(data.rights);
}
function msg_action(data){
	/***
	 * Some one did an action,
	 * Also, this one can be current user
	 * */
}
function msg_public_card(data){
	/***
	 * Public cards is updated
	 * */
}
function msg_start_game(data){
	
}
var funs = {
	'sit':		msg_sit,
	'bhc':		msg_bhc,
	'phc':		msg_phc,
	'winner':	msg_winner,
	'next':		msg_next,
	'action':	msg_action,
	'public':	msg_public_card,
	'start':    msg_start_game
};

function _board_msg_handler(data){
	
	funs[data.msgType](data);
}
board_msg_handler.process = _board_msg_handler;

}(window.board_msg_handler = window.board_msg_handler || {} ,jQuery));
