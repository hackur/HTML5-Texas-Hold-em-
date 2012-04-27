(function(sit_transit,$,undefined){
	var len = 9;

	function _sit_transit(sit) {
		console.log(sit + "   +++++=");
		var transit_id = sit, transit_temp = -1;
		for (var i = transit_id; i < len; i++) {
			++transit_temp;
			SeatList[i].setPos(transit_temp);
		}

		for (var i = 0; i < transit_id; i++) {
			++transit_temp;
			SeatList[i].setPos(transit_temp);
		}
	}
	sit_transit.transit = _sit_transit;
}(window.sit_transit = window.sit_transit || {} ,jQuery));
