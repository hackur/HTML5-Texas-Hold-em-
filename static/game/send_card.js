
(function(dealCard,$){
	var back_cards = [];
	var playerHC  = [];


	function _deal(seat_no,degree, finishCallback){

		var seat = SeatList[seat_no];
		var backCard = $('<img class="backcard" src="./pokers/back.png" />').appendTo($("#container"));

		var seatOffset = window.SeatList[seat.pos].getSeatDIV().offset();
		var containerOffset = $("#container").offset();
		var cur_cardpos = {};
		cur_cardpos.left = seatOffset.left - containerOffset.left; 
		cur_cardpos.top = seatOffset.top - containerOffset.top; 

		var nextcard = function(){
			if(seat.userid == user_info.id){
				var cid = playerHC.pop();
				console.log(cid);
				backCard.remove();
				$(cid).fadeIn("fast");
				$("#cards_in_hand1").fadeIn();
				$("#cards_in_hand2").fadeIn();
			}
		};

		send_back_card(cur_cardpos.left, cur_cardpos.top, degree,backCard, nextcard);
		back_cards.push(backCard);

	};
	function deal(seat_list){
		var timeOut = 0;
		$.each(seat_list,function(index,seat){
			setTimeout(function(){
			_deal(seat,10);
			},timeOut += 200);
		});
		$.each(seat_list,function(index,seat){
			setTimeout(function(){
			_deal(seat,-10);
			},timeOut += 200);
		});
	};
	function set_hc(hc){
		playerHC = hc;
	}
	function send_back_card(left_cor, top_cor, degree, card, callback) {
		setTimeout(function(){
		var i = 0;
		degree = degree + 720;
		if(callback){
			card.bind("webkitTransitionEnd",callback);
			card.bind("transitionend",callback);
			card.bind("MSTransitionEnd",callback);
			card.bind("oTransitionEnd",callback);
		}
		card.css({'top': top_cor + 100,'left': left_cor + 100});
		card.css("-moz-transform", "rotate(" + degree + "deg)" );
		card.css("-webkit-transform", "rotate(" + degree + "deg)" );
		card.css("-ms-transform", "rotate(" + degree + "deg)" );
		card.css("-o-transform", "rotate(" + degree + "deg)" );
		card.css("transform", "rotate(" + degree + "deg)" );

		},1);
		return;

	};
	function clear(){
		$.each(back_cards,function(index,card){
			card.remove();
		});
	};
	function send_public_card(cards) {
		 var _cards = ["#card0","#card1","#card2","#card3","#card4"];

		 for(var i = 0; i < cards.length; i++){
			if($(_cards[i]).is(":visible") == false){
		 		poker_lib.setCard(cards[i], _cards[i]);
				$(_cards[i]).fadeIn("fast");
			}
		 }
	};
	dealCard.deal = deal;
	dealCard.clear = clear;
	dealCard.set_hc = set_hc;
	dealCard.send_public_card = send_public_card;

}(window.dealCard = window.dealCard || {} ,jQuery));
