import webapp2
import webtest
import unittest2
import urllib

from google.appengine.ext import testbed
from webapp2_extras import json

import app
import settings
import handlers

class RPCTest(unittest2.TestCase):
	url = 'http://bit.ly/9Uk1wi'
	url2 = 'http://ow.ly/fWklr' # this is a shrunk bit.ly link
	url_peeled = 'http://linkpeelr.appspot.com'
	bad_url = 'http://0.0.0.0'

	where = 'http://www.facebook.com'
	ip = '192.168.0.1'

	def setUp(self):
		# Create a WSGI application.
		application = webapp2.WSGIApplication(app.routes, debug = True, config = settings.app_config)
		application.error_handlers[404] = handlers.common.handle_404
	
		# Wrap the app with WebTest's TestApp.
		self.testapp = webtest.TestApp(application)

		# First, create an instance of the Testbed class.
		self.testbed = testbed.Testbed()

		# Then activate the testbed, which prepares the service stubs for use.
		self.testbed.activate()

		# Next, declare which service stubs you want to use.
		self.testbed.init_memcache_stub()
		self.testbed.init_urlfetch_stub()

	def tearDown(self):
		pass

	def test_peel(self):
		response = self.testapp.get('/rpc/peel?url=%s&where=%s&ip=%s' % 
			(urllib.quote(self.url), urllib.quote(self.where), urllib.quote(self.ip)))
		
		self.assertEqual(response.status_int, 301)
		self.assertEqual(response.content_type, 'application/json')
		self.assertEqual(json.decode(response.body)['code'], 301)
		self.assertEqual(json.decode(response.body)['response']['url'], self.url_peeled)

	def test_peel_bad(self):
		response = self.testapp.get('/rpc/peel?url=%s&where=%s&ip=%s' % 
			(urllib.quote(self.bad_url), urllib.quote(self.where), urllib.quote(self.ip)), expect_errors = True)
		
		self.assertEqual(response.status_int, 402)
		self.assertEqual(response.content_type, 'application/json')
		self.assertEqual(json.decode(response.body)['code'], 402	)

	def test_peel_all(self):
		response = self.testapp.get('/rpc/peel_all?url=%s&where=%s&ip=%s' % 
			(urllib.quote(self.url2), urllib.quote(self.where), urllib.quote(self.ip)))
		
		self.assertEqual(response.status_int, 301)
		self.assertEqual(response.content_type, 'application/json')
		self.assertEqual(json.decode(response.body)['code'], 301)
		self.assertEqual(json.decode(response.body)['response']['url'], self.url_peeled)

	def test_api_bad(self):
		response = self.testapp.get('/rpc/dne?url=%s&where=%s&ip=%s' % 
			(urllib.quote(self.url), urllib.quote(self.where), urllib.quote(self.ip)), expect_errors = True)
		
		self.assertEqual(response.status_int, 400)
		self.assertEqual(response.content_type, 'application/json')
		self.assertEqual(json.decode(response.body)['code'], 400)

	def test_last(self):
		self.test_peel()
		
		response = self.testapp.get('/rpc/last')

		self.assertEqual(response.status_int, 200)
		self.assertEqual(response.content_type, 'application/json')
		self.assertEqual(json.decode(response.body)['code'], 200)
		self.assertEqual(json.decode(response.body)['response']['peeled'], self.url_peeled)

	def test_last_bad(self):
		response = self.testapp.get('/rpc/last', expect_errors = True)

		self.assertEqual(response.status_int, 402)
		self.assertEqual(response.content_type, 'application/json')
		self.assertEqual(json.decode(response.body)['code'], 402)

class LegacyRPCTest(unittest2.TestCase):
	url = 'http://bit.ly/9Uk1wi'
	url2 = 'http://ow.ly/fWklr' # this is a shrunk bit.ly link
	url_peeled = 'http://linkpeelr.appspot.com'
	bad_url = 'http://0.0.0.0'

	where = 'http://www.facebook.com'
	ip = '192.168.0.1'

	def setUp(self):
		# Create a WSGI application.
		application = webapp2.WSGIApplication(app.routes, debug = True, config = settings.app_config)
		application.error_handlers[404] = handlers.common.handle_404
	
		# Wrap the app with WebTest's TestApp.
		self.testapp = webtest.TestApp(application)

		# First, create an instance of the Testbed class.
		self.testbed = testbed.Testbed()

		# Then activate the testbed, which prepares the service stubs for use.
		self.testbed.activate()

		# Next, declare which service stubs you want to use.
		self.testbed.init_memcache_stub()
		self.testbed.init_urlfetch_stub()

	def tearDown(self):
		pass

	def test_peel(self):
		response = self.testapp.get('/api?action=peel&url=%s&where=%s&ip=%s' % 
			(urllib.quote(self.url), urllib.quote(self.where), urllib.quote(self.ip)))
		
		self.assertEqual(response.status_int, 200)
		self.assertEqual(response.content_type, 'application/json')
		self.assertEqual(json.decode(response.body)[0], 301)
		self.assertEqual(json.decode(response.body)[1], self.url_peeled)

	def test_peel_bad(self):
		response = self.testapp.get('/api?action=peel&url=%s&where=%s&ip=%s' % 
			(urllib.quote(self.bad_url), urllib.quote(self.where), urllib.quote(self.ip)), expect_errors = True)
		
		self.assertEqual(response.status_int, 200)
		self.assertEqual(response.content_type, 'application/json')
		self.assertEqual(json.decode(response.body)[0], 3)

	def test_peel_all(self):
		response = self.testapp.get('/api?action=peel_all&url=%s&where=%s&ip=%s' % 
			(urllib.quote(self.url2), urllib.quote(self.where), urllib.quote(self.ip)))
		
		self.assertEqual(response.status_int, 200)
		self.assertEqual(response.content_type, 'application/json')
		self.assertEqual(json.decode(response.body)[0], 301)
		self.assertEqual(json.decode(response.body)[1], self.url_peeled)

	def test_api_bad(self):
		response = self.testapp.get('/api?action=dne&url=%s&where=%s&ip=%s' % 
			(urllib.quote(self.url), urllib.quote(self.where), urllib.quote(self.ip)), expect_errors = True)
		
		self.assertEqual(response.status_int, 200)
		self.assertEqual(response.content_type, 'application/json')
		self.assertEqual(json.decode(response.body)[0], 1)

	def test_last(self):
		self.test_peel()
		
		response = self.testapp.get('/api?action=last')

		self.assertEqual(response.status_int, 200)
		self.assertEqual(response.content_type, 'application/json')
		self.assertEqual(json.decode(response.body)[0], 200)
		self.assertEqual(json.decode(response.body)[1][2], self.url_peeled)

	def test_last_bad(self):
		response = self.testapp.get('/api?action=last', expect_errors = True)

		self.assertEqual(response.status_int, 200)
		self.assertEqual(response.content_type, 'application/json')
		self.assertEqual(json.decode(response.body)[0], 3)



