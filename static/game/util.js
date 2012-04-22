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
function decide_event(){
	window.event_up = "touchend";
	window.event_down = "touchstart"; 
	window.event_move = "touchmove";
	if(navigator.userAgent.match(/iPhone/i) ||
	 		navigator.userAgent.match(/Android/i) ||
			navigator.userAgent.match(/iPad/i) ||
			navigator.userAgent.match(/iPod/i) ||
			navigator.userAgent.match(/webOS/i) ||
			navigator.userAgent.match(/BlackBerry/)
	){
		event_up = "touchend";
		event_down = "touchstart"; 
		event_move = "touchmove";
		window.touch_enable = true;
	}
	else{
		event_up = "mouseup"; 
		event_down = "mousedown"; 
		event_move = "mousemove";
		window.touch_enable = false;
	}

	if( $.browser.webkit ) {
			eventTransitionEnd = "webkitTransitionEnd";
	} else if( $.browser.mozilla ) {
			eventTransitionEnd = "transitionend";
	} else if ($.browser.opera) {
			eventTransitionEnd = "oTransitionEnd";
	}
}
