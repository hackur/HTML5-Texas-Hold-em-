
function Seat(id,pos){
	var seatObj = {};


				/*
				<div id="seat0" class="seat seatPos0">
					<div class="chip0 chip">
						<div id="tstake0" class="tstake">0</div>
					</div>
					<div id="name0" class="name">name</div>
					<div id="money0" class="money">money</div>
					<div id="countdown0"></div>
					
				</div>
				*/
	var divSeat = $('<div class="seat"></div>');
	var divName = $('<div class="name">name</div>');
	var divMoney = $('<div class="money">money</div>');
	var divCountdown = $('<div></div>');
	var divChip = $('<div class="chip"> </div>');
	var divStake = $('<div class="tstake">0</div>');
	divStake.appendTo(divChip);

	divChip.appendTo(divSeat);
	divName.appendTo(divSeat);
	divMoney.appendTo(divSeat);
	divCountdown.appendTo(divSeat);
	divSeat.addClass("seatPos" + pos);
	divSeat.appendTo($("#gametable"));
	
	seatObj.IsSat = IsSat;
	
	seatObj.getIsSat = function() {
			return seatObj.IsSat;
	};
	seatObj.setIsSat = function(newIsSat) {
			seatObj.IsSat = newIsSat;
	};

	seatObj.sit = function(_username,_stake) {	
				seatObj.username 	= _username;
				seatObj.stake 		= _stake;
				divName.html(_username);
				divMoney.html(_stake);
				//document.getElementById("money" + id.slice(-1)).innerHTML = _stake;
				seatObj.setIsSat(true);
	};

	seatObj.setStake = function(seat_no, newstake) {
				divMoney.html(newstake);
	};
	seatObj.id = id;
	seatObj.pos = pos;
	seatObj.setIsSat(false);

	return seatObj;
};
function seatInit(){
	window.SeatList = [];
	for(i = 0; i < 9 ;i ++){
			SeatList.push(SeatObj(i,i));
	}
}
