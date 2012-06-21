function poptip() {
	var poptip = {};
	/*<div id="logoutTip" class="speech-bubble speech-bubble-right">
    	<p>Click to logout</p>
	</div>*/
	var content, direct, remaintime;
	var divID;
	var divTip = $('<div class = speech-bubble></div>');
	var divTipContent = $('<p></p>');
	poptip.init = function(divToAdd, _divID,  _content, _direct, _remaintime){
		divID = _divID;
		content = _content;
		direct = _direct;
		remaintime = _remaintime;
		divTip.attr('id',divID);
		divTip.addClass("speech-bubble-"+direct);
		divTipContent.html(content);
		divTipContent.appendTo(divTip);	
		divTip.appendTo(divToAdd);
		//setTimeout(Msg,1000);
		//Msg();
	}
	function ShowIn() {
		divTip.fadeIn();
	}
	function ShowOut() {
		//divTip.fadeOut('fast', function() {
		//	divTip.remove();
		//});
		divTip.remove();
	}
	function Msg() {
		divTip.fadeIn();
		setTimeout(function(){
			divTip.fadeOut('slow',function(){
				divTip.remove();
			});
		},remaintime * 1000);
	}
	poptip.ShowIn = ShowIn;
	poptip.ShowOut = ShowOut;
	poptip.Msg = Msg;
	return poptip;
	
};
init = function() {
	var backBtnTip = poptip();
	var standTip = poptip();
	var quickStart = poptip();
	var sitDown = poptip();
	backBtnTip.init($("#backBtnTip"), "backBtnTip", "Back to Previous Level", "left", 5);
	standTip.init($("#standTip"), "standTip", "Stand Up", "right", 5);
	quickStart.init($("#quick_accTip"), "quick_accTip", "Quick Start Game", "right", 5);
	sitDown.init($("#sitTip"), "sitTip", "click one of the 9 seats to sit down ","bottom", 5);
	backBtnTip.Msg();
	standTip.Msg();
	quickStart.Msg();
	sitDown.Msg();
}

//$(init);
window.onload = init;
