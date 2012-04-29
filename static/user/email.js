function Email(data){
	var email		= {};
	var id			= -1;
	var senderId	= -1;
	var sendDate	= null;
	var message		= null;
	var senderName	= null;
	var emailDOM	= null;

	init	= function(data){
		email.id		= data.id;
		email.sendDate	= data.date;
		email.message	= data.message;
		email.senderId	= data.sender_id;
		email.senderName= data.sender_name;
	};
	
	email.toHTML	= function(){
		emailDOM	= $('<div class="mail-item">'+
							'<div class="content">'+email.sendDate+": "+email.senderName+'</div>'+
							'<div class="mail-border"></div>'+
						'</div>');
		emailDOM.bind('vclick', viewContent);
		return emailDOM;
	};
	var viewContent	= function(){
		$('#sender').text("发件人：" + email.senderName);
		$('#time').text("时间：" + email.sendDate);
		$('#content').text("内容：" + email.message);
		$('#bigFrame2').css("display","block");
		$('#mail_list_frame').css("display", "none");
		window.SelectedEmail = email;
	};
	var dispose	=  function(){
		emailDOM.remove();
	};

	init(data);
	return email;
}
window.EmailList	= [];
window.SelectedEmail= null;
