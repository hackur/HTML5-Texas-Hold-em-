function poptip() {
	var poptip = {};
	/*<div id="logoutTip" class="speech-bubble speech-bubble-right">
    	<p>Click to logout</p>
	</div>*/
	var left, top, width, height, content, direct, remaintime;
	var divID;
	var divTip = $('<div class = speech-bubble></div>');
	var divTipContent = $('<p></p>');
	poptip.init = function(divToAdd, _divID,  _content, _direct, _remaintime, _left, _top, _width, _height){
		divID = _divID;
		left = _left;
		top = _top;
		width = _width;
		height = _height;
		content = _content;
		direct = _direct;
		remaintime = _remaintime;
		divTip.attr('id',divID);
		divTip.addClass("speech-bubble-"+direct);
		divTipContent.append(content);
		divTipContent.appendTo(divTip);	
		divTip.appendTo(divToAdd);
		setTimeout(Msg,1000);
	}
	function Msg() {
		divTip.fadeIn();
		setTimeout(function(){
			divTip.fadeOut('slow',function(){
				divTip.remove();
			});
		},remaintime * 1000);
	}
	return poptip;
	
};
init = function() {
	var backBtnTip = poptip();
	var standTip = poptip();
	var quickStart = poptip();
	//var sitDown = poptip();
	backBtnTip.init($("#backBtnTip"), "backBtnTip", "Back to Previous Level", "left", 5);
	standTip.init($("#standTip"), "standTip", "Stand Up", "right", 5);
	quickStart.init($("#quick_accTip"), "quick_accTip", "Quick Start Game", "right", 5);
	//sitDown.init($("#sitTip"), "sitTip", "选择带的钱数，然后坐下 ","bottom", 100);
} 

//$(init);
window.onload = init;
