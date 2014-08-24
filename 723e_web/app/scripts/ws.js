define("ws", ["jquery"], function($) {
	// Define API Server
	var server = {
		protocol: "http",
		domain: "localhost",
		port: "8000",
		url: function() {
			return this.protocol + "://" + this.domain + ":" + this.port;
		}
	};

	// This service describe remote API
	var init = server.url() + "/api/v1/init/";

	var v1 = {
		// List all user accounts
		accounts: server.url() + "/api/v1/accounts/",
		// Get token key
		login: server.url() + "/api/api-token-auth/"
	}

	// Authentification Token Key
	var key = sessionStorage.getItem("key");

	var _setToken = function(_key) {
		key = _key;
		sessionStorage.setItem("key", _key);
	}

	var _ajax = function(type, _options) {

		// list configuration
		options = $.extend({
			type: type,
			beforeSend: function(xhr) {
				if (key !== null && key != undefined) {
					xhr.setRequestHeader('Authorization', 'Token ' + key);
				}
			}
		}, _options);

		console.log(options);

		return $.ajax(options);
	}

	var _get = function(_options) {
		return _ajax('GET', _options);
	}
	var _post = function(_options) {
		return _ajax('POST', _options);
	}
	var _push = function(_options) {
		return _ajax('PUSH', _options);
	}
	var _delete = function(_options) {
		return _ajax('DELETE', _options);
	}

	return {
		// This object return server access.
		init: init,
		v1: v1,
		get: _get,
		post: _post,
		push: _push,
		del: _delete,
		setToken: _setToken
	}
});
