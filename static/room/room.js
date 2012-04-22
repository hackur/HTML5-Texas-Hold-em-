
function fetchRoom(){
	$.ajax({
		type:'get',
		url:"/list_room",
		data:{},
		success:function(data){
			console.log(data);
			$("#createroom").click(function(){
				$("#setting").show();

			});
			$.each(data.rooms,function(index,room){
				var id = room[0];
				var blind = parseInt(room[1]);
				var player = room[2];
				var max_player = room[3];
				var min_stake = room[4];
				var max_stake = room[5];
				var item = $('<li class="roomitem"></li>');
				item.append($('<span class="roomid"></span>').html(id));
				item.append($('<span class="info1"></span>').html(blind/2 + "/" + blind));
				item.append($('<span class="info2"></span>').html(min_stake +"/" + max_stake));
				item.append($('<span class="numplaying"></span>').html(player +"/"+max_player));
				$("#gridcontent").append(item);
				item.click(function(){
					console.log(id);
					localStorage["current_room_id"] = id;
					window.location="../game/game.html";
				});
			});
		},
		dataType:'json',
		cache:false
	});
}
function create_room(){
	console.log($("#blind").val());
	var blind = $("#blind").val();
	var max_stake = $("#max_stake").val();
	var min_stake = $("#min_stake").val();
	var max_player = $("#max_player").val();
	$.post(
			"/create_room",
			{blind:blind,max_player:max_player,
				min_stake:min_stake,max_stake:max_stake},
				function(data){
					localStorage["current_room_id"]= data.room_id;
					window.location="../game/game.html";
					console.log(data);
				},
				'json'
	);

}
$(fetchRoom);
