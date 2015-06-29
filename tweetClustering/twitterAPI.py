# -*- coding: utf8 -*-

import urllib
import base64
import httplib
import zlib
import json
import time
import re
import os
from pprint import pformat


CONSUMER_KEY = 'N3iL81n0Fr0ogwy8GlJUUvDHi'
CONSUMER_SECRET = '8opYcFDnPCaC6ZYoHR308CipZv719MckF4Q4fEeOrweyF7MqlS'
HOST = 'api.twitter.com'


class TwitterAPI(object):
    """
    Object for interacting with twitter API.
    As twitter is imposing limitations to the its api calls,
    in order to test your scripts easier, all requests result will be
    cached. If another call to the same url with the same parameters
    is done later on, no request will actually be issued.
    """
    def __init__(self, gzip=True):
        """
        Initialize the object that will interact with twitter API.
        This will send an initial request to twitter to retrieve the
        bearer token, required to authenticate future requests.
        * gzip:boolean, whether to ask for gzip compression or not. Enabled by
          default.
        """
        super(TwitterAPI, self).__init__()
        self._gzip = gzip

        self._encodedConsumerKey = urllib.quote(CONSUMER_KEY)
        self._encodedConsumerSecret = urllib.quote(CONSUMER_SECRET)
        self._concatConsumerURL = "%s:%s" % (
            self._encodedConsumerKey,
            self._encodedConsumerSecret)
        self._bearerToken = None
        self._bearerToken = self._getBearerToken()

    def _buildCacheFileName(self, rType, url, paramString=None, **params):
        """
        Build the name of the cache file from the type or the request, the url
        requested and the parameters attached to the request.
        All non-alphanumeric characters will be replaced by a dash.
        The filename will point over a file under the `cache` folder, which
        will be created if it does not exist.
        * rType:string, type of the HTTP request
          (either 'GET', 'POST', 'PUT' or 'DELETE')
        * url:string, the requested url. This should not contain the hostname.
          (e.g.: "/1.1/search/tweets.json" instead of
          "api.twitter.com/1.1/search/tweets.json")
        * paramString:string, url-encoded parameters. These will be added
          *before* the other parameters.
        * **params: keyword arguments, any number of parameters to be used
         with the request. If `paramString` is given, these `params`
         will be url-encoded then appended to the given `paramString`.
        Returns the name of the file that will or should contain the cached
        content of the request.
        """
        if not os.path.exists('cache'):
            os.mkdir('cache')
        filename = os.path.join(
            'cache',
            rType + '-' + re.sub("[^A-Za-z0-9]", "-", url))
        if paramString is not None:
            filename += re.sub("[^A-Za-z0-9]", "-", paramString)
        else:
            filename += '?'
        filename += re.sub("[^A-Za-z0-9]", "-", urllib.urlencode(params))
        filename += '.json'
        return filename

    def _getCachedContent(self, *args, **kwargs):
        """
        Returns the cached content for the given request, if it exists.
        `*args` (positional arguments) and `**kwargs` (keyword arguments)
        will be given to the `_buildCacheFileName` function.
        Returns the object that was json-encoded and cached for this request,
        or `None` if the file did not exist.
        """
        filename = self._buildCacheFileName(*args, **kwargs)
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except:
            return

    def _sendRequest(self, rType, url, paramString=None, **params):
        """
        Send a request to twitter API.
        * rType:string, type of the HTTP request
          (either 'GET', 'POST', 'PUT' or 'DELETE')
        * url:string, the requested url. This should not contain the hostname.
          (e.g.: specify "/1.1/search/tweets.json" instead of
          "api.twitter.com/1.1/search/tweets.json")
        * paramString:string, url-encoded parameters. These will be added
          *before* the other parameters.
        * **params: keywords arguments, any number of parameters to be used
         with the request. If `paramString` is given, these `params`
         will be url-encoded then appended to the given `paramString`.
        Returns the json-loaded object retrieved by a request for the given
        resource.
        """
        start_t = time.time()
        # create full url, with parameters
        params = urllib.urlencode(params)
        if rType.upper() == 'GET':
            if paramString is not None:
                url += paramString
            else:
                url += '?'
                url += params

        # create the request, add all necessary headers
        req = httplib.HTTPSConnection(HOST)
        #print "Request to: %s %s ..." % (rType, url),
        req.putrequest(rType, url)
        req.putheader("Host", HOST)
        req.putheader("User-Agent", "NLP Challenge v1.0")
        if self._bearerToken is None:
            auth = 'Basic %s' % base64.b64encode(self._concatConsumerURL)
        else:
            auth = 'Bearer %s' % self._bearerToken
        req.putheader("Authorization", auth)
        req.putheader("Content-Type",
                      "application/x-www-form-urlencoded;charset=UTF-8")
        if rType.upper() == 'POST':
            req.putheader("Content-Length", "%d" % len(params))
        else:
            req.putheader("Content-Length", "0")
        if self._gzip:
            req.putheader("Accept-Encoding", "gzip")
        req.endheaders()

        # send the request, retrieve the response
        if rType.upper() == 'POST':
            req.send(params or paramString[1:])
        else:
            req.send('')
        resp = req.getresponse()

        # process and decode result
        if resp.status != 200:
            raise Exception(
                "Twitter API responded with: %d %s"
                % (resp.status, resp.reason))
        if self._gzip:
            text = zlib.decompress(
                resp.read(),
                zlib.MAX_WBITS | 16)
        else:
            text = resp.read()

        #print " %.3fs" % (time.time() - start_t)
        try:
            return json.loads(text)
        except ValueError:
            print "Unable to decode json from string: %s" % text
            raise

    def _sendCachedRequest(self, rType, url, paramString=None, **params):
        """
        Wraps a call to `_sendRequest` to either retrieve the content locally
        if it has already been cached, or retrieve the content from twitter API
        by issuing an HTTP request and cache the content for further re-use.
        * rType:string, type of the HTTP request
          (either 'GET', 'POST', 'PUT' or 'DELETE')
        * url:string, the requested url. This should not contain the hostname.
          (e.g.: specify "/1.1/search/tweets.json" instead of
          "api.twitter.com/1.1/search/tweets.json")
        * paramString:string, url-encoded parameters. These will be added
          *before* the other parameters.
        * **params: keywords arguments, any number of parameters to be used
         with the request. If `paramString` is given, these `params`
         will be url-encoded then appended to the given `paramString`.
        Returns the json-loaded object retrieved now or earlier by a request
        for the given resource.
        """
        cachedContent = self._getCachedContent(
            rType, url, paramString, **params)
        if cachedContent is not None:
            #print "Cached from: %s %s%s" % (
              #  rType, url, paramString or urllib.urlencode(params))
            return cachedContent

        content = self._sendRequest(rType, url, paramString, **params)
        filename = self._buildCacheFileName(rType, url, paramString, **params)
        with open(filename, 'w') as f:
            json.dump(content, f)
        return content

    def _getBearerToken(self):
        """
        Retrieve the access token required to authenticate requests to twitter
        public API.
        """
        responseObj = self._sendRequest(
            'POST', '/oauth2/token/', grant_type='client_credentials')
        return responseObj['access_token']

    def _getTrends(self, lat, lng):
        """
        Returns the trending topics around the location given by the
        latitude and longitude.
        * lat:string, GPS-coordinates, latitude component.
        * lng:string, GPS-coordinates, longitude component.
        Returns the name of the trends objects, as returned by a call to
        [`/1.1/trends/closest.json'`](https://dev.twitter.com/rest/reference/get/trends/place)
        """
        closest = self._sendRequest(
            'GET', '/1.1/trends/closest.json',
            lat=lat, long=lng)
        # print closest
        WOEID = closest[0]['woeid']
        trends = self._sendRequest(
            'GET', '/1.1/trends/place.json', id=WOEID)
        print "Found trends for location: %s" % closest[0]['name']
        # print trends
        return (t['name'] for t in trends[0]['trends'])

    def getTrends(self):
        """
        Returns the trending topics around a few cities which are:
        Ottawa, Toronto, New York City, Washington and Albuquerque.
        Returns the name of the trends objects, as returned by a call to
        [`/1.1/trends/closest.json'`](https://dev.twitter.com/rest/reference/get/trends/place)
        """
        cities = {
            'ottawa': dict(lat="45.423494", lng="-75.697933"),
            'toronto': dict(lat="43.7000", lng="-79.4000"),
            'new york city': dict(lat="40.7127", lng="-74.0059"),
            'washington': dict(lat="47.5000", lng="-120.5000"),
            'albuquerque': dict(lat="35.1107", lng="-106.6100")
        }
        trends = set()
        for name, gps in cities.iteritems():
            print "Looking for trends in... %s" % name.title()
            cityTrend = [n for n in self._getTrends(**gps)]
            print "Trends found: %s" % str(cityTrend)
            trends.update(cityTrend)
        return trends

    def search(self, query, count=25):
        """
        Call the search API endpoint to retrieve the N most popular/recent
        tweets that matches the given search query.
        As twitter limits the size of the batch of tweets retrieved to 100,
        if the count given is higher than this limit multiple requests will be
        issued.
        The returned count may be lower than expected if there was no more
        indexed tweets available.
        **WARNING:** The search API endpoint is limitted to 480 queries per
        15 minutes. Issuing more requests will lead to an Exception with the
        message "429 Too Many Requests".
        See: [`/1.1/search/tweets.json'`](https://dev.twitter.com/rest/reference/get/search/tweets)
        for more information.
        * query:string, tweets search query, may be one or more hashtags,
          @mentions or any other criteria.
        * count:integer, number of tweets to return.
        Returns a list of string, list of tweet text content. The function will
        try, but cannot guarantee, to return as many items as specified by the
        `count` parameter.
        """
        res = []
        paramString = None
        while len(res) < count:
            if paramString is None:
                response = self._sendCachedRequest(
                    'GET', '/1.1/search/tweets.json',
                    q=query, count=(count - len(res)), lang='en',
                    include_entities=1)
            else:
                if 'count' in paramString:
                    paramString = re.sub(
                        r'count=\d+', 'count=%d' % (count - len(res)),
                        paramString)
                response = self._sendCachedRequest(
                    'GET', '/1.1/search/tweets.json',
                    paramString=paramString)
            res += [tweet['text'] for tweet in response['statuses']]
            try:
                paramString = response['search_metadata']['next_results']
            except:
                paramString = None
                break
        #print "  %d items retrieved." % (len(res))
        return res
