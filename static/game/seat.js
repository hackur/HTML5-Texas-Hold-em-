
function Seat(id,pos){
	var seatObj = {};
		/*
		<div id="seat0" class="seat seatPos0">
			<div class="chip">
				<div id="tstake0" class="tstake">0</div>
			</div>
			<div id="name0" class="name">name</div>
			<div id="money0" class="money">money</div>
			<div id="countdown0"></div>
		</div>
		*/
	console.log([id,pos,"-------------------------!!!!!!!!!"]);
	var divSeat = $('<div class="seat"></div>');
	var divSeatbg = $('<div class="seatbg"></div>');
	var divSeatdownbg = $('<div class="countdown win seat_dowm_bg"></div>');
	var divName = $('<div class="name">name</div>');
	var divMoney = $('<div class="money">money</div>');
	var divCountdown = $('<div class="countdown"></div>');
	var divCount = $('<div class="countdown down"></div>');
	var divWinbg = $('<div class="winbg"></div>')
	var divWin = $('<div class="countdown win"></div>');
	var divWin_last_card01 = $('<img class="countdown win card01" src="./pokers/club/A.png">');
	var divWin_last_card02 = $('<img class="countdown win card02" src="./pokers/club/A.png">');
	var divChip = $('<div class="chip"> </div>');
	var divStake = $('<div class="tstake"></div>');
	var cur_pos = "seatPos" + pos;
	divStake.appendTo(divChip);
	divSeatbg.appendTo(divSeat);
	divChip.appendTo(divSeat);
	divName.appendTo(divSeat);
	divMoney.appendTo(divSeat);
	divCountdown.appendTo(divSeat);
	divCount.appendTo(divCountdown);
	divWinbg.appendTo(divSeat);
	divWin.appendTo(divCountdown);
	divSeatdownbg.appendTo(divWin);
	divWin_last_card01.appendTo(divWin);
	divWin_last_card02.appendTo(divWin);
	divSeat.addClass(cur_pos);
	divSeat.appendTo($("#container"));

	var IsSat = false;
	var table = 0;
	var chips = [];
	var Inter_val = 0;
	seatObj.getIsSat = function() {
			return IsSat;
	};
	seatObj.setIsSat = function(newIsSat) {
			IsSat = newIsSat;
	};
	seatObj.player= undefined;
	seatObj.sit = function(_username,_stake,_user_id) {	
				seatObj.username 	= _username;
				seatObj.stake 		= _stake;
				seatObj.userid		= _user_id;

				divName.html(_username);
				divMoney.html(_stake);
				seatObj.setIsSat(true);
				$.ajax({
					type: 'post',
					data: {id:seatObj.userid},
					url	: 'player-archive',
					success:function(data){
						seatObj.player = Player(data);
					},
					dataType:'json'
				});
	};

	seatObj.setStake = function(newstake,newtable) {
			divMoney.html(newstake);
			var diff = newtable - table;
			if(diff > 0){
				var newChip = $('<div class="chipStart"></div>');
				newChip.prependTo(divSeat);
				newChip.addClass("chip100");

				setTimeout(function(){
					newChip.addClass("chip");

				},1);
				divStake.html(newtable);
				divStake.show();
				chips.push(newChip);
			}
	};
	seatObj.clearStake = function(){
		table = 0;
		divStake.hide();
	}

	seatObj.setCountdown = function(timeout) {
		divCount.removeClass("countdown down");
		divCount.addClass("countdown down");
		divCount.show();
		divCount.animate(
			{ top : divCount.height() }, 
			parseInt(timeout)*1000, function() {
				divCount.hide();
				divCount.removeAttr("style");
			}
		);
	};

	seatObj.removeCountdown = function(position) {
		divCount.stop();
		divCount.hide();
		divCount.removeAttr("style");
	};

	seatObj.showWinCard = function() {
		divWin_last_card01.show();
		divWin_last_card02.show();
	};

	seatObj.setWinCard = function(card, carDiv_no) {
		var _suit;
		var _rank;

		console.log(card);
		if (card.length == 2) {
			_suit = card.charAt(1);
			_rank = card.charAt(0);
		}
		if (card.length == 3) {
			_suit = card.charAt(2);
			_rank = "10";
		}
		if (card.length != 2 && card.length != 3) {
			console.log("ERROR!!!");
			return;
		}
		if(carDiv_no == 1) {
			console.log([poker_lib.getCard(_suit, _rank),"+++++++++++++++++++++++++++++++>>>>>>"]);
			divWin_last_card01.attr("src", poker_lib.getCard(_suit, _rank));
		} else {
			divWin_last_card02.attr("src", poker_lib.getCard(_suit, _rank));
		}
	};

	seatObj.removeCard = function() {
		divWin_last_card01.removeAttr("style");
		divWin_last_card02.removeAttr("style");
	};

	seatObj.seatStand = function() {
		seatObj.username 	= "";
		seatObj.stake 		= "";
		seatObj.userid		= "";
		divName.html("name");
		divMoney.html("money");
		seatObj.setIsSat(false);
	}

	seatObj.showSeatdownbg = function() {
		divSeatdownbg.show();
		var i = 1;
		Inter_val = setInterval(function() {
			if (i % 2 != 0) {
				divSeatdownbg.css("top", "5px");
			} else {
				divSeatdownbg.css("top", "35px");
			}
			i++;
		}, 1000);
	};

	seatObj.removeSeatdownbg = function() {
		divSeatdownbg.stop();
		clearInterval(Inter_val);
		divSeatdownbg.removeAttr("style");
	};

	seatObj.showWinbg = function() {
		divWinbg.show();
	};

	seatObj.removeWinbg = function() {
		divWinbg.removeAttr("style");
	};

	seatObj.getSeatDIV = function(){
		return divSeat;
	};

	seatObj.getChipDIV = function(){
		return divChip;
	};

	seatObj.setPos = function(newpos) {
		divSeat.removeClass(cur_pos);
		cur_pos = "seatPos" + newpos;
		divSeat.addClass(cur_pos);
	};
	seatObj.getChips = function(){
		return chips;
	};
	seatObj.cleanChips = function(){
		chips = [];
	};

	seatObj.showStand = function() {
		$("#stand").removeClass("stand2");
		$("#stand").addClass("stand1");
		$("#stand").click(function() {
			actionButton.send_action_stand();
			seatObj.removeStand();
			seatObj.removeCountdown();
		});
	};

	seatObj.removeStand = function() {
		$("#stand").unbind("click");
		$("#stand").removeClass("stand1");
		$("#stand").addClass("stand2");
	};
	seatObj.appendMessage = function(message){
		message.appendTo(divSeat);
	}
	//seatObj.sendChip = function(chip)
	seatObj.id = id;
	seatObj.pos = pos;
	seatObj.setIsSat(false);

	return seatObj;
};
function Player(){
	var player			= {};
	player.id			= undefined;
	player.username		= undefined;
	player.family		= undefined;
	player.position		= undefined;
	player.level		= undefined;
	player.asset		= undefined;
	player.family_score = undefined;
	player.total_game	= undefined;
	player.won_game		= undefined;
	player.percentage	= undefined;
	player.max_reward	= undefined;
	player.last_login	= undefined;


	player.init = function(display_css, data){
		player.displayer_css= displayer_css;
		player.id			= data.id;
		player.head_portrait= data.head_portrait;
		player.username		= data.username;
		player.family		= data.family;
		player.position		= data.position;
		player.level		= data.level;
		player.asset		= data.asset;
		player.family_score	= data.family_score;
		player.total_game	= data.total_game;
		player.won_game		= data.won_game;
		player.percentage	= data.percentage;
		player.max_reward	= data.max_reward;
		player.last_login	= data.last_login;
	};
	player.show	= function(position){
		player_info.show(player);
	};
	player.hide	= function(){
		player_info.hide();;
	}
}


function seatInit(){
	window.SeatList = [];
	for(i = 0; i < 9 ;i ++){
			SeatList.push(Seat(i,i));
	}
}
(function($){
	var display_css		= "player-info-display-css";
	var dialog			= $('<div id="player-info-dialog" class="player-info"></div>');
	var dialog_bottom	= $('<div id="player-info-bottom"></div>');
	var dialog_content	= $('<div id="player-info-content"></div>');
	var portrait_box	= $('<div  id="portrait_box"></div>');
	var pusername		= $('<span id="username"></span>');
	var pfamily			= $('<span id="family"></span>');
	var plevel			= $('<span id="level"></span>');
	var pposition		= $('<span id="position"></span>');
	var passet			= $('<span id="asset"></span>');
	var pfamily_score	= $('<span id="family_score"></span>');
	var ppercentage		= $('<span id="percentage"></span>');
	var pmax_reward		= $('<span id="max_reward"></span>');
	var ptotal_games	= $('<span id="total_games"></span>');
	var pwon_games		= $('<span id="won_games"></span>');
	var plast_login		= $('<span id="last_login"></span>');
	var plast_login		= $('<span id="last_login"></span>');
	var phead_portrait	= $('<img id="player_head_portrait" src="../.#" style="width: 102px; height: 126px; top: 6px; left: 8px; position: absolute; ">');
	var add_friend_btn	= $('<div id="add_friend_btn">加为好友</div>');
	var send_stake_btn	= $('<div id="send_stake_btn">赠送好友</div>');
	dialog_content.appendTo(dialog);
	dialog_bottom.appendTo(dialog);

	portrait_box.appendTo(dialog_content);
	username.appendTo(dialog_content);
	family.appendTo(dialog_content);
	level.appendTo(dialog_content);
	position.appendTo(dialog_content);
	asset.appendTo(dialog_content);
	family_score.appendTo(dialog_content);
	percentage.appendTo(dialog_content);
	max_reward.appendTo(dialog_content);
	total_reward.appendTo(dialog_content);
	won_games.appendTo(dialog_content);
	last_login.appendTo(dialog_content);

	add_friend_btn.appendTo(dialogBottom);
	send_stake_btn.appendTo(dialogBottom);

	dialog.show = function(player){
		head_portrait.attr('src', player.head_portrait);
		username.text('ID名称：'+player.username);	
		family.text('家族：'+player.family);	
		position.text('职位：'+player.position);	
		level.text('等级：'+player.level);	
		asset.text('资产：'+player.asset);	
		family_score.text('家族积分：'+player.family_score);
		percentage.text('胜率：'+player.percentage);
		max_reward.text('赢得最大赌注：'+player.max_reward);
		total_games.text('总局数：'+player.total_games);
		won_games.text('胜利局数：'+player.won_games);
		last_login.text('最近上线时间：'+player.last_login);
		dialog.addClass(display_css);
	};
	dialog.hide	= function(){
		dialog.removeClass(display_css);
	};
	add_friend_btnt.click(function(){
		console.log("add_friend_btnt.click");
	});	
	send_stake_btnt.click(function(){
		console.log("send_stake_btnt.click");
	});	
	$('#container').append(dialog);
	window.player_info = dialog;
})($);
