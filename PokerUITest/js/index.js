

			var Animation=(function(document,$){
				var document=document,
					$=$,
					chipsOnTable=[];


				var
				sendchip=function(elem){
					$(elem).removeClass('original');
					var len=$(elem).length;
					while(len--){
						$($(elem).get(len)).addClass('show'+len)
					}

				}
				,sendpoker=function(elem){
					$(elem).removeClass('hiddenpoker');
					var len=$(elem).length;
					while(len--){
						$($(elem).get(len)).addClass('show'+len)
					}
				}
				,sendchiptomiddle=function(){

				}


				return {
					sendchip:sendchip,
					sendpoker:sendpoker
				}
			})(document,$,undefined);

			var table_init = function() {
				setTimeout(function(){Animation.sendchip(
					$(".chipcontainer img")
				);},2000);
				/*setTimeout(function(){
					Animation.sendpoker($(".middleContainer img"))
				},5000);*/

				$('.go_on').click(function() {
					send_three_cards();
					Animation.sendpoker($(".middleContainer img"));
				});
			
			};
			
			/* */
			var send_three_cards = function() {
				var _card0 = $("#card0")[0];
				var _card1 = $("#card1")[0];
				var _card2 = $("#card2")[0];

				//should be modified, not hard code, instead, get data from server-side
				var _card0URL = poker_lib.getCard("S", "A");
				var _card1URL = poker_lib.getCard("S", "J");
				var _card2URL = poker_lib.getCard("D", "T");	//"T" -> "10"

				_card0.setAttribute("src", _card0URL);
				_card1.setAttribute("src", _card1URL);
				_card2.setAttribute("src", _card2URL);
			};
