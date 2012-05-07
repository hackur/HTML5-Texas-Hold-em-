
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
	var divSeat = $('<div class="seat"></div>');
	var divSeatbg = $('<div class="seatbg"></div>');
	var divSeatdownbg = $('<div class="countdown win seat_dowm_bg"></div>');
	var divName = $('<div class="name"></div>');
	var divMoney = $('<div class="money"></div>');
	var divCountdown = $('<div class="countdown"></div>');
	var divCount = $('<div class="countdown down"></div>');
	var divWinbg = $('<div class="winbg"></div>')
	var divWin = $('<div class="countdown win"></div>');
	var divWin_last_card01 = $('<img class="countdown win card01" src="./pokers/club/A.png">');
	var divWin_last_card02 = $('<img class="countdown win card02" src="./pokers/club/A.png">');
	var divChip = $('<div class="chip"> </div>');
	var divStake = $('<div class="tstake"></div>');
	var cur_pos = "seatPos" + pos;
	var portrait_border = $('<div class="portrait_border"></div>');
	var portrait = $('<img class="portrait"/>');
	var dealerBtn = $("<p class='dealerBtn'>D</p>");
	
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
	// portrait_border.appendTo(divSeat);
	portrait.appendTo(divSeat);
	divSeat.appendTo($("#container"));
	dealerBtn.appendTo(divSeat);

	var IsSat = false;
	var table = 0;
	var chips = [];
	var Inter_val	= 0;
	var position	= pos; 
	seatObj.player= undefined;
	seatObj.cards = [];
	seatObj.showCardName = function(public_cards){
		var temp = seatObj.cards;
		temp = temp.concat(public_cards);
		var name = window.getHandCardName( window.identifyCard(temp));
		$('#card-name-'+position).remove();
		divSeat.append($("<div class='card-name' id='card-name-"+position+"'>" + name + "</div>"));
	};
	seatObj.showWinCardName = function(public_cards){
		var name = window.getHandCardName( window.identifyCard(public_cards));
		$('#card-name-'+position).remove();
		divSeat.append($("<div class='card-name-win' id='card-name-"+position+"'>" + name + "赢!</div>"));
	};
	seatObj.getIsSat = function() {
			return IsSat;
	};
	seatObj.setIsSat = function(newIsSat) {
			IsSat = newIsSat;
	};
	seatObj.player = undefined;
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
					url	: '/player-archive',
					success:function(data){
						console.log("-----------------")
						seatObj.player = Player(data);
						portrait.attr("src", seatObj.player.head_portrait);
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
	seatObj.showAction = function(action) {
		if (action != undefined) {
			var actionBox = $("<p class='actionBox'>"+action+"</p>");
			actionBox.appendTo(divSeat);
			setTimeout(function() {
				actionBox.remove();
			}, 5000);
		}
	};

	seatObj.showDealerBtn = function() {
		dealerBtn.fadeIn(500);
	};

	seatObj.removeDealerBtn = function() {
		dealerBtn.css("display", "none");
	};

	seatObj.clearStake = function(){
		table = 0;
		divStake.hide();
	};

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
		divName.html("");
		divMoney.html("");
		portrait.remove()
		portrait = $('<img class="portrait" />');
		portrait.appendTo(divSeat);
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
function Player(data){
	var player			= {};
	player.id			= undefined;
	player.username		= undefined;
	player.family		= undefined;
	player.position		= undefined;
	player.level		= undefined;
	player.asset		= undefined;
	player.family_score = undefined;
	player.family_glory = undefined;
	player.total_game	= undefined;
	player.won_game		= undefined;
	player.percentage	= undefined;
	player.max_reward	= undefined;
	player.last_login	= undefined;
	player.friends		= undefined;


	player.init = function(data){
		player.id			= data.id;
		player.head_portrait= data.head_portrait;
		player.username		= data.name;
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
//		player.friends		= data.friends;
		console.log(data.username);
		console.log(player.username);
	};

	player.show	= function(player){
		player_info.show(player);
	};
	player.hide	= function(){
		player_info.hide();
	};
	player.init(data);
	console.log("==================");
	console.log(player);
	return player;
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
	var username		= $('<span id="username"></span>');
	var family			= $('<span id="family"></span>');
	var level			= $('<span id="level"></span>');
	var position		= $('<span id="position"></span>');
	var asset			= $('<span id="asset"></span>');
	var family_score	= $('<span id="family_score"></span>');
	var family_glory	= $('<span id="family_glory"></span>')
	var percentage		= $('<span id="percentage"></span>');
	var max_reward		= $('<span id="max_reward"></span>');
	var total_games		= $('<span id="total_games"></span>');
	var won_games		= $('<span id="won_games"></span>');
	var last_login		= $('<span id="last_login"></span>');
	var head_portrait	= $('<img id="player_head_portrait" style="width: 102px; height: 126px;" />');
	var add_friend_btn	= $('<div id="add_friend_btn"><div id="add_friend_text">加为好友</div></div>');
	var send_stake_btn	= $('<div id="send_stake_btn"><div id="send_stake_text">赠送好友</div></div>');
	var info_text		= $('<div id="info_text">信   息</div>')
	var send_val		= $('<span id="send_amount"></span>');
	var closeBtn 		= $('<span class="closeBtn">X</span>');

	portrait_box.appendTo(dialog_content);
	info_text.appendTo(dialog_content);
	username.appendTo(dialog_content);
	family.appendTo(dialog_content);
	level.appendTo(dialog_content);
	position.appendTo(dialog_content);
	asset.appendTo(dialog_content);
	family_score.appendTo(dialog_content);
	family_glory.appendTo(dialog_content);
	percentage.appendTo(dialog_content);
	max_reward.appendTo(dialog_content);
	total_games.appendTo(dialog_content);
	// won_games.appendTo(dialog_content);
	last_login.appendTo(dialog_content);
	closeBtn.appendTo(dialog_content);
	head_portrait.appendTo(portrait_box);

	add_friend_btn.appendTo(dialog_bottom);
	send_stake_btn.appendTo(dialog_bottom);
	send_val.appendTo(dialog_content);
	var presentBar = slider_bar();
	
			
	dialog_content.appendTo(dialog);
	dialog_bottom.appendTo(dialog);
	
	dialog.init = function(){
		dialog.appendTo($('#container'));
		presentBar.setVar(changeNum);
		presentBar.setPosition(170,363);
		presentBar.create(dialog_content,1,100,1);
		
	};
	function changeNum(num) {
		
	}
	
	dialog.show = function(player){
		dialog_content.css("display","block");
		dialog_bottom.css("display","block");
		head_portrait.attr('src', player.head_portrait);
		username.text('ID名称：'+player.username);	
		family.text('家族：'+player.family);	
		position.text('职位：'+player.position);	
		level.text('等级：'+player.level);	
		asset.text('资产：'+player.asset);	
		family_score.text('家族积分：'+player.family_score);
		family_glory.text('家族荣誉：'+player.family_glory);
		percentage.text('胜率：'+player.percentage);
		max_reward.text('赢得最大赌注：'+player.max_reward);
		total_games.text('胜利局数/总局数：'+player.total_game+"/"+player.won_game);
		// won_games.text('胜利局数：'+player.won_games);
		last_login.text('最近上线时间：'+player.last_login);
		dialog.addClass(display_css);
		presentBar.setVar(function(value){
			send_val.html("$" + value);
		});
		presentBar.set_argument(1,window.user_info.asset,1); //TODO Make a better amount
	
	};
	dialog.hide	= function(){
		dialog_content.hide();
		dialog_bottom.hide();
	};
	add_friend_btn.bind(event_click,function(){
		console.log("add_friend_btnt.click");

		$.ajax({
			type: 'post',
			data: {"user_id": window.SelectedSeat.userid},
			url	: '/buddy-info/add',
			success:function(recvInfo){
				message_box.showMessage(recvInfo.status,2);
			},
			dataType:'json'
		});
	});	
	send_stake_btn.click(function(){
		console.log("send_stake_btnt.click");
	});	
	window.player_info = dialog;

})($);
