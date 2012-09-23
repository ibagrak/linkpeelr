
var _gaq = _gaq || [];
_gaq.push(['_setAccount', 'UA-18747503-1']);
_gaq.push(['_trackPageview']);

(function() {
  var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
  ga.src = 'https://ssl.google-analytics.com/ga.js';
  var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
})();

var version = getVersion();

function getVersion() {
  	var xhr = new XMLHttpRequest();
  	xhr.open('GET', chrome.extension.getURL('manifest.json'), false);
  	xhr.send(null);
  	var manifest = JSON.parse(xhr.responseText);
  	return manifest.version;
}
						
function peel_all(request, callback) {
	var xhr = new XMLHttpRequest();
  
  xhr.onreadystatechange = function(data) {
  	if (xhr.readyState == 4) {
      if (xhr.status == 200) {
    		var data = JSON.parse(xhr.responseText);
    		var error_code = data[0];
        var ellipses = "";
	
  			/* got a redirect -> set field value to new URL */
				if (error_code == 301 || error_code == 302) {
					if (data[1].length > 50) {
	  					ellipses = "...";
					}

				  callback("<a href='" + data[1] + "'>" + data[1].substr(0,50) + ellipses + "</a>");
				/* got a direct link (e.g. 200) or error code (e.g. 404) doesn't matter) 
		 		 * -> disable "Peel" button
		 		 **/
				} else {
					if (request.url.length > 50) {
  	  					ellipses = "...";
  					}
					/* make link in tooltip clickable */
					callback("<a href='" + request.url + "'>" + request.url.substr(0,50) + ellipses + "</a>");
				}
      } else {
        callback("Oops! Something is wrong..");
        }
      }
    }
  
   	// Note that any URL fetched here must be matched by a permission in
    // the manifest.json file!
    var url = 'http://linkpeelr.appspot.com/api?action=' + request.action + '&url=' + request.url + '&where=' + request.where + '&version=' + version;
    xhr.open('GET', url, true);
    xhr.send();
  };

/**
 * Handles data sent via chrome.extension.sendRequest().
   * @param request Object Data sent in the request.
   * @param sender Object Origin of the request.
   * @param callback Function The method to call when the request completes.
   */
function onRequest(request, sender, callback) {
  if (request.action == 'peel_all') {
    	peel_all(request, callback);
  }
};

// Wire up the listener.
chrome.extension.onRequest.addListener(onRequest);