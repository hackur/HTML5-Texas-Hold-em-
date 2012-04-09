


(function(game_control, $, undefined){

	var deal = function() {
		/* draw roundRec time bar here*/

		$('#btCall').click(function() {			
			if($("#card0")[0].src == "" || $("#card1")[0].src == "" || $("#card2")[0].src == "")
			{
				ante_chips("#chip0", "215px", "320px", function() {
					ante_chips("#chip4", "150px", "80px", function() {
						ante_chips("#chip3", "390px", "80px", function() {
							ante_chips("#chip2", "580px", "80px", function() {
								ante_chips("#chip1", "700px", "320px", function() {
									collect_chips();
									round_one();
								});
							})
						});
					});
				});

			}
			else 
			{
				if($("#card3")[0].src == "")
				{
					round_two();				
				}
				else
				{	
					if($("#card4")[0].src == "")
					{
						round_three();
					}
				}
			}
		});

	};

	var collect_chips = function() {
		for(var i = 0; i <= 4; i++ )
		{
			$("#chip" + i ).animate(
				{
					left: "750px",
					top: "180px"
				},
				{
					duration: "slow"
				}
			);
		}		
	};

	var ante_chips = function(chipId, ileft, itop, callback) {
		$(chipId).show();
		$(chipId).animate(
			{
				left: ileft,
				top: itop
			},
			{
				duration: 'fast',
				complete: function() {
					if(callback) { callback(); }
				}
			}
		);
		
	};

	var round_one = function() {
		

		get_three_cards();
		$("#card0").fadeIn("fast", function() {
			$("#card1").fadeIn("fast", function() {
				$("#card2").fadeIn("fast");
			});
		});
	};

	var round_two = function() {
		get_one_card($("#card3")[0], "D", "K");
		$("#card3").fadeIn("fast");	
	};

	var round_three = function() {
		get_one_card($("#card4")[0], "S", "T");
		$("#card4").fadeIn("fast");
	}

	/* */
	var get_three_cards = function() {
		var _card0 = $("#card0")[0];
		var _card1 = $("#card1")[0];
		var _card2 = $("#card2")[0];

		//should be modified, not hard code, instead, get data from server-side
		var _card0URL = poker_lib.getCard("S", "A");
		var _card1URL = poker_lib.getCard("S", "J");
		var _card2URL = poker_lib.getCard("D", "2");

		_card0.setAttribute("src", _card0URL);
		_card1.setAttribute("src", _card1URL);
		_card2.setAttribute("src", _card2URL);
	};

	var get_one_card = function(elem, suit, rank) {
		var _cardUrl = poker_lib.getCard(suit, rank);
		elem.setAttribute("src", _cardUrl);
	};

	game_control.deal = deal;

}(window.game_control = window.game_control || {}, jQuery));