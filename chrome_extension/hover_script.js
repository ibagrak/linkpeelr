/*
 * Created on Sep 28, 2010
 *
 *   @author: ibagrak
 *   
 *   Used parts of TipTip tooltip code (license below)
 *   Used parseUri script (license below)
 */

/*
 * TipTip
 * Copyright 2010 Drew Wilson
 * www.drewwilson.com
 * code.drewwilson.com/entry/tiptip-jquery-plugin
 *
 * Version 1.3   -   Updated: Mar. 23, 2010
 *
 * This Plug-In will create a custom tooltip to replace the default
 * browser tooltip. It is extremely lightweight and very smart in
 * that it detects the edges of the browser window and will make sure
 * the tooltip stays within the current window size. As a result the
 * tooltip will adjust itself to be displayed above, below, to the left 
 * or to the right depending on what is necessary to stay within the
 * browser window. It is completely customizable as well via CSS.
 *
 * This TipTip jQuery plug-in is dual licensed under the MIT and GPL licenses:
 *   http://www.opensource.org/licenses/mit-license.php
 *   http://www.gnu.org/licenses/gpl.html
 */

//parseUri 1.2.2
//(c) Steven Levithan <stevenlevithan.com>
//MIT License

var imgURL = chrome.extension.getURL("ajax-loader.gif");
var animation = "<img src='" + imgURL + "'/>";

var defaults = { 
		activation: "hover",
		keepAlive: false,
		maxWidth: "300px",
		edgeOffset: 3,
		defaultPosition: "bottom",
		delay: 400,
		fadeIn: 200,
		fadeOut: 200,
		attribute: "title",
		content: false, // HTML or String to fill TipTIp with
	  	enter: function(){},
	  	exit: function(){}
  	};

var opts = defaults;
var timeout = false;

function parseUri (str) {
	var	o   = parseUri.options,
		m   = o.parser[o.strictMode ? "strict" : "loose"].exec(str),
		uri = {},
		i   = 14;

	while (i--) uri[o.key[i]] = m[i] || "";

	uri[o.q.name] = {};
	uri[o.key[12]].replace(o.q.parser, function ($0, $1, $2) {
		if ($1) uri[o.q.name][$1] = $2;
	});

	return uri;
};

parseUri.options = {
	strictMode: false,
	key: ["source","protocol","authority","userInfo","user","password","host","port","relative","path","directory","file","query","anchor"],
	q:   {
		name:   "queryKey",
		parser: /(?:^|&)([^&=]*)=?([^&]*)/g
	},
	parser: {
		strict: /^(?:([^:\/?#]+):)?(?:\/\/((?:(([^:@]*)(?::([^:@]*))?)?@)?([^:\/?#]*)(?::(\d*))?))?((((?:[^?#\/]*\/)*)([^?#]*))(?:\?([^#]*))?(?:#(.*))?)/,
		loose:  /^(?:(?![^:@]+:[^:@\/]*@)([^:\/?#.]+):)?(?:\/\/)?((?:(([^:@]*)(?::([^:@]*))?)?@)?([^:\/?#]*)(?::(\d*))?)(((\/(?:[^?#](?![^?#\/]*\.[^?#\/.]+(?:[?#]|$)))*\/?)?([^?#\/]*))(?:\?([^#]*))?(?:#(.*))?)/
	}
};

function active_tiptip(control, html_contents){
	
	// Setup tip tip elements and render them to the DOM
 	if($("#tiptip_holder").length <= 0){
 		var tiptip_holder = $('<div id="tiptip_holder" style="max-width:'+ opts.maxWidth +';"></div>');
		var tiptip_content = $('<div id="tiptip_content"></div>');
		var tiptip_arrow = $('<div id="tiptip_arrow"></div>');
		$("body").append(tiptip_holder.html(tiptip_content).prepend(tiptip_arrow.html('<div id="tiptip_arrow_inner"></div>')));
	} else {
		var tiptip_holder = $("#tiptip_holder");
		var tiptip_content = $("#tiptip_content");
		var tiptip_arrow = $("#tiptip_arrow");
	}
 
	tiptip_content.html(html_contents);

	tiptip_holder.hide().removeAttr("class").css("margin","0");
	tiptip_arrow.removeAttr("style");
	
	var top = parseInt(control.offset()['top']);
	var left = parseInt(control.offset()['left']);
	var org_width = parseInt(control.outerWidth());
	var org_height = parseInt(control.outerHeight());
	var tip_w = tiptip_holder.outerWidth();
	var tip_h = tiptip_holder.outerHeight();
	var w_compare = Math.round((org_width - tip_w) / 2);
	var h_compare = Math.round((org_height - tip_h) / 2);
	var marg_left = Math.round(left + w_compare);
	var marg_top = Math.round(top + org_height + opts.edgeOffset);
	var t_class = "";
	var arrow_top = "";
	var arrow_left = Math.round(tip_w - 12) / 2;

    if(opts.defaultPosition == "bottom"){
    	t_class = "_bottom";
   	} else if(opts.defaultPosition == "top"){ 
   		t_class = "_top";
   	} else if(opts.defaultPosition == "left"){
   		t_class = "_left";
   	} else if(opts.defaultPosition == "right"){
   		t_class = "_right";
   	}
	
	var right_compare = (w_compare + left) < parseInt($(window).scrollLeft());
	var left_compare = (tip_w + left) > parseInt($(window).width());
	
	if((right_compare && w_compare < 0) || (t_class == "_right" && !left_compare) || (t_class == "_left" && left < (tip_w + opts.edgeOffset + 5))){
		t_class = "_right";
		arrow_top = Math.round(tip_h - 13) / 2;
		arrow_left = -12;
		marg_left = Math.round(left + org_width + opts.edgeOffset);
		marg_top = Math.round(top + h_compare);
	} else if((left_compare && w_compare < 0) || (t_class == "_left" && !right_compare)){
		t_class = "_left";
		arrow_top = Math.round(tip_h - 13) / 2;
		arrow_left =  Math.round(tip_w);
		marg_left = Math.round(left - (tip_w + opts.edgeOffset + 5));
		marg_top = Math.round(top + h_compare);
	}

	var top_compare = (top + org_height + opts.edgeOffset + tip_h + 8) > parseInt($(window).height() + $(window).scrollTop());
	var bottom_compare = ((top + org_height) - (opts.edgeOffset + tip_h + 8)) < 0;
	
	if(top_compare || (t_class == "_bottom" && top_compare) || (t_class == "_top" && !bottom_compare)){
		if(t_class == "_top" || t_class == "_bottom"){
			t_class = "_top";
		} else {
			t_class = t_class+"_top";
		}
		arrow_top = tip_h;
		marg_top = Math.round(top - (tip_h + 5 + opts.edgeOffset));
	} else if(bottom_compare | (t_class == "_top" && bottom_compare) || (t_class == "_bottom" && !top_compare)){
		if(t_class == "_top" || t_class == "_bottom"){
			t_class = "_bottom";
		} else {
			t_class = t_class+"_bottom";
		}
		arrow_top = -12;						
		marg_top = Math.round(top + org_height + opts.edgeOffset);
	}

	if(t_class == "_right_top" || t_class == "_left_top"){
		marg_top = marg_top + 5;
	} else if(t_class == "_right_bottom" || t_class == "_left_bottom"){		
		marg_top = marg_top - 5;
	}
	if(t_class == "_left_top" || t_class == "_left_bottom"){	
		marg_left = marg_left + 5;
	}
	tiptip_arrow.css({"margin-left": arrow_left+"px", "margin-top": arrow_top+"px"});
	tiptip_holder.css({"margin-left": marg_left+"px", "margin-top": marg_top+"px"}).attr("class","tip"+t_class);
	
	if (timeout){ clearTimeout(timeout); }
	timeout = setTimeout(function(){ tiptip_holder.stop(true,true).fadeIn(opts.fadeIn); }, opts.delay);	
};

function deactive_tiptip(){
	var tiptip_holder = $("#tiptip_holder");
	var tiptip_content = $("#tiptip_content");
	var tiptip_arrow = $("#tiptip_arrow");
	
	if (timeout){ clearTimeout(timeout); }
	tiptip_holder.fadeOut(opts.fadeOut);
};


var x;
var y;

$(document).ready(function() {
	
	$("body").mousemove(function (event) {
		x = event.pageX; 
		y = event.pageY;
	});
	
	$("a").live('click', function(event) {
		deactive_tiptip();
	});
	
	// Ignore links which already show a Twitter @anywhere popup on mouseover
	$("a:not(.twitter-anywhere-user)").live('mouseover mouseout', function(event) {
		// on mouseover
		if (event.type == 'mouseover') {
			var control = $(this);
			var href = control.attr('href');
			
			if (typeof(href) == "undefined" || href === '') {
				return;
			}
			
			if (href != null && href.length > 0) {
				// what we ignore: 
				// self referential
				if (href.charAt(0) == '#') {
					return;
				// relative 
				} else if (href.charAt(0) == '/' || href.charAt(0) == '.') {
					return;
				// // secure
				// } else if (href.length > 5 && href.substr(0, 5) == 'https') {
				// 	return;
				// another protocol
				} else if (href.length > 4 && href.substr(0, 4) != 'http') {
					return;
				} 
				
				// don't peel long URLs
				if (href.length > 30) {
					return;
				}
				
				// shortened urls never end in '/'
				if (href.charAt(href.length - 1) == '/') {
					return;
				}
				
				// don't peel long domain names, they are almost always direct. 
				// host without a dot typically means relative URL
				var url_parts = parseUri(href);
				if (url_parts['host'].length > 11 || url_parts['host'].indexOf('.') == -1) {
					return;
				}
				
				if (/imgur.com$/.test(url_parts['host'])) {
					return;
				}
				
				// don't peel for search engine pages
				if (window.location.host.indexOf('google') != -1 || 
					window.location.host.indexOf('yahoo') != -1 || 
					window.location.host.indexOf('bing') != -1) {
					return;
				}
				
				// within the domain
				if (window.location.host == url_parts['host']) {
					return;
				}
			}
			
			control.removeAttr('title');
			
			if (control.attr("linkpeelr_cache")) {
				active_tiptip(control, control.attr("linkpeelr_cache"));	
				return;
			} 
			
			active_tiptip(control, animation)			
				
			/* callback for ajax peel */
			function callback(result) {
				control.attr("linkpeelr_cache", result);
				
				var top = parseInt(control.offset()['top']);
				var left = parseInt(control.offset()['left']);
				var org_width = parseInt(control.outerWidth());
				var org_height = parseInt(control.outerHeight());
				
				if (y >= top && y <= top + org_height && x >= left && x <= left + org_width) {
					active_tiptip(control, result);
				}
			}
			
			chrome.extension.sendRequest({'action' : 'peel_all', 'url' : href, 'where' : window.location.host}, callback);
				
		// on mouseout
		} else if (event.type == 'mouseout') {
			deactive_tiptip();
		} 
	});
});