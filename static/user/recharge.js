(function(recharge,$){
	FB.init({appId: <your_app_id>, status: true, cookie: true});
	var items =[
		{index:1, description:"10000 Credits", order_info:"recharge_1"},
		{index:2, description:"20000 Credits", order_info:"recharge_2"},
		{index:3, description:"50000 Credits", order_info:"recharge_3"},
		{index:4, description:"100000 Credits", order_info:"recharge_4"}
	];
	var commodities = [];

	function Commodity(info){
		var entity = {};
		entity.info= info;
		entity.construct = function(){
			console.log("------------construction--------------");
			console.log(entity.info);
			var _itemDes = $('<div></div>');
			var _button  = $('<div class="rpurchase"></div>');

			_itemDes.attr('id','convert'+entity.info.index);
			_itemDes.html(entity.info.description);
			
			_button.attr('id', "rpurchase"+entiry.info.index);
			_button.html("Purchase");
			_button.bind("vclick", entity.invokeOrder);
			
			$("#recharge_frame").append(_itemDes);
			$("#recharge_frame").append(_button);
		};

		entity.invokeOrder = function(){
			var obj = {
				method:"pay",
				order_info: entity.info.order_info,
				action:"buy_item", 
				dev_purchase_params: {'oscif': true}
			};
			FB.ui(obj, orderCallback);
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
	for(var i=0; i < items.length; i++){
		commodities.push(Commodity(items[i]));
	}
	window.commodities = commodities;
})(window.recharge = window.recharge || {}, jQuery);
