(function(recharge,$){
	//FB.init({appId: 231740453606973, status: true, cookie: true});
	var items =[
		{index:1, description:"1000 chips", order_info: 201201, orginal_price:"10 Credits", price: "10 Credits"},
		{index:2, description:"2000 chips", order_info: 201202, orginal_price:"20 Credits", price: "19 Credits"},
		{index:3, description:"5000 chips", order_info: 201203, orginal_price:"50 Credits", price: "46 Credits"},
		{index:4, description:"10000 chips", order_info:201204, orginal_price:"100 Credits", price: "90 Credits"},
		{index:5, description:"20000 chips", order_info:201205, orginal_price:"200 Credits", price: "175 Credits"},
		{index:6, description:"50000 chips", order_info:201206, orginal_price:"500 Credits", price: "440 Credits"}
	];
	var commodities = [];

	function Commodity(info){
		var entity = {};
		entity.info= info;
		entity.construct = function(){
			var _itemDes = $('<div></div>');
			var _originalPrice = $('<strike class="oprice"></strike>');
			var _button  = $('<div class="rpurchase"></div>');

			_itemDes.attr('id','convert'+entity.info.index);
			_itemDes.html(entity.info.description);
			
			_originalPrice.html(entity.info.orginal_price);

			_button.attr('id', "rpurchase"+entity.info.index);
			_button.html(entity.info.price);
			_button.bind("vclick", entity.invokeOrder);

			_itemDes.appendTo($("#recharge_frame"));
			_button.appendTo($("#recharge_frame"));
			_originalPrice.appendTo(_itemDes);
		};

		entity.invokeOrder = function(){
			var obj = {
				method:"pay",
				order_info: entity.info.order_info,
				action:"buy_item", 
				dev_purchase_params: {'oscif': true}
			};
			console.log(obj);
			FB.ui(obj, entity.orderCallback);
		};
	
		entity.orderCallback = function(data){
			console.log("order callback [start]");
			console.log(entity.info);
			if (data['order_id']){
				console.log("order done.");
			}else{
				console.log("order cancel.");
			}
			console.log("order callback [end]");
		};

		entity.construct();
		return entity;
	}

	var initCommodity = function(){
		for(var i=0; i < items.length; i++){
			commodities.push(Commodity(items[i]));
		}
		window.commodities = commodities;
	}
	console.log("==================commodities=======================");
	console.log(commodities);
	window.initCommodity = initCommodity;
})({}, jQuery);
