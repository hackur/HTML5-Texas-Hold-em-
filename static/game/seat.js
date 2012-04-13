var SeatObj = function(IsSat,id,pos) {
	var seatObj = {};
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
		document.getElementById("name" + id.slice(-1)).innerHTML = _username
		document.getElementById("money" + id.slice(-1)).innerHTML = _stake;

		seatObj.setIsSat(1);
	};
	seatObj.setStake = function(seat_no, newstake) {
		document.getElementById("money" + seat_no).innerHTML = newstake;
	}

	seatObj.id = id;
	seatObj.pos = pos;

	return seatObj;
};
