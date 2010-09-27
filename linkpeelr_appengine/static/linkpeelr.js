/*
 * Created on Sep 23, 2010
 *
 *   @author: ibagrak
 */

$(document).ready(function() {
	$("#main_input").focus();
	
	$("#main_form").submit(function () { return false; });
	
	$(":button").click(function() {
		$("#main_input").focus();
	});
	
	$("#follow_button").click(function() {
		if ($("#main_input").val() != '') {
			window.location = $("#main_input").val()
		}
	});
	
	$("#peel_button").click(function() {
		var kvs = {}
		
		function callback(result) {
			var error_code = result[0];
			
			/* got a redirect -> set field value to new URL */
			if (error_code == 301 || error_code == 302) {
				$("#main_input").val(result[1]); 
			/* got either a direct link (could be 404, doesn't matter) 
			 * -> disable "Peel" button
			 * */
			} else {
				$("#peel_button").attr("disabled", "disabled");
			}
		}

		kvs['action'] = 'peel';
		kvs['url'] = $("#main_input").val();
		
		if (kvs['url'] != '') {
			$.ajax({
		  		type: 'GET',
		  		url: "/api",
		  		data: kvs,
		  		success: callback,
		  		dataType: "json",
			});
		} 
	});
	
	$("#main_input").keyup(function() {
		$("#peel_button").removeAttr("disabled");
	});
});