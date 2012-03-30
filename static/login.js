

function login_check() {
	$('#llogin').click(function() {

					$.ajax({
						type:'post',
						url:"login",
						data:{username:$('#account').val(), password:$('#password').val()},
						success:function(data){
							console.log(data);
						},
						dataTye:'json',
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
						url:"guest-login",
						data: test_data,
						success:function(data){
							if(flag == 0) {	
								result = JSON.parse(data);
								localStorage.setItem('username', result.username);
								localStorage.setItem('password', result.password);
							}
						},
						dataTye:'json',
					});				

					return false;
				});
}