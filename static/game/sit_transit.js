(function(sit_transit,$,undefined){
	var all_class = ["#seat0","#seat1","#seat2","#seat3",
			"#seat4"];
	var all_position = [];
	function init(){
		$.each(all_class,function(id,value){
			var left = $(value).css('left');
			var top = $(value).css('top');
			all_position.push([left,top]);
		});
	}
	$(init);

	function _sit_transit(sit) {
		console.log(sit + "   +++++=");
		var transit_id = sit, transit_temp = -1;
		for (var i = transit_id; i < all_class.length; i++) {
			++transit_temp;
			transit(all_position[transit_temp][0], all_position[transit_temp][1], all_class[i]);
		}

		for (var i = 0; i < transit_id; i++) {
			++transit_temp;
			transit(all_position[transit_temp][0], all_position[transit_temp][1], all_class[i]);
		}
	}

	function transit(to_left,to_top, transit_from) {
	  	$(transit_from).css('left',to_left);
	  	$(transit_from).css('top',to_top);
	}
	sit_transit.transit = _sit_transit;
}(window.sit_transit = window.sit_transit || {} ,jQuery));