define(["jquery", "backbone", "ws"], function($, Backbone, WebServices) {

	var currencies = Backbone.Model.extend({
		urlRoot: WebServices.v1.currencies,
		defaults: {

		},
		initialize: function() {
			//alert("Welcome to this world");
		},
		toString: function(amount){
			return ""+amount+" AMOUNT"
		}
	});

	return currencies;
});
