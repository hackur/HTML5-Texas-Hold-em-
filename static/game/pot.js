
(function(pot_manager,$){
	

	var cur_pot = -1;
	var pot_amounts = [];
	var pots = {};
	var pot_container;

	function init(){
		pot_container = $('<div class="potWrapper" align="center"></div>');
		pot_container.appendTo($("#container"));
	}
	$(init);

	function create_pot(pid){
		var potObj = {};
		potObj.pid = pid;
		
		var new_pot = $("<span class='potSpan'></span>");
		var new_coin = $("<img class='potChip'></img>");
		var new_amount = $("<span></span>");
		//new_coin.hide();
		new_amount.appendTo(new_pot);
		new_coin.appendTo(new_pot);
		new_pot.appendTo(pot_container);
		pots[pid] = potObj;
		potObj.coinElement = new_coin;
		potObj.amountElement = new_amount;
		potObj.potElement = new_pot;
		potObj.amount = 0;
		new_amount.html(potObj.amount);
		potObj.setAmount = function(amount){
			potObj.amount = amount;
			new_amount.html(potObj.amount);
		}
		return potObj;
	}
	function make_coin_animation(startOffset,destOffset,img,
						coinElement,chip){
		var coin = $('<div class="chip"></div>');
		coin.css("background-image",img);
		coin.css("left",startOffset.left +"px");
		coin.css("top",startOffset.top +"px");
		coin.appendTo($("#bd"));

		setTimeout(function(){
			coin.bind(eventTransitionEnd,function(){
				coin.remove();
				coinElement.css("background-image",img);
			});
			chip.remove();
			coin.css("left",destOffset.left +"px");
			coin.css("top",destOffset.top +"px");
		},1);
	}
	function make_coin_distribute_animation(startOffset,destOffset,img){
		var coin = $('<div class="chip"></div>');
		coin.css("background-image",img);
		coin.css("left",startOffset.left +"px");
		coin.css("top",startOffset.top +"px");
		coin.appendTo($("#bd"));

		setTimeout(function(){
			coin.bind(eventTransitionEnd,function(){
				coin.remove();
			});
			coin.css("left",destOffset.left +"px");
			coin.css("top",destOffset.top +"px");
		},1);
	}
	function distribute(userid,pid){
		var seat = getSeatById(userid);
		var destOffset = seat.getSeatDIV().offset();
		var potObj = pots[pid];
		var startOffset = potObj.coinElement.offset();
		make_coin_distribute_animation(startOffset,destOffset,
				potObj.coinElement.css("background-image"));
	}

	function collect_coin(pot,users){
		$.each(users,function(index,userid){
			$.each(SeatList,function(index,seat){
				if(seat.userid == userid){
					var chips = seat.getChips();
					$.each(chips,function(index,chip){
						var startOffset = chip.offset();
						var destOffset = pot.coinElement.offset();	
						var img = chip.css("background-image");
						make_coin_animation(startOffset,destOffset,img,pot.coinElement,chip);
						seat.clearStake();
					});
				}
			});
		});
	}
	function update(pot_info){
		$.each(pot_info,function(index,pot){
			//pot[0] --> users
			//pot[1] --> amount,pid
			var pid = pot[1].pid;
			if(pots[pid]){
				return;
			}
			var newpot = create_pot(pot[1].pid);
			//Create pot
		});
		$.each(pot_info,function(index,pot){
			console.log([index,pot]);
			var pid = pot[1].pid;
			if(pots[pid].amount == pot[1].amount ){
				return;
			}
			pots[pid].setAmount(pot[1].amount);
			collect_coin(pots[pid],pot[0]);
		});
		$.each(SeatList,function(index,seat){
			$.each(seat.getChips(),function(index,chip){
				console.log("removing");
				console.log(chip);
				chip.remove();
			});
			seat.cleanChips();
		});
	}
	function reset(){
		$.each(pots,function(index,pot){
			pot.potElement.remove();
		});
		pots = {}
		pot_amounts = [];
	}
	function unit_test(){
		var users = [
			["mamingcao",1000,1],
			["mile",1000,2],
			["vencent",1000,3],
			["ting",1000,4]
			];
		$.each(SeatList,function(index,seat){
			if(index >= users.length) return;
			var user = users[index];
			seat.sit(user[0],user[1],user[2]);
			seat.setStake(100,100);
		
		});

		setTimeout(
		function(){

			update([ 
			[ [1,2],{amount:400,pid:1}   ] ,
			[ [1,2],{amount:400,pid:2}   ] ,
			[ [1,2],{amount:400,pid:3}   ] ,
			[ [1,2],{amount:400,pid:4}   ] ,
			
			]);
		},1000);

		setTimeout(
		function(){

		$.each(SeatList,function(index,seat){
			if(index >= users.length) return;
			var user = users[index];
			seat.sit(user[0],user[1],user[2]);
			seat.setStake(100,100);
		
		});
		},1500);


		setTimeout(
		function(){
			update([ 
			[ [1,2],{amount:400,pid:1}   ] ,
			[ [1,2],{amount:400,pid:2}   ] ,
			[ [1,2],{amount:400,pid:3}   ] ,
			[ [1,2],{amount:800,pid:4}   ] ,
			
			]);

		},2000);

		setTimeout(
		function(){
			distribute(1,1);
			distribute(2,2);
			distribute(3,3);
			distribute(4,4);
		},3000);
	}
	/*
	$(function(){
		setTimeout(unit_test,10);
	});
	*/

	pot_manager.update = update;
	pot_manager.distribute = distribute;
	pot_manager.reset = reset;
}(window.pot_manager = window.pot_manager || {} ,jQuery));
