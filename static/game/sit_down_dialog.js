
(function(sit_dialog,$){
	var slider_button;
	var slider_button_down = false;
	var startX = 0;
	var startY = 0;
	var barLeft = 0;
	var barRight = 0;
	var seatObj;
	var cur_stake;

	function sit_silder_down(e){
		if(e.target == slider_button){
			slider_button_down = true;
			window.addEventListener(event_move, sit_silder_move);
			startX = get_event_position(e)[0];
		}
		else{
			var m_x  = get_event_position(e)[0];
			var m_y  = get_event_position(e)[1];
			var width = $("#sit_down_dialog").css('width');
			width = parseInt(width.slice(0,width.length-2));
			var height = $("#sit_down_dialog").css('height');
			height = parseInt(height.slice(0,height.length-2));
			var left = $("#sit_down_dialog").offset().left;
			var top = $("#sit_down_dialog").offset().top;
			console.log([width,height,left,top]);
			if(m_x < left || m_y < top){
				hide();
				return;
			}
			if(m_x > left + width || m_y > top + height){
				hide();
				return;
			}
		}
	
	}
	function sit_silder_move(e){
		var curX = get_event_position(e)[0];
		if(curX > barRight){
			curX = barRight;
		}
		if(curX < barLeft){
			curX = barLeft;
		}
		curX -= barLeft;
		decide_amount(curX);
		e.preventDefault();
	}
	function decide_amount(mouseX){
		var max = Math.min(window.room_info.max_stake,window.user_info.asset);
		console.log(max);
		var steps = (max - window.room_info.min_stake) 
				/ window.room_info.blind;

		var perStep = (barRight - barLeft) / steps;
		var add = Math.round(mouseX / perStep) * window.room_info.blind
		var total = add + window.room_info.min_stake;
		var buttonPos = Math.round(mouseX / perStep) * perStep;
		if(buttonPos + barLeft > barRight){
			buttonPos = barRight - barLeft;
			total = max;
		}
		cur_stake = total;
		$('#sit_dialog_amount').text(total);
		$("#sit_slider_button").css('left', buttonPos  + "px");
	}
	function sit_silder_up(e){
		window.removeEventListener(event_move, sit_silder_move);
	}

	function submitSit(){
		var id = seatObj.id;
		$.ajax({
			type: "post",
			url: "/sit-down",
			data: {seat: id, stake: cur_stake},
			success: function(data) {
				console.log("Below is sit-down data:");
				console.log(data);
				if(data.status == "success"){
					sit_transit.transit(id);
				}
				else{

				}
			},
			dataType: "json"
		});
		hide();
	};

	function show(_seatObj){
		document.getElementById("sit_down_dialog").style.display = "block";
		$("#submitButton").click(submitSit);

		console.log(event_down);
		window.addEventListener(event_down, sit_silder_down);
		window.addEventListener(event_up, 	sit_silder_up);
		barLeft = $("#sit_slider_bar").offset().left;
		barRight = $("#sit_slider_bar").css('width');
		barRight = parseInt(barRight.slice(0,barRight.length-2)) +  barLeft;
		$('#sit_dialog_amount').text(window.room_info.min_stake);
		cur_stake = window.room_info.min_stake;

		slider_button = document.getElementById("sit_slider_button");
		seatObj = _seatObj;
	};
	function hide(){
		window.removeEventListener(event_down, sit_silder_down);
		window.removeEventListener(event_up, 	sit_silder_up);
		document.getElementById("sit_down_dialog").style.display = "none";
		/**TODO Clear button event listener **/
	}

	sit_dialog.show = show;

}(window.sit_dialog = window.sit_dialog || {} ,jQuery));
