
(function(board_msg_handler,$){
/**
 * MSG Type: (in game_room.py)
 *
(MSG_SIT,MSG_BHC,MSG_PHC,MSG_WINNER,MSG_NEXT,MSG_ACTION,MSG_PUBLIC_CARD) \
				= ('sit','bhc','phc','winner','next','action','public')
 *
 */
var div1 = [];
var div2 = [];
function msg_sit(data){
	/** Someone sat down
	 *
	 **/
	var seatID = data.seat_no;
	var username = data.info.user;
	var stake = data.info.player_stake;
	var userid = data.info.uid;
	var public_card = [];
	var div_winbg;
	SeatList[seatID].sit(username,stake,userid);
	if(username == window.user_info.username){
		window.user_info.sit_no = seatID;
	}
	$("#seatbg" + seatID).css("display", "none");
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
	console.log("WINNER!");
	console.log(data);
	$.each(data,function(userid,info){
		console.log(info);
		if(info.isWin == undefined){
			return;
		}
		var seat = getSeatById(userid);
		console.log([userid, seat,info.seat_no,"+++++++++++++"]);
		div1.push("#last_card" + info.seat_no + "1");
		div2.push("#last_card" + info.seat_no + "2");
		seat.setStake(info.stake,0);
		if(info.isWin){
			$.each(info.pot,function(index,pid){
				pot_manager.distribute(userid,pid);
			});
			div_winbg = "#winbg" + info.seat_no;
			$(div_winbg).css("display","block");
		}
	console.log([public_card, info.handcards, "------------------------------"]);
	for (var i = 0, k = 0;  i <= info.handcards.length - 1 && k <= 1; i++) {
		for (var j = 0; j <= public_card.length - 1; j++) {
			if (info.handcards[i] == public_card[j]) {
				break;
			} else if (j == public_card.length - 1) {
				console.log([info.handcards[i], "++++++++++++++++++++++++"]);
				if (k == 0) {
					poker_lib.setCard(info.handcards[i], div1[div1.length - 1]);
					$(div1[div1.length - 1]).css("display","block");
					k++;
				} else {
					poker_lib.setCard(info.handcards[i], div2[div2.length - 1]);
					$(div2[div2.length - 1]).css("display","block");
					k++;
				}
			}
		}
	}
	$.each(seat.getChips(),function(index,chip){
		console.log("removing");
		console.log(chip);
		chip.remove();
	});
		seat.cleanChips();
	});

	$.each(SeatList,function(index,seat){
		$.each(seat.getChips(),function(index,chip){
			console.log("removing");
			console.log(chip);
			chip.remove();
		});
		seat.cleanChips();
		seat.clearStake();
	});

	setTimeout(function(){
		while(div1.length > 0) {
			$(div1.pop()).removeAttr("style");
			$(div2.pop()).removeAttr("style");
		} 
		$(div_winbg).removeAttr("style");
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
	 public_card = data.cards;
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
