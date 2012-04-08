
(function(actionButton,$){

	var A_ALLIN 		= 1;
	var A_CALLSTAKE 	= 2;
	var A_RAISESTAKE	= 3;
	var A_CHECK			= 4;
	var A_DISCARDGAME	= 5;

	var buttons = { 
			1:'#btAllin', 4:'#btCheck',
			3:'#btRaise',2:'#btCall',
			5: '#btFold'
			};
	function disable_all(){
		$.each(buttons,function(key,value){
			$(value).removeClass("buttonEnable");
			$(value).addClass("buttonDisable");
		});
	}

	function enable_buttons(rights){
		var allRight = [A_ALLIN,A_CHECK,A_RAISESTAKE,A_CALLSTAKE,A_DISCARDGAME];
		$.each(rights,function(index,value){
			var bid = buttons[value];
			$(bid).addClass("buttonEnable");
			$(bid).removeClass("buttonHide");
			$(bid).removeClass("buttonDisable");

			allRight.splice(allRight.indexOf(value),1);
		});
		$.each(allRight,function(index,value){
			var bid = buttons[value];
			$(bid).removeClass("buttonEnable");
			$(bid).addClass("buttonHide");
			$(bid).addClass("buttonDisable");
		});
	}

	actionButton.enable_buttons = enable_buttons;
	actionButton.disable_all = disable_all;

	function unit_test(){
		//enable_buttons([2,3,4]);
		disable_all();
	}
	$(unit_test);

}(window.actionButton = window.actionButton || {} ,jQuery));

