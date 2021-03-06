
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
	if( userid == window.user_info.id){
		window.user_info.sit_no = seatID;
		window.user_info.userIsSat = true;
		for (var i = 0; i < SeatList.length; i++) {
			SeatList[i].removeSeatdownbg();
		}
		SeatList[data.seat_no].showStand();
		window.chat_dialog.display();
	}
	SeatList[data.seat_no].removeSeatdownbg();
}
function msg_bhc(data){ 
	/*
	 * Broadcast some one got hand card
	 * The "some one" may be you. Message should
	 * be ignored in that case
	 * */
	dealCard.deal(data.seat_list);
	SeatList[parseInt(data.dealer)].showDealerBtn();
}
function msg_phc(data){ 
	//Private message: you got hand card
	var seatId = window.user_info.sit_no;
	//set_hand_cards(data.cards[0], data.cards[1]);
	poker_lib.setCard(data.cards[0], '#cards_in_hand1');
	poker_lib.setCard(data.cards[1], '#cards_in_hand2');
	//$("#cards_in_hand1").fadeIn();
	//$("#cards_in_hand2").fadeIn();
	SeatList[seatId].cards	= [];
	SeatList[seatId].cards.push(poker_lib.evaluateCard(data.cards[0]));
	SeatList[seatId].cards.push(poker_lib.evaluateCard(data.cards[1]));
	
	dealCard.set_hc(['#cards_in_hand1','#cards_in_hand2']);
/*
	dealCard.deal(window.user_info.sit_no,
				["#cards_in_hand1","#cards_in_hand2"]);
	*/
	/*
	console.log("checking ================");
	console.log(window.user_info)
	for (var i = 0; i < SeatList.length; i++) {
		console.log("i = "+i);
		console.log("is sit"+SeatList[i].getIsSat())
		if(window.user_info.userIsSat == true && window.user_info.sit_no == i){
			SeatList[i].hideBackCard();
		}
		else{
			if(SeatList[i].getIsSat() == true){
				SeatList[i].showBackCard();
			}
		}
	}
	*/
}
function msg_winner(data){
	//We have a winner in this game
	message_box.showMessage("We have a winner! ",3);
	for (var i = 0; i < SeatList.length; i++) {
		SeatList[i].hideBackCard();
	}
	actionButton.disable_all();
	actionButton.resetAutoButtons();
	actionButton.disable_AutoButtons();
	window.user_info.userIsPlay = false;
    function distribute(){
        /* We have to wait for while here 
         * Because we may still collecting coins
         * */
        $.each(data,function(userid,info){
            if(info.isWin == undefined){
                    return;
            }
            var seat = getSeatById(userid);
            if(info.isWin){
                $.each(info.pot,function(index,pid){
                    pot_manager.distribute(userid,pid);
                });
                SeatList[info.seat_no].showWinbg();
            }
        });
        $.each(SeatList,function(index,seat){
            $.each(seat.getChips(),function(index,chip){
                chip.remove();
            });
            seat.cleanChips();
            seat.clearStake();
			seat.removeDealerBtn();
        });
		pot_manager.reset();
    }
    setTimeout(distribute,1000);
	console.log("game finished===========+++++++++++++++++++++");
	console.log(data);
	
	$.each(data,function(userid,info){
		console.log(info)
		if(info.isWin == undefined){
			return;
		}
		var seat	= getSeatById(userid);
		seat.cards	= [];
		seat.setStake(info.stake,0);
		SeatList[info.seat_no].removeCountdown();
		
		if(info.handcards == undefined){
			return;
		}
		var cards	= [];
		for(var i=0;i<info.handcards.length;i++){
			cards.push(poker_lib.evaluateCard(info.handcards[i]));
		}
		if(info.isWin == false){
			seat.showCardName(cards);
		}else{
			seat.showWinCardName(cards);
		}
		console.log("check point");
        for (var i = 0, k = 0;  i <= info.handcards.length - 1 && k <= 1; i++) {
            for (var j = 0; j <= public_card.length - 1; j++) {
                if (info.handcards[i] == public_card[j]) {
                    break;
                } else if (j == public_card.length - 1) {
                    if (k == 0) {
                        SeatList[info.seat_no].setWinCard(info.handcards[i], 1);
                        k++;
                    } else {
                        SeatList[info.seat_no].setWinCard(info.handcards[i], 2);
                        k++;
                    }
                }
            }
        }
		SeatList[info.seat_no].showWinCard();
	});


	setTimeout(function(){
		//pot_manager.reset();
	 	var cards = ["#card0","#card1","#card2","#card3","#card4"];
		 for(var i = 0; i < cards.length; i++){
			$(cards[i]).fadeOut("fast");
		 }
		$("#cards_in_hand1").fadeOut("fast");
		$("#cards_in_hand2").fadeOut("fast");
		$(".card-name").remove();
		$(".card-name-win").remove();
		dealCard.clear();
		$.each(data,function(userid,info){
			if (info.seat_no != undefined) {
				SeatList[info.seat_no].removeCard();
			}
			if (info.isWin) {
				SeatList[info.seat_no].removeWinbg();
			}
		});
	},2500);
}
function msg_next(data){
	/**
	 * Telling who is the next person should make decision 
	 * Rights ( whether user can  call, check,...) will included
	 * Also amount limits is included ( How much user can put in action)
	 * */
	//time_bar(data.seat_no);
	SeatList[data.seat_no].setCountdown(data.to);

	if( SeatList[data.seat_no].userid == window.user_info.id )
	{ 
		if(window.user_info.userIsPlay){
			actionButton.disable_AutoButtons();
		}
		window.user_info.userIsPlay = true;
		actionButton.enable_buttons(data.rights,data.amount_limits);
	}
	else{
		actionButton.disable_all();
		if(window.user_info.userIsPlay){
			actionButton.enable_AutoButtons();
		}
	}
	//collect_chips();
}
function msg_action(data){
	/***
	 * Some one did an action,
	 * Also, this one can be current user
	 * */
	//*document.getElementById("money" + data.seat_no).innerHTML = data.stake;*/
	SeatList[data.seat_no].setStake(data.stake,data.table);
	SeatList[data.seat_no].showAction(actionName[(data.action).toString()],data.action)
	SeatList[data.seat_no].removeCountdown(data.seat_no);
	
	//send_chips(data.seat_no, data.table);
}
function msg_public_card(data){
	/***
	* Public cards is updated
	* */
	window.public_card = data.cards;
	dealCard.send_public_card(data.cards);
	if(window.user_info.userIsSat){
		var seatId	= window.user_info.sit_no;
		var cards	= []; 
		for(var i=0;i<data.cards.length;i++){
			cards.push(poker_lib.evaluateCard(data.cards[i]));
		}
		SeatList[seatId].showCardName(cards);
	}
}
function msg_start_game(data){
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
	if (window.user_info.userIsSat)
		window.user_info.userIsPlay = true;
	actionButton.disable_all();
	for (var i = 0; i < SeatList.length; i++) {
		SeatList[i].hideBackCard();
	}
}
function msg_pot(data){
	pot_manager.update(data.pot);
}
function msg_standup(data){
	console.log("standup Message");
	$.each(data,function(userid, info) {
		if (info.seat_no != undefined) {

			SeatList[info.seat_no].seatStand();
			SeatList[info.seat_no].removeCountdown();
			if (!window.user_info.userIsSat) {
				SeatList[info.seat_no].showSeatdownbg();
			}
			else if(parseInt(window.user_info.sit_no) == parseInt(info.seat_no)) {
				SeatList[info.seat_no].removeStand();
				
				for (var i = 0; i < 9; i++) {
					if (!SeatList[i].getIsSat()) {
						SeatList[i].showSeatdownbg();
					} 
				}
				window.user_info.userIsPlay = false;
				window.user_info.userIsSat = false;
				window.user_info.sit_no = undefined;
				actionButton.disable_all();
				actionButton.disable_AutoButtons();
				window.chat_dialog.hide();
			}
		}
	});
}
function msg_chat(data){
	chat_dialog.receive(data);
};
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
	'standup':	msg_standup,
	'chat':		msg_chat
};


function _board_msg_handler(data){
	if(funs[data.msgType])
		funs[data.msgType](data);
	else{
		console.log("NOT SUPPORTED");
		console.log(data);
	}
}
board_msg_handler.process = _board_msg_handler;

}(window.board_msg_handler = window.board_msg_handler || {} ,jQuery));
