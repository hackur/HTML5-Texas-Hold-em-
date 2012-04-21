
function Seat(id,pos){
	var seatObj = {};
		/*
		<div id="seat0" class="seat seatPos0">
			<div class="chip">
				<div id="tstake0" class="tstake">0</div>
			</div>
			<div id="name0" class="name">name</div>
			<div id="money0" class="money">money</div>
			<div id="countdown0"></div>
		</div>
		*/
	console.log([id,pos,"-------------------------!!!!!!!!!"]);
	var divSeat = $('<div class="seat"></div>');
	var divSeatbg = $('<div class="seatbg"></div>');
	var divSeatdownbg = $('<div class="countdown win seat_dowm_bg"></div>');
	var divName = $('<div class="name">name</div>');
	var divMoney = $('<div class="money">money</div>');
	var divCountdown = $('<div class="countdown"></div>');
	var divCount = $('<div class="countdown down"></div>');
	var divWinbg = $('<div class="winbg"></div>')
	var divWin = $('<div class="countdown win"></div>');
	var divWin_last_card01 = $('<img class="countdown win card01" src="./pokers/club/A.png">');
	var divWin_last_card02 = $('<img class="countdown win card02" src="./pokers/club/A.png">');
	var divChip = $('<div class="chip"> </div>');
	var divStake = $('<div class="tstake"></div>');
	var cur_pos = "seatPos" + pos;
	divStake.appendTo(divChip);
	divSeatbg.appendTo(divSeat);
	divChip.appendTo(divSeat);
	divName.appendTo(divSeat);
	divMoney.appendTo(divSeat);
	divCountdown.appendTo(divSeat);
	divCount.appendTo(divCountdown);
	divWinbg.appendTo(divSeat);
	divWin.appendTo(divCountdown);
	divSeatdownbg.appendTo(divWin);
	divWin_last_card01.appendTo(divWin);
	divWin_last_card02.appendTo(divWin);
	divSeat.addClass(cur_pos);
	divSeat.appendTo($("#container"));
	
	var IsSat = false;
	var table = 0;
	var chips = [];
	seatObj.getIsSat = function() {
			return IsSat;
	};
	seatObj.setIsSat = function(newIsSat) {
			IsSat = newIsSat;
	};

	seatObj.sit = function(_username,_stake,_user_id) {	
				seatObj.username 	= _username;
				seatObj.stake 		= _stake;
				seatObj.userid		= _user_id;

				divName.html(_username);
				divMoney.html(_stake);
				//document.getElementById("money" + id.slice(-1)).innerHTML = _stake;
				seatObj.setIsSat(true);
	};

	seatObj.setStake = function(newstake,newtable) {
			divMoney.html(newstake);
			var diff = newtable - table;
			if(diff > 0){
				var newChip = $('<div class="chipStart"></div>');
				newChip.prependTo(divSeat);
				newChip.addClass("chip100");

				setTimeout(function(){
					newChip.addClass("chip");

				},1);
				divStake.html(newtable);
				divStake.show();
				chips.push(newChip);
			}
	};
	seatObj.clearStake = function(){
		table = 0;
		divStake.hide();
	}

	seatObj.setCountdown = function(position) {
		divCount.removeClass("countdown down");
		divCount.addClass("countdown down");
		divCount.show();
		divCount.animate({ top : divCount.height() }, 10000, function() {
					divCount.hide();
					divCount.removeAttr("style");
				}
		);
	};

	seatObj.removeCountdown = function(position) {
		divCount.stop();
		divCount.hide();
		divCount.removeAttr("style");
	};

	seatObj.showWinCard = function() {
		divWin_last_card01.show();
		divWin_last_card02.show();
	};

	seatObj.setWinCard = function(card, carDiv_no) {
		var _suit;
		var _rank;

		console.log(card);
		if (card.length == 2) {
			_suit = card.charAt(1);
			_rank = card.charAt(0);
		}
		if (card.length == 3) {
			_suit = card.charAt(2);
			_rank = "10";
		}
		if (card.length != 2 && card.length != 3) {
			console.log("ERROR!!!");
			return;
		}
		if(carDiv_no == 1) {
			console.log([poker_lib.getCard(_suit, _rank),"+++++++++++++++++++++++++++++++>>>>>>"]);
			divWin_last_card01.attr("src", poker_lib.getCard(_suit, _rank));
		} else {
			divWin_last_card02.attr("src", poker_lib.getCard(_suit, _rank));
		}
	};

	seatObj.removeCard = function() {
		divWin_last_card01.removeAttr("style");
		divWin_last_card02.removeAttr("style");
	};

	seatObj.seatStand = function() {
		seatObj.username 	= "";
		seatObj.stake 		= "";
		seatObj.userid		= "";
		divName.html("name");
		divMoney.html("money");
		seatObj.setIsSat(false);
	}

	seatObj.showSeatdownbg = function() {
		divSeatdownbg.show();
	};

	seatObj.removeSeatdownbg = function() {
		divSeatdownbg.removeAttr("style");
	};

	seatObj.showWinbg = function() {
		divWinbg.show();
	};

	seatObj.removeWinbg = function() {
		divWinbg.removeAttr("style");
	};

	seatObj.getSeatDIV = function(){
		return divSeat;
	};

	seatObj.getChipDIV = function(){
		return divChip;
	};

	seatObj.setPos = function(newpos) {
		divSeat.removeClass(cur_pos);
		cur_pos = "seatPos" + newpos;
		divSeat.addClass(cur_pos);
	};
	seatObj.getChips = function(){
		return chips;
	}
	seatObj.cleanChips = function(){
		chips = [];
	}
	//seatObj.sendChip = function(chip)

	seatObj.id = id;
	seatObj.pos = pos;
	seatObj.setIsSat(false);

	return seatObj;
};
function seatInit(){
	window.SeatList = [];
	for(i = 0; i < 9 ;i ++){
			SeatList.push(Seat(i,i));
	}
}
