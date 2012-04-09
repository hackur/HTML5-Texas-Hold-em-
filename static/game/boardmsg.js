
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

	set_hand_cards(data.cards[0], data.cards[1]);

	dealCard.set_hc(['#cards_in_hand1','#cards_in_hand2']);

/*
	dealCard.deal(window.user_info.sit_no,
				["#cards_in_hand1","#cards_in_hand2"]);
	*/
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
	console.log("msg_action=====================================");
	console.log(data);
	var _s_b;
	var _b_b;
	if(data.action == 7) {
		_s_b = data.seat_no;
		document.getElementById("money" + _s_b).innerHTML = data.stake;
		send_chips(_s_b);
		console.log("_s_b is : " + _s_b);
	}
	if(data.action == 6) {
		_b_b = data.seat_no;
		document.getElementById("money" + _b_b).innerHTML = data.stake;
		send_chips(_b_b);
		console.log("_b_b is : " + _b_b);
	}
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
