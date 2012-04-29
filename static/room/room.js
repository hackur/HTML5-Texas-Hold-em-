function fetchRoom(roomClass) {
	var roomcontent;
	if(roomClass == 0) {
		roomcontent = "#normalroomcontent";
	} else if(roomClass == 1) {
		roomcontent = "#advancedroomcontent";
	} else if(roomClass == 2) {
		roomcontent = "#responseroomcontent";
	} else if(roomClass == 3) {
		roomcontent = "#competitionroomcontent";
	} else if(roomClass == 4) {
		roomcontent = "#familybattleroomcontent";
	}
	$(roomcontent).html("");
	$.ajax({
		type : 'get',
		url : "/list_room",
		data : {
			type : roomClass
		},
		success : function(data) {
			console.log(data);
			$("#createroom").click(function() {
				$("#settingDialog").show();

			});
			$.each(data.rooms, function(index, room) {
				var id = room[0];
				var blind = parseInt(room[1]);
				var player = room[2];
				var max_player = room[3];
				var min_stake = room[4];
				var max_stake = room[5];
				var item = $('<li class="roomitem"></li>');
				item.append($('<span class="roomid"></span>').html(id));
				item.append($('<span class="info1"></span>').html(blind / 2 + "/" + blind));
				item.append($('<span class="info2"></span>').html(min_stake + "/" + max_stake));
				item.append($('<span class="numplaying"></span>').html(player + "/" + max_player));
				$(roomcontent).append(item);

				item.click(function() {
					console.log(id);
					localStorage["current_room_id"] = id;
					window.location = "../game/game.html";
				});
			});
		},
		dataType : 'json',
		cache : false
	});
}

function create_room() {
	console.log(parseInt($("#curBlind").html()));
	//console.log($("#curBlind").val());
	var blind = parseInt($("#curBlind").html());
	//var max_stake = $("#max_stake").val();
	//var min_stake = $("#min_stake").val();
	var max_stake = 100;
	var min_stake = 1000;
	//var max_player = $("#personNumShow").val();
	var max_player = parseInt($("#personNumShow").html());
	$.post("/create_room", {
		blind : blind,
		max_player : max_player,
		min_stake : min_stake,
		max_stake : max_stake
	}, function(data) {
		localStorage["current_room_id"] = data.room_id;
		window.location = "../game/game.html";
		console.log(data);
	}, 'json');

}

$(function() {
	fetchRoom(0);
});
