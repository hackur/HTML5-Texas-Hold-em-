
(function(actionButton,$){

	var A_ALLIN 		= 1;
	var A_CALLSTAKE 	= 2;
	var A_RAISESTAKE	= 3;
	var A_CHECK			= 4;
	var A_DISCARDGAME	= 5;
	var A_STAND       = 8;
	var limits;
	
	var buttons = { 
			1:'#btAllin', 4:'#btCheck',
			3:'#btRaise',2:'#btCall',
			5: '#btFold'
			};
	var actions = {
		1:action_allin,
		2:action_call,
		3:action_raise,
		4:action_check,
		5:action_discard
	};
	
	var flagCheck = 0;
	var flagCheckOrFold = false;
	var flagCallAny = false;

	function disable_all(){
		console.log("disable_all");
		$.each(buttons,function(key,value){
			$(value).removeClass("buttonEnable");
			$(value).addClass("buttonDisable");
			$(value).addClass("buttonHide");
			$(value).unbind("click");
		});
		raise_slider_dispose();
	}
	function send_action(action_type,amount){
		console.log("SEND ACTION!!");
		var message = { action: action_type };
		if(amount){
			message['amount'] = amount;
		}
		var msg = JSON.stringify(message);
		if(window.ws){
			window.ws.send(msg);
			return;
		}
		console.log(msg);
		$.ajax({
			type:'post',
			url:"/post-board-message",
			data:{message:msg},
			success:function(data){
				console.log(data);
			},
			dataType:'json'
			}
		);
		disable_all();
		

	}
	function send_action_stand(){
		send_action(A_STAND);
		disable_AutoButtons();
	}
	function action_allin(){
		send_action(A_ALLIN);
	}
	function action_call(){
		send_action(A_CALLSTAKE);
	}
	function action_raise(){
		$("#btRaise").unbind("click");
		raise_slider_init();
	}
	function action_check(){
		send_action(A_CHECK);
	}
	function action_discard(){
		window.user_info.userIsPlay = false;
		send_action(A_DISCARDGAME);
	}
	var down_pos;
	var down_slider_pos;
	var cur_raise_value;
	function raise_update_value(height,maxHeight){
		var min = limits[A_RAISESTAKE][0];
		var max = limits[A_RAISESTAKE][1];
		//var steps = (max - min) / 1;
		//console.log("height" + height + " maxHeight" + maxHeight);
		var position = minMaxPosition(min,max);
		//console.log(min + " " + max + "minmax");
		//console.log(position[0] + " " + position[1]);
		var SpaceNum = position[1] - position[0] + 1;
		var SpaceLength = maxHeight / SpaceNum;
		var whichSpace = Math.floor(height / SpaceLength);
		var value = mem[position[0] + whichSpace];
		if (value <= min)
			value = min;
		if (value >= max)
			value = max; 
		//var value = Math.round(height/maxHeight * steps) +  min;
		//var value = Math.floor(height/maxHeight * steps) +  min;
		cur_raise_value = value;

		$("#raise_amount").html(value);
		
	}
	function minMaxPosition(min,max) {
		var i;
		position=[];
		for(i = 1; i < 46; i++){
			if (mem[i]>min) {
				position[0]=i-1;
				break;
			}
			
			
		}
		while( i<64){
			if (mem[i]>max) {
				position[1]=i;
				break;
				
			}	
			i++;	
		}
		return position;
		
	}
	var mem = [];
 	var weight = [1,10,100,1000,10000,100000,1000000,10000000];
 	var xx = [9,1,2,3,4,5,6,7,8]
 	function genMem() {
 		var i = 1;
 		while(i<64){	
 		var degree = Math.floor((i-1)/9);
 		mem[i]=xx[i%9]*weight[degree];
 		i++;
 		}
 		//for(i = 1; i < 46; i++)
 		//	console.log(mem[i] + "\n");
 	}
 	genMem();
	function raise_slider_move(e){
		var startY = get_event_position(e)[1];
		var minTop = 
				$("#raise_amount").offset().top +
				$("#raise_amount").height();
		var	maxTop = $("#raise_slider").offset().top 
				+ $("#raise_slider").height()
				- $("#raise_slider_button").height();
		var diffX = startY - down_pos;
		var next_pos = down_slider_pos + diffX;
		
		if(next_pos >= minTop && next_pos <= maxTop){
			$("#raise_slider_button").css("top",(next_pos - $("#raise_amount").offset().top ) + "px");
		}
		else{
			return;
		}
		raise_update_value(maxTop - next_pos,maxTop - minTop);
		e.preventDefault();

	}
	function raise_slider_up(){
		window.removeEventListener(event_move, raise_slider_move);
	}
	function raise_slider_dispose(addEvent){
		$('#raise_slider').hide();
		$('#btRaiseText').html("Raise");
		if(addEvent)
			$("#btRaise").click(action_raise);
		window.removeEventListener(event_down, raise_slider_down);
		window.removeEventListener(event_up, raise_slider_up);
	}
	function raise_slider_down(e){
		if(e.target == document.getElementById("raise_slider_button")){
			window.addEventListener(event_move, raise_slider_move);
			down_pos = get_event_position(e)[1];
			down_slider_pos = $("#raise_slider_button").offset().top;
		}
		else if(e.target == document.getElementById("raise_slider")){
			console.log("PASS!!!");
		}
		else if(e.target == document.getElementById("btRaiseText")){
			raise_slider_dispose();
			send_action(A_RAISESTAKE,cur_raise_value);
			/*** SEND ACTION ***/
		}
		else if(e.target == document.getElementById("raise_amount")){
		}
		else{
			raise_slider_dispose(true);
		}
		e.preventDefault();
	}

	function raise_slider_init(){
		raise_update_value(0,100);
		$('#btRaiseText').html("OK");
		$('#raise_slider').show();
		window.addEventListener(event_down, raise_slider_down);
		window.addEventListener(event_up, raise_slider_up);
		var	maxTop = $("#raise_slider").offset().top 
				+ $("#raise_slider").height()
				- $("#raise_slider_button").height();

		$("#raise_slider_button").css("top",(maxTop - $("#raise_amount").offset().top ) + "px");
		//window.addEventListener(event_move, raise_slider_move);
	}

	function enable_buttons(rights,_limits){
		if(checkAutoButtons(rights))
			return;
		
		console.log(["enable_buttons",rights,_limits]);
		var allRight = [A_ALLIN,A_CHECK,A_RAISESTAKE,A_CALLSTAKE,A_DISCARDGAME];
		limits = _limits;
		$.each(rights,function(index,value){
			if(buttons[value] == undefined){
				return;
			}
			console.log("index " + index + "value " + value);
			var bid = buttons[value];
			$(bid).addClass("buttonEnable");
			$(bid).removeClass("buttonHide");
			$(bid).removeClass("buttonDisable");

			allRight.splice(allRight.indexOf(value),1);
			$(bid).click(actions[value]);
			if(value == A_CALLSTAKE){
				$(bid).html("CALL " + _limits[value]);
			}
			
		});
		$.each(allRight,function(index,value){
			var bid = buttons[value];
			$(bid).removeClass("buttonEnable");
			$(bid).addClass("buttonHide");
			$(bid).addClass("buttonDisable");
		});
	}
	function checkAutoButtons(rights) {
		var hasCheckRight = 0, hasAllInRight = 0,hasCallStakeRight = 0;
		var i = 0;
		while(i < rights.length) {
			if(A_CHECK == rights[i]){
				hasCheckRight = 1;
			}
			if(A_ALLIN == rights[i]){
				hasAllInRight = 1;
			}
			if(A_CALLSTAKE == rights[i]) {
				hasCallStakeRight = 1;
			}
			i++;
		}
		if (flagCallAny){
			if(hasCallStakeRight){
				action_call();
				resetAutoButtons();
				return true;
			}
			if(hasAllInRight){
				action_allin();
				resetAutoButtons();
				return true;
			}	
		}
		if (flagCheckOrFold){
			if(hasCheckRight){
				action_check();
				resetAutoButtons();
				return true;
			}
			action_discard();
			resetAutoButtons();
			return true;
			
		}
		if (flagCheck){
			var i = 0,flag = 0;
			if(hasCheckRight){
				action_check();
				resetAutoButtons();
				return true;
			}
		}
		
		resetAutoButtons();
		return false;
	}
	function enable_AutoButtons(){
		//resetAutoButtons();
		$("#btAutoCheck").removeClass("autoButtonHide");
		$("#btAutoCheck").unbind("vclick",chooseCheck);
		$("#btAutoCheck").bind("vclick",chooseCheck);
		$("#btAutoCheckOrFold").removeClass("autoButtonHide");
		$("#btAutoCheckOrFold").unbind("vclick",chooseCheckOrFold);
		$("#btAutoCheckOrFold").bind("vclick",chooseCheckOrFold);
		$("#btAutoCallAny").removeClass("autoButtonHide");
		$("#btAutoCallAny").unbind("vclick",chooseCallAny);
		$("#btAutoCallAny").bind("vclick",chooseCallAny);
	
	}
	function disable_AutoButtons(){
		console.log("disable autobuttons");
		$("#btAutoCheck").addClass("autoButtonHide");
		$("#btAutoCheck").unbind("vclick",chooseCheck);
		$("#btAutoCheckOrFold").addClass("autoButtonHide");
		$("#btAutoCheckOrFold").unbind("vclick",chooseCheckOrFold);
		$("#btAutoCallAny").addClass("autoButtonHide");
		$("#btAutoCallAny").unbind("vclick",chooseCallAny);
	}
	function resetAutoButtons() {
		if(flagCheck){
			$("#cbAutoCheck").removeClass("check");
			$("#cbAutoCheck").addClass("noCheck");
			flagCheck = 0;
		}
		if(flagCheckOrFold) {
			$("#cbAutoCheckOrFold").removeClass("check");
			$("#cbAutoCheckOrFold").addClass("noCheck");
			flagCheckOrFold = 0;
		}
		if(flagCallAny){
			$("#cbAutoCallAny").removeClass("check");
			$("#cbAutoCallAny").addClass("noCheck");
			flagCallAny = 0;
		}
	}
	function chooseCheck(){
		
		if(!flagCheck){
			resetAutoButtons();
			$("#cbAutoCheck").removeClass("noCheck");
			$("#cbAutoCheck").addClass("check");
			flagCheck = 1;
		} else {
			$("#cbAutoCheck").removeClass("check");
			$("#cbAutoCheck").addClass("noCheck");
			flagCheck = 0;
		}
	}
	function chooseCheckOrFold(){

		if(!flagCheckOrFold){
			resetAutoButtons();
			$("#cbAutoCheckOrFold").removeClass("noCheck");
			$("#cbAutoCheckOrFold").addClass("check");
			flagCheckOrFold = 1;
		} else {
			$("#cbAutoCheckOrFold").removeClass("check");
			$("#cbAutoCheckOrFold").addClass("noCheck");
			flagCheckOrFold = 0;
		}
	}
	function chooseCallAny(){

		if(!flagCallAny){
			resetAutoButtons();
			$("#cbAutoCallAny").removeClass("noCheck");
			$("#cbAutoCallAny").addClass("check");
			flagCallAny = 1;
		} else {
			$("#cbAutoCallAny").removeClass("check");
			$("#cbAutoCallAny").addClass("noCheck");
			flagCallAny = 0;
		}
	}

	actionButton.enable_buttons = enable_buttons;
	actionButton.disable_all = disable_all;
	actionButton.send_action_stand = send_action_stand;
	actionButton.enable_AutoButtons = enable_AutoButtons;
	actionButton.disable_AutoButtons = disable_AutoButtons;
	actionButton.resetAutoButtons = resetAutoButtons;
	function unit_test(){
		enable_buttons([2,3,4]);
	}
	//$(unit_test);

}(window.actionButton = window.actionButton || {} ,jQuery));

