/*
 * Created on Sep 23, 2010
 *
 *   @author: ibagrak
 */
var headline_count;
var headline_interval;
var current_headline = 0;
var old_headline = 0;

$(document).ready(function() {
	headline_count = $("div.headline").size();
	$("div.headline:eq("+current_headline+")").css('top', '0px');
	
	headline_interval = setInterval(headline_rotate, 3000);
	$('#test_scroller').hover(function() {
		clearInterval(headline_interval);
	}, function() {
		headline_interval = setInterval(headline_rotate, 3000);
		headline_rotate();
	});
	
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
	
	$("#ext_button").click(function() {
		window.location = $("#ext_button").attr("href");
	});
	
	$("#peel_button").click(function() {
		var kvs = {}
		
		function callback(result) {
			var error_code = result[0];
			
			/* got a redirect -> set field value to new URL */
			if (error_code == 301 || error_code == 302) {
				$("#main_input").val(result[1]); 
			/* got a direct link (e.g. 200) or error code (e.g. 404) doesn't matter) 
			 * -> disable "Peel" button
			 * */
			} else {
				$("#peel_button").attr("disabled", "disabled");
			}
		}

		kvs['action'] = 'peel';
		kvs['url'] = $("#main_input").val();
		kvs['where'] = 'linkpeelr.appspot.com';
		kvs['version'] = '1.7.6';
		
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

function headline_rotate() {
	current_headline = (old_headline + 1) % headline_count;
	
	function callback(result) {
		var error_code = result[0];
		if (error_code == 0) {
			var exists = false;
			var key = result[1][0];

			$(".headline").each(function(index) {
				if ($(this).attr("id") == key) {
					exists = true;
				} 
			});
			
			if (!exists) {
				var unpeeled = result[1][1]; 
				var peeled = result[1][2]; 
				var where = result[1][3]; 
				var ip = result[1][4]; 
				
				var ellipses = "";
				
				if (peeled.length > 50) {
	  				ellipses = "...";
				}
				
				$("div.headline:eq(" + current_headline + ")").html(
						'<span class="from" style="font-size:small"><a href="' + unpeeled + '">' + unpeeled + '</a></span> <br> \
						&dArr;<br> \
						<span class="to"><a href="' + peeled + '">' + peeled.substr(0,50) + ellipses + '</a></span><br> \
						<div id="peeled_info">peeled while browsing <em>' + where + '</em> in ' + 
						'<img style="vertical-align:text-top" height="12px" src="http://api.hostip.info/flag.php?ip=' + ip + '"></div>');
				
				$("div.headline:eq(" + current_headline + ")").removeClass('empty');
				$("div.headline:eq(" + current_headline + ")").attr('id', key)
			}
		} 
		
		$("div.headline:eq(" + old_headline + ")")
			.animate({top: -95},"slow", function() {
				$(this).css('top', '95px');
			});
		
		$("div.headline:eq(" + current_headline + ")")
			.animate({top: 0},"slow");

		old_headline = current_headline;
	}
	
	kvs = {}
	kvs['action'] = 'last';
	kvs['version'] = '1.7.6';
	
	if (kvs['url'] != '') {
		$.ajax({
	  		type: 'GET',
	  		url: "/api",
	  		data: kvs,
	  		success: callback,
	  		dataType: "json",
		});
	} 
}