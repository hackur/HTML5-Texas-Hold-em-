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
	$.ajax({
		type : 'get',
		url : "/list_room",
		data : {
			type : roomClass
		},
		success : function(data) {
			$(roomcontent).html("");
			var roomID = 1;
			$.each(data.rooms, function(index, room) {
				var id = room[0];
				var blind = parseInt(room[1]);
				var player = room[2];
				var max_player = room[3];
				var min_stake = room[4];
				var max_stake = room[5];
				var item = $('<li class="roomitem"></li>');
				
				item.append($('<span class="roomid"></span>').html(roomID++));
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

$(function(){
	$("#createroom").bind(event_click,function() {

		$.get("/config/room", {}, 
		function(data) {
			var room = data[curRoomType];
			if(room == undefined){
				message_box.showMessage("暂不支持此类房间！",3);
				return;
			}
			blindSliderBar.set_argument(room[0],room[1],room[2]);
			$("#settingDialog").show();
		}, 'json');

	});

	$("#refresh").bind(event_click,function(){
		fetchRoom(curRoomType);
	});
});

function create_room() {
	console.log(parseInt($("#curBlind").html()));
	//console.log($("#curBlind").val());
	var blind = parseInt($("#curBlind").html()) * 2;
	var max_player = parseInt($("#personNumShow").html());
	$.post("/create_room", {
		blind : blind,
		max_player : max_player,
		roomType :curRoomType
	}, function(data) {
		if(data.room_id){
			localStorage["current_room_id"] = data.room_id;
			window.location = "../game/game.html";
			console.log(data);
		}
		else{
			//TODO SHOW ERROR
		}
	}, 'json');

}

function initSetting() {
	$("#backTo").bind(event_click,function(){
		//self.history.go(-1);
		//console.log(document.domain);
		//window.location = "http://" + document.domain + ":" + window.location.port + "/facebook/"
		window.location = "../user/user.html"
	});
	console.log("----------------------------------------------");
	window.blindSliderBar = slider_bar();
	var personSliderBar = slider_bar();
	blindSliderBar.setPosition(70,52);
	blindSliderBar.setVar(changeBlind);
	blindSliderBar.create($("#blindBar"),2,100,2);
	personSliderBar.setPosition(70,119);
	personSliderBar.setVar(changePersonNum);
	personSliderBar.create($("#personNumBar"),2, 9, 1 , 360);
	console.log($("#confirmBtn"));
	$("#confirmBtn").click(submitRomeSetting);
	function submitRomeSetting() {
		create_room();
	}
	$("#cancelBtn").click(cancelSetting);
	function cancelSetting() {
		$("#settingDialog").hide();

	}
	$("#closeButton").click(cancelSetting);
	function changeBlind(val) {
		$("#curBlind").html( (val>>1) +"/" + val);
	}	
	function changePersonNum(val) {
		$("#personNumShow").html(val);
	}	
}
$(initSetting);
$(function() {
	fetchRoom(0);
});


var curStat = "normalroom";
var curRoomType = 0;
function nTabs(thisObj, Num) {
	if (thisObj.className == curStat) return;
	var tabObj = thisObj.parentNode.id;
	console.log(thisObj);
	$("#settingDialog").css("display","none");
	fetchRoom(Num);
	curRoomType = Num;
	console.log(Num);


	var tabList = document.getElementById(tabObj).getElementsByTagName("li");
	for (i = 0; i < tabList.length; i++) {
		if (i == Num) {
			console.log($(".roomhover")[i]);
			$(".roomhover")[i].style.opacity = 1;
			curStat = tabList[i].className;

			document.getElementById(tabList[i].className + "content").style.display = "block";
		} else {
			$(".roomhover")[i].style.opacity = 0;
			document.getElementById(tabList[i].className + "content").style.display = "none";
		}
	}
}
function initRoomSelect(){
	$(".roomhover")[0].style.opacity = 1;
}
$(initRoomSelect); 
