
(function(dealCard,$){
	var back_cards = [];
	var playerHC  = [];


	function _deal(seat_list,degree, finishCallback){
		if(seat_list.length == 0){
			if(finishCallback){
				finishCallback();
			}
			return;
		}
		var seat_no = seat_list.shift();

		var seat = SeatList[seat_no];
		var backCard = $('<img class="backcard" src="./pokers/back.png" />').appendTo($("#send_cards"));

		//var cur_cardpos = window.cardpos[seat.pos];

		var nextcard = function(){
			if(seat.username == user_info.username){
				var cid = playerHC.pop();
				console.log(cid);
				backCard.remove();
				$(cid).fadeIn("fast");
			}
			_deal(seat_list,degree,finishCallback);
			/*
			if(seat.username == user_info.username ){
				var cid = playerHC.pop();
				console.log(cid);
				backCard.remove();
				$(cid).fadeIn("fast");
			}
			else{
				console.log([seat.getIsSat(),seat.username,user_info.username]);
			}
			if(count + 1 <  window.SeatList.length ){
				seat_no = (seat_no  + 1) % window.SeatList.length;
				_deal(seat_no,count +1,degree,finishCallback);
			}
			else{
				if(finishCallback){
					finishCallback();
				}
			}
			*/
		};

		//send_back_card(cur_cardpos[0], cur_cardpos[1], degree,backCard, nextcard);
		nextcard();
		back_cards.push(backCard);

	};
	function deal(seat_list){
		_deal(seat_list.slice(),"10",function(){
			_deal(seat_list.slice(),"-10");
		});
	};
	function set_hc(hc){
		playerHC = hc;
	}
	function send_back_card(left_cor, top_cor, degree, card, callback) {
		var i = 0;
		if(callback){
			callback();
				  }
				  return;
		card.animate({
			left: left_cor,
			top:  top_cor,
			width: "30px",
			height: "41px"
			}, 
			{
					duration: "normal",
			step: function() {
				i++;
				card.css("-moz-transform", "rotate(" + i + "deg)" );
				card.css("-webkit-transform", "rotate(" + i + "deg)" );
				card.css("-ms-transform", "rotate(" + i + "deg)" );
				card.css("-o-transform", "rotate(" + i + "deg)" );
				card.css("transform", "rotate(" + i + "deg)" );
			},
			complete: function() {
				  //set '#backshadow' the same with '#back' and display it...   width and height depand on ratio
				  card.css({'top': top_cor,'left': left_cor,'width': '30px','height': '41px'});
				  card.css("-moz-transform", "rotate(" + degree + "deg)" );
				  card.css("-webkit-transform", "rotate(" + degree + "deg)" );
				  card.css("-ms-transform", "rotate(" + degree + "deg)" );
				  card.css("-o-transform", "rotate(" + degree + "deg)" );
				  card.css("transform", "rotate(" + degree + "deg)" );
				  //reset '#back'
				  //card.css({'top': '120px', 'left': '450px', 'width': '0px', 'height': '0px'});

				  if(callback)
				  {
					  callback();
				  }

				}
			}
		);
	};
	function clear(){
		$.each(backCard,function(index,card){
			card.remove();
		});
	};
	dealCard.deal = deal;
	dealCard.clear = clear;
	dealCard.set_hc = set_hc;

}(window.dealCard = window.dealCard || {} ,jQuery));
