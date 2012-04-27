

(function(poker_lib, $, undefined) {

	var getCard = function(suit, rank) {
		var _suit;
		var _rank;

		switch(suit) {
			case "S": _suit = "spade";
				break;
			case "H": _suit = "heart";
				break;
			case "D": _suit = "diamond";
				break;
			case "C": _suit = "club";
				break;
			default:
				console.log("No such a poker.");
				break;
		}
		
		_rank = rank;

		return "./pokers/" + _suit + "/" + _rank + ".png";
	};

	var setCard = function(card, cardDivId) {
		var _suit;
		var _rank;

		console.log(card);
		if (card.length == 2) {
			_suit = card.charAt(1);
			_rank = card.charAt(0);
		}
		else if (card.length == 3) {
			_suit = card.charAt(2);
			_rank = "10";
		}
		if (card.length != 2 && card.length != 3) {
			console.log("ERROR!!!");
			return;
		}
		console.log(_suit + " " + _rank);
		$(cardDivId)[0].src = getCard(_suit, _rank);
	};

	poker_lib.setCard = setCard;
	poker_lib.getCard = getCard;

}(window.poker_lib = window.poker_lib || {}, jQuery));

