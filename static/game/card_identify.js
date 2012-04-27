(function($){
	
	function identifyCard(card_list){
		var score	= 0;
		var kicker	= [];
		var pairs	= {};
		var prev	= 0;
		console.log(card_list);
		card_list.sort(function(a,b){return a.rank - b.rank;});
		for(var i=0; i<card_list.length;i++){
			var card= card_list[i];
			if(prev	== card.rank){
				key = card.rank;
				if(pairs[key] != undefined){
					pairs[key] += 1;
				}else{
					pairs[key]	= 2;
				}
			}
			prev	= card.rank;
		}

		var nop = {};
		for(var key in pairs){
			var value = pairs[key];
			console.log(value);
			if(nop[value] != undefined){
				nop[value].count += 1;
				nop[value].keys.push(key);
			}else{
				nop[value] = {count:1, keys:[key]};
			}
		}
		console.log("===================nop=====================");
		console.log(nop[1]);
		console.log(nop[2]);
		console.log(nop[3]);
		console.log(nop[4]);
		console.log(nop[0]);
		console.log("====================end=====================");
		if(nop[4] != undefined){
			score		= 7;
			key			= nop[4].keys[0];
			last_card	= -1;
			for(var i = 0; i < card_list.length; i++){
				var card = card_list[i];
				if(card.rank != key && card.rank > last_card){
					last_card = card.rank;
				}
			}
			return {score:score, kicker:[key, last_card]}
		}else if(nop[3] != undefined){
			if(nop[3].count == 2 || nop[2] != undefined){
				score 		= 6;
				kicker[0]	= -1;
				temp		= null;
				for(var k = 0; k < nop[3].keys.length; k++){
					if(nop[3].keys[k] > kicker[0]){
						kicker[0]	= nop[3].keys[k];
						temp		= k;
					}
				}
				nop[3].keys.splice(temp, 1);
			}else{
				score		= 3;
				kicker[0]	= nop[3].keys[0];
				temp		= [];
				for(var k = 0; k < card_list.length; k++){
					var card = card_list[k];
					if(card.rank != kicker[0]){
						temp.push(card);
					}
				}
				temp.sort(function(a, b){return b.rank - a.rank;});
				kicker.push(temp[0].rank);
				kicker.push(temp[1].rank);
			}
		}else if(nop[2] != undefined){
			if(nop[2].count >= 2){
				score = 2;
				nop[2].keys.sort(function(a, b){return b.rank - a.rank;});
				kicker.push(nop[2].keys[0]);
				kicker.push(nop[2].keys[1]);
				temp	= [];
				for(var k = 0; k < card_list.length; k++){
					var card = card_list[k];
					if(card.rank != kicker[0] && card.rank != kicker[1]){
						temp.push(card);
					}
				}
				temp.sort(function(a, b){return b.rank - a.rank;});
				kicker.push(temp[0]);
			}else{
				score = 1;
				kicker.push(nop[2].keys[0]);
				temp	= [];
				for(var k = 0; k < card_list.length; k++){
					var card = card_list[k];
					if(card.rank != kicker[0]){
						temp.push(card);
					}
				}
				temp.sort(function(a, b){return b.rank - a.rank;});
				kicker.push(temp[0]);
				kicker.push(temp[1]);
				kicker.push(temp[2]);
			}
		}
		var counter = 0;
		var high	= 0;
		var	straight= false;
		if(card_list[card_list.length - 1].rank == 14){
			prev = 1;
		}else{
			prev = null;
		}
		for(var j = 0; j < card_list.length; j++){
			var card = card_list[j];
			console.log(card);
			if(prev != null  && card.rank == (prev + 1)){
				counter += 1;
				console.log(counter);
				if(counter >= 4){
					straight= true;
					high	= card.rank;
				}
			}else if(prev != null && prev == card.rank){

			}else{
				counter = 0;
			}
			
			prev	= card.rank;
		}
		if((straight || counter >= 4) && score < 4){
			straight= true;
			score	= 4;
			kicker	= [high];
		}


		var flush	= false;
		var total	= {};
		for(var k = 0; k < card_list.length; k++){
			var suit = card_list[k].suit;
			if(total[suit] != undefined){
				total[suit]	+= 1;
			}else{
				total[suit]	= 1;
			}
		}
		var key		= -1;
		for(var k in total){
			if(total[k] >= 5){
				key = k;
			}
		}

		if(key != -1 && score < 5){
			flush	= true;
			score	= 5;
			temp	= [];
			for(var k = 0; k < card_list.length; k++){
				var card = card_list[k];
				if(card.suit == key){
					temp.push(card.rank);
				}
			}
			temp.sort(function(a,b){return b.rank - a.rank;});
			kicker = temp;	
		}
		if(flush && straight){
			counter			= 0;
			hight			= 0;
			straight_flush	= 0;
			if(kicker[kicker.length - 1] == 14){
				prev = 1;
			}else{
				prev = null;
			}
			for(var k = 0; k < kicker.length; k++){
				var rank = kicker[k];
				if(prev != null && rank == (prev + 1)){
					counter += 1;
					if(counter >= 4){
						straight_flush = true;
						high	= rank;
					}
				}else if(prev!=null && prev == rank){
				}else{
					counter = 0;
				}
				prev = rank;
			}
			if(straight_flush){
				if(high == 14){
					score = 9
				}else{
					score = 8
				}
				kicker = [high];
				return {score:score, kicker:kicker}
			}
		}
		if(flush){
			kicker.sort(function(a,b){return b-a});
			length	= kicker.length -5;
			kicker.splice(5, length);
		}
		if(score == 0){
			for(var j = 0; j < card_list.length; j++){
				kicker.push(card_list[j].rank);
			}
			kicker.sort(function(a,b){return b-a});
			length	= kicker.length -5;
			kicker.splice(5, length);
		}
		return {score:score, kicker:kicker}
	}
	function getHandCardName(handCard){
		switch(handCard.score){
			case 0:
				return "高牌";
			case 1:
				return "一对";
			case 2:
				return "两对";
			case 3:
				return "三条";
			case 4:
				return "顺子";
			case 5:
				return "同花";
			case 6:
				return "满堂红";
			case 7:
				return "四條";
			case 8:
				return "同花顺";
			case 9:
				return "皇家同花顺";
		}
	}
	window.identifyCard 	= identifyCard;
	window.getHandCardName	= getHandCardName;
})($);
