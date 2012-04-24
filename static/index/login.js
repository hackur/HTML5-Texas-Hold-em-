
var user_link = "../user/user.html";

function login_check() {
	console.log("LOGIN CHECK!!");
	$('#llogin').click(function() {

		$.ajax({
			type:'post',
		url:"/login",
		data:{username:$('#account').val(), password:$('#password').val()},
		success:function(data){
			var result = JSON.parse(data);
			console.log(data);
			if(result.status == "success"){
				window.location = user_link;
			}
			else{
				alert("incorrect password");

			}
		},
	//	dataType:'json',
		});
		return false;
	});

	$('#lvisitor').click(function() {
		var test_data = {};
		var flag;

		if(localStorage.getItem('username') == undefined 
			|| localStorage.getItem('password') == undefined)
		{
			flag = 0;
		}
		else {
			flag = 1;
			test_data.username = localStorage.getItem('username');
			test_data.password = localStorage.getItem('password');
		}

	$.ajax({
		type:'post',
		url:"/guest-login",
		data: test_data,
		success:function(data){
			var result = JSON.parse(data);
			if(flag == 0) {	
				localStorage.setItem('username', result.username);
				localStorage.setItem('password', result.password);
			}
			console.log(result);
			console.log(result['status']);
			if(result.status == "success"){
				window.location = user_link;
			}
			else{
				alert("incorrect password");

			}
		},
		//dataType:'json',
	});				

	return false;
	});
//	register();
}
function register(){
		console.log("reg!!");
	$("#lcancel").bind("vclick",function(){
		console.log("Hello World");
	});
}
