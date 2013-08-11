PREFIX = gae
APP_ID = linkpeelr-hrd
VERSION = 2.1.0

predeploy: config_remote

test:
	@export SERVER_SOFTWARE=Dev ; export APPLICATION_ID=$(APP_ID) ; cd $(PREFIX) ; python tests/testrunner.py /usr/local/google_appengine . 

local: local_app local_ext

local_app: 
	mustache local.yml $(PREFIX)/static/js/script.js.mustache > $(PREFIX)/static/js/script.js

	cd $(PREFIX)/static ; cat ./js/bs/bootstrap-transition.js ./js/bs/bootstrap-alert.js ./js/bs/bootstrap-button.js ./js/bs/bootstrap-carousel.js ./js/bs/bootstrap-collapse.js ./js/bs/bootstrap-dropdown.js ./js/bs/bootstrap-modal.js ./js/bs/bootstrap-tooltip.js ./js/bs/bootstrap-popover.js ./js/bs/bootstrap-scrollspy.js ./js/bs/bootstrap-tab.js ./js/bs/bootstrap-typeahead.js ./js/bs/bootstrap-affix.js ./js/plugins.js ./js/script.js > js/site.js
	cd $(PREFIX)/static ; ./node_modules/.bin/lessc --compress ./css/less/bootstrap.less > css/bootstrap.css ; ./node_modules/.bin/lessc --compress ./css/less/responsive.less > css/responsive.css ; cat css/h5bp.css > css/site.css ;  cat css/bootstrap.css >> css/site.css; ./node_modules/.bin/lessc --compress ./css/less/font-awesome-ie7.less > ./css/font-awesome-ie7.css

local_ext: 
	mustache local.yml chrome_extension/background.js.mustache > chrome_extension/background.js
	mustache local.yml chrome_extension/manifest.json.mustache > chrome_extension/manifest.json

remote: remote_app remote_ext

remote_app:
	mustache remote.yml $(PREFIX)/static/js/script.js.mustache > $(PREFIX)/static/js/script.js

	cd $(PREFIX)/static ; cat ./js/bs/bootstrap-transition.js ./js/bs/bootstrap-alert.js ./js/bs/bootstrap-button.js ./js/bs/bootstrap-carousel.js ./js/bs/bootstrap-collapse.js ./js/bs/bootstrap-dropdown.js ./js/bs/bootstrap-modal.js ./js/bs/bootstrap-tooltip.js ./js/bs/bootstrap-popover.js ./js/bs/bootstrap-scrollspy.js ./js/bs/bootstrap-tab.js ./js/bs/bootstrap-typeahead.js ./js/bs/bootstrap-affix.js ./js/plugins.js ./js/script.js > js/combined.js; ./node_modules/.bin/uglifyjs js/combined.js > js/site.js
	cd $(PREFIX)/static ; ./node_modules/.bin/lessc --compress ./css/less/bootstrap.less > css/bootstrap.css ; ./node_modules/.bin/lessc --compress ./css/less/responsive.less > css/responsive.css ; cat css/h5bp.css > css/site.css ;  cat css/bootstrap.css >> css/site.css; ./node_modules/.bin/lessc --compress ./css/less/font-awesome-ie7.less > ./css/font-awesome-ie7.css

remote_ext: 
	mustache remote.yml chrome_extension/background.js.mustache > chrome_extension/background.js
	mustache remote.yml chrome_extension/manifest.json.mustache > chrome_extension/manifest.json

clean: clean_app clean_ext 

clean_ext: 
	rm -f chrome_extension/background.js
	rm -f chrome_extension/manifest.json
	
clean_app:
	rm -f $(PREFIX)/static/js/script.js
	rm -f $(PREFIX)/static/js/site.js
	rm -f $(PREFIX)/static/js/combined.js

	rm -f $(PREFIX)/static/css/bootstrap.css
	rm -f $(PREFIX)/static/css/responsive.css
	rm -f $(PREFIX)/static/css/site.css
	rm -f $(PREFIX)/static/css/font-awesome-ie7.css


