
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
}
function msg_next(data){
	/**
	 * Telling who is the next person should make decision 
	 * Rights ( whether user can  call, check,...) will included
	 * Also amount limits is included ( How much user can put in action)
	 * */
	console.log("msg_next=========================================");
	console.log(data);

	//window.flag = 0;
	//should be called after dealed card
	time_bar(data.seat_no);
	//if($("#name" + data.seat_no).html())
	//console.log($("#name" + data.seat_no).html());
	console.log(window.user_info.username);
	console.log(SeatList[data.seat_no].username);
	if( SeatList[data.seat_no].username == window.user_info.username )
	{ 
		actionButton.enable_buttons(data.rights,data.amount_limits);
		//console.log("yes, match!");
		//game_control.deal();
		//btCallFun();
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
	//send_chips(data.seat_no, data.table);

/*
	$('#btCheck').click(function(){
		var message = { action: 4 };
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
	});	
	*/
}
function msg_public_card(data){
	/***
	 * Public cards is updated
	 * */
	 console.log("msg_public_card ==================================");
	 console.log(data);
	 poker_lib.setCard(data.cards[0], '#card0');
	 poker_lib.setCard(data.cards[1], '#card1');
	 poker_lib.setCard(data.cards[2], '#card2');
	 poker_lib.setCard(data.cards[3], '#card3');
	 poker_lib.setCard(data.cards[4], '#card4');
}
function msg_start_game(data){
	console.log("msg_start_game================================");
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
	'start':    msg_start_game
};

function _board_msg_handler(data){
	
	funs[data.msgType](data);
}
board_msg_handler.process = _board_msg_handler;

}(window.board_msg_handler = window.board_msg_handler || {} ,jQuery));
