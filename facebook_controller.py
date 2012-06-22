import json
import hashlib
import urllib
import base64
import hmac
import tornado.ioloop
import tornado.httpserver
import tornado.web
from tornado.httpclient import HTTPClient
from tornado.httpclient import AsyncHTTPClient
from datetime import datetime
from database import DatabaseConnection,User,Room

from random import random
from thread_pool import in_thread_pool, in_ioloop, blocking
import time
from database import *

facebook_app_id        = "231740453606973"
facebook_app_secret    = "17a7bf50f0cdbfc143cb3eb63b33a874"
facebook_graph        = "https://graph.facebook.com/%s?fields=id,name,picture,gender,username"
facebook_permission_url    = "https://graph.facebook.com/%s/permissions?access_token=%s"
facebook_feed        = "https://graph.facebook.com/me/feed?access_token=%s"
canvas_page            = "http://seressoft.com:8001/facebook/"
facebook_profile_pic = "https://graph.facebook.com/%s/picture?type=large&return_ssl_resources=1"
auth_url            = "https://www.facebook.com/dialog/oauth?client_id="+facebook_app_id+"&redirect_uri="+urllib.pathname2url(canvas_page)+"&scope=user_status,publish_actions,publish_stream"

def _base64_url_decode(inp):
    padding_factor = (4 - len(inp) % 4) % 4
    inp += "="*padding_factor
    return base64.b64decode(unicode(inp).translate(dict(zip(map(ord, u'-_'), u'+/'))))

class FaceBookChannelHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("./channel.html")

    def post(self):
        self.render("./channel.html")

class FaceBookLogin(tornado.web.RequestHandler):
    def get(self):
        #args['code']            = self.get_argument('code')
        #args['client_secret']    = facebook_app_secret
        if "user_id" in self.session:
            self.redirect("/static/user/user.html")

    @tornado.web.asynchronous
    def post(self):
        signed_request    = self.get_argument('signed_request')
        encoded_sig, payload    = signed_request.split(u'.', 1)

        sig = _base64_url_decode(encoded_sig)
        data= json.loads(_base64_url_decode(payload))
        if data.get('algorithm').upper() != 'HMAC-SHA256':
            self.finish('Unknown algorithm')
            return None
        else:
            expected_sig = hmac.new(facebook_app_secret, msg=payload, digestmod=hashlib.sha256).digest()

        if sig != expected_sig:
            self.finish('Bad request')
            return None
        else:
            if "user_id" not in data:
                self.finish("<script>top.location.href='" + auth_url + "'</script>")
            else:
                self.access_token    = data[u'oauth_token']
                self.payload        = data
                self._check_permission(data)

    def _check_permission(self, data):
        permission_url    = facebook_permission_url % (data["user_id"], self.access_token)
        http_client    = AsyncHTTPClient()
        http_client.fetch(  permission_url,
                            self._handle_check_permission,
                            method    = 'GET',
                            headers    = None,
                            body    = None)

    def _handle_check_permission(self, response):
        permissions    = json.loads(response.body)["data"][0]
        if  "user_status" in permissions and permissions["user_status"] == 1 and \
            "publish_actions" in permissions and permissions["publish_actions"] == 1 and \
            "publish_stream" in permissions and permissions["publish_stream"] == 1:
            user  = User.verify_user_openID(accountType = User.USER_TYPE_FACEBOOK,
                                            accountID    = self.payload["user_id"])
            if not user:
                self.get_user_info(self.payload)
            else:
                self._login_user(user)
        else:
            self.finish("<script>top.location.href='" + auth_url + "'</script>")

    def get_user_info(self, data):
        graph_url    = facebook_graph % (data["user_id"])
        http_client    = AsyncHTTPClient()
        http_client.fetch(    graph_url,
                            self.handle_user_info,
                            method    = 'GET',
                            headers    = None,
                            body    = None)

    def handle_user_info(self, response):
        content    = json.loads(response.body)
        uid        = content["id"]
        user    = User.new(    username    = "%s_%s" % (User.USER_TYPE_FACEBOOK, uid),
                            accountType    = User.USER_TYPE_FACEBOOK,
                            accountID    = uid,
                            access_token= self.access_token)
        if content["gender"] == "male":
            user.gender = "M"
        elif content["gender"] == "female":
            user.gender    = "F"
        else:
            user.gender    = "N/A"
        user.screen_name        = content["name"]
        #user.headPortrait_url    = content["picture"]
        user.headPortrait_url   = facebook_profile_pic % uid
        self._update_facebook_feed(user);
        self._login_user(user)

    def _login_user(self, user):
        if user.last_login == None:
            user.bonus_notification = 1
        else:
            last_login_date = datetime.fromtimestamp(user.last_login)
            if last_login_date.date() < datetime.today().date():
                user.bonus_notification = 1

        user.last_login    = int(time.time())
        self.session['user_id'] = user.id
        self.redirect("/static/user/user.html")

    def _update_facebook_feed(self, user):
        feed_url        = facebook_feed % (self.access_token)
        body            = {}
        body["message"]    = "I am playing Texas Holdem."
        body["link"]    = "http://apps.facebook.com/seres_texas_holdem"
        http_client    = AsyncHTTPClient()
        http_client.fetch(    feed_url,
                            self._handle_facebook_feed,
                            method    = 'POST',
                            headers    = None,
                            body    = urllib.urlencode(body))

    def _handle_facebook_feed(self,response):
        print "facebook feed response[start]"
        print response.body
        print "facebook feed response[end]"

class FaceBookPurchaseHandler(tornado.web.RequestHandler):
    def post(self):
        signed_request    = self.get_argument('signed_request')
        encoded_sig, payload    = signed_request.split(u'.', 1)

        sig = _base64_url_decode(encoded_sig)
        data= json.loads(_base64_url_decode(payload))
        method = self.get_argument('method')
        if data.get('algorithm').upper() != 'HMAC-SHA256':
            self.finish('Unknown algorithm')
            return None
        else:
            expected_sig = hmac.new(facebook_app_secret, msg=payload, digestmod=hashlib.sha256).digest()

        if sig != expected_sig:
            self.finish('Bad request')
            return None
        else:
            self._process_data(data,method)

    def _process_data(self, data,method):
        request_type = method
        if request_type == 'payments_get_items':
            item_id        = data["credits"]['order_info']
            item        = Commodity.find(commodity_id = int(item_id))
            itemInfo    = {}
            itemInfo['item_id']        = item_id
            itemInfo['title']        = item.title
            itemInfo['price']        = item.price
            itemInfo['description']    = item.description
            itemInfo['image_url']    = item.image_url
            response    = {"content":[itemInfo], "method":request_type}
        elif request_type == "payments_status_update":
            order_details    = json.loads(data['credits']['order_details'])
            item_data        = order_details['items'][0]['data']
            if "modified" in item_data:
                earned_currency_order = item_data['modified']
            else:
                earned_currency_order = None
            current_order_status = order_details["status"]
            if current_order_status == "placed":
                if earned_currency_order != None:
                    print earned_currency_order
            #        product            = earned_currency_order['product']
            #        product_title    = earned_currency_order['product_title']
            #        product_amount    = earned_currency_order['product_amount']
            #        credits_amount    = earned_currency_order['credits_amount']

                client_id    = data['user_id']
                items        = order_details['items']
                client        = User.verify_user_openID(    accountType = User.USER_TYPE_FACEBOOK,
                                                        accountID    = client_id)
                for item in items:
                    commodity = Commodity.find(commodity_id = int(item["item_id"]))
                    client.update_attr('asset', commodity.money)

                self.save_order(client_id, order_details)
                next_order_status    = "settled"
                response = {
                    "content" : {
                        "status":next_order_status,
                        "order_id":order_details['order_id']
                    },
                    "method" : request_type
                }
            elif current_order_status == "disputed":
                raise Exception("disputed")
                pass
            elif current_order_status == "refunded":
                raise Exception("refunded")
            elif current_order_status == "settled":
                response = {}
            else:
                raise Exception(request_type)

        print json.dumps(response)
        self.finish(json.dumps(response))

    def save_order(self, user_id, order):
        items = []
        for item in order["items"]:
            items.append(item["item_id"])
        PurchaseOrder.new(    order["status"],
                            user_id,
                            order["update_time"],
                            order["ref_order_id"],
                            order["order_id"],
                            items,
                            order["app"],
                            order["time_placed"],
                            order["currency"],
                            order["amount"],
                            order["receiver"],
                            order["buyer"],
                            order["data"],
                            order["properties"])

