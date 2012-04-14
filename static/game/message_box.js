
(function(message_box,$){
	var box;
	function init(){
		box = $("<div></div>");
		box.appendTo($("#container"));
		box.addClass("message_box");
	}
	$(init);

	var message_boxes = [];

	function showMessage(content,expire){
		contentbox = $("<label class='message_box_content'></label>");
		
		var msg = $('<div class="message_box_entry"></div>');
		contentbox.appendTo(msg);
		contentbox.html(content);
		message_boxes.unshift(msg);
		$.each(message_boxes,function(index,box){
			box.css("top",index * 45 +"px");
		});
		msg.prependTo(box);
		setTimeout(function(){
			msg.fadeOut('slow',function(){
				msg.remove();
				message_boxes.splice(message_boxes.indexOf(msg),1);
			});
		},expire * 1000);
	}
	message_box.showMessage = showMessage;


}(window.message_box = window.message_box || {} ,jQuery));
