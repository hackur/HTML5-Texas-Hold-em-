window.get_event_position = function(e){
	if(window.touch_enable && e.touches){
		if(e.touches[0]){
			e.clientX =  e.touches[0].pageX;
			e.clientY =  e.touches[0].pageY;
		}
		else{
			e.clientX =  e.changedTouches[0].pageX;
			e.clientY =  e.changedTouches[0].pageY;
		}
	}
	return [e.clientX,e.clientY]
}
function show_loading(){
	$.mobile.showPageLoadingMsg();
}
function hide_loading(){
	$.mobile.hidePageLoadingMsg()
}
//function decide_event(){
	//window.event_up = "touchend";
	//window.event_down = "touchstart"; 
	//window.event_move = "touchmove";
	//window.event_click = "click";
	if(navigator.userAgent.match(/iPhone/i) ||
	 		navigator.userAgent.match(/Android/i) ||
			navigator.userAgent.match(/iPad/i) ||
			navigator.userAgent.match(/iPod/i) ||
			navigator.userAgent.match(/webOS/i) ||
			navigator.userAgent.match(/BlackBerry/)
	){
		window.event_up = "touchend";
		window.event_down = "touchstart"; 
		window.event_move = "touchmove";
		window.event_click = "vclick";
		window.touch_enable = true;
	}
	else{
		window.event_up = "mouseup"; 
		window.event_down = "mousedown"; 
		window.event_move = "mousemove";
		window.event_click = "click";
		window.touch_enable = false;
	}

	if( $.browser.webkit ) {
			window.eventTransitionEnd = "webkitTransitionEnd";
	} else if( $.browser.mozilla ) {
			window.eventTransitionEnd = "transitionend";
	} else if ($.browser.opera) {
			window.eventTransitionEnd = "oTransitionEnd";
	}
//}
