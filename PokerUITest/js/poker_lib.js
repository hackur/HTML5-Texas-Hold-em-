

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

		if(rank == "T")
			_rank = "10";
		else
			_rank = rank;

		return "./img/pokers/" + _suit + "/" + _rank + ".png";
	};

	poker_lib.getCard = getCard;

}(window.poker_lib = window.poker_lib || {}, jQuery));