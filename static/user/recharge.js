

(function(recharge,$){
	
	/*var runner_button;
	var runner_button_down = false;
	var runwayLeft = 0;
	var runwayRight = 0;

	var drag = function() {

		window.addEventListener(event_down, runner_down);
		window.addEventListener(event_up, runner_up);
		runner_button = document.getElementById('rrunner');
	};

	var runner_down = function(e) {
		if(e.target == runner_button) {
			runner_button_down = true;
			window.addEventListener(event_move, runner_move);
		}
	};

	var runner_up = function(e) {
		window.removeEventListener(event_move, runner_move);
	};

	var runner_move = function(e) {
		runwayLeft = $("#rrunway").offset().left;
		runwayRight = $("#rrunway").css('width');
		runwayRight = parseInt(runwayRight.slice(0, runwayRight.length - 2)) 
						+ runwayLeft;
		console.log(runwayRight + " " + runwayLeft);

		var curX = get_event_position(e)[0];
		console.log(get_event_position(e)[0]);
		if(curX > runwayRight){
			curX = runwayRight;
		}
		if(curX < runwayLeft){
			curX = runwayLeft;
		}
		curX -= runwayLeft;
		$(runner_button).offset({left:  curX + 40 });
		e.preventDefault();
	};

	var dispose = function() {
		window.removeEventListener(event_down, runner_down);
		window.removeEventListener(event_up, runner_up);
	};
	*/
	var rechargeSliderBar = slider_bar();
	function drag(){
		rechargeSliderBar.setPosition(39,259);
		rechargeSliderBar.setVar(changeChargeNum);
		function changeChargeNum(val) {
			$("#current").html(val);
		}
		rechargeSliderBar.create($("#rechargeSliderbar"),0,10000,100);
	}
	recharge.drag = drag;
	
})(window.recharge = window.recharge || {}, jQuery);