define([
	'jquery',
	'underscore',
	'backbone',
	'mustache',
	'initView',
	'text!templates/transactions.mustache',
	'text!templates/transactions/debitscreditsForm.mustache',
	'debitsCreditsModel',
	'debitsCreditsCollection',
	'text!templates/transactions/changesForm.mustache',
	'changesModel',
	'currenciesCollection',
	'text!templates/transactions/list.mustache',
	'categoryCollection',
	'text!templates/transactions/dateSelectPage.mustache'
], function(
	$,
	_,
	Backbone,
	Mustache,
	InitView,
	TransactionsTemplate,
	DebitsCreditsFormTemplate,
	DebitsCreditsModel,
	DebitsCreditsCollection,
	ChangesFormTemplate,
	ChangesModel,
	CurrenciesCollection,
	listTemplate,
	CategoryCollection,
	DateSelectorPageTemplate) {

	var currencies = new CurrenciesCollection();
	var categories = new CategoryCollection();

	var arrayAbstract = [];
	var nbSource = 0;

	var DashboardView = Backbone.View.extend({
		el: $("#content"),

		displayForm: function(year, month, change){
			var template = Mustache.render(ChangesFormTemplate, {
				change: change,
				currencies: currencies.toJSON(),
				categories: categories.toJSON()
			});
			$("#content").html(template);

			// Put select markup as selected
			if (change) {
				$("#changes_form select[name='currency']").find('option[value="' + change.currency + '"]').attr('selected', true);
				$("#changes_form select[name='new_currency']").find('option[value="' + change.new_currency + '"]').attr('selected', true);
				$("#changes_form select[name='category']").find('option[value="' + change.category + '"]').attr('selected', true);
			}

			var view = this;
			// User cancel form. We go back to view page.
			$("button.changes_form_cancel").on("click", function() {
				Backbone.history.navigate("#/transactions/"+year+"/"+month, {
					trigger: true
				});
			});

			$("button.changes_form_submit").on("click", function() {

				var array = $("#changes_form").serializeArray();
				var dict = {};

				for (var i = 0; i < array.length; i++) {
					dict[array[i]['name']] = array[i]['value']
				}
				dict['user'] = "http://localhost:8000/api/v1/users/1";

				var change = new ChangesModel(dict);

				change.save(dict, {
					wait: true,
					success: function(model, response) {
						console.log('Successfully saved!');
						Backbone.history.navigate("#/transactions/"+year+"/"+month, {
							trigger: true
						});
					},
					error: function(model, error) {
						console.log(model.toJSON());
						console.log('error.responseText');
					}
				});

			});

		},

		render: function(year, month, change_id) {
			var initView = new InitView();
			if (initView.isLoaded() === false) {
				initView.render();
			}

			initView.changeSelectedItem("nav_transactions");

			var view = this;

			currencies.fetch({
				success: function() {
					categories.fetch({
						success: function() {
							if(change_id){
								var change = new ChangesModel({id: change_id});
								change.fetch({
							        success: function (c) {
							            view.displayForm(year, month, change.toJSON());
							        }
							    });
							}else{
								view.displayForm(year, month);
							}
						}
					});
				}
			});
		}
	});

	return DashboardView;

});