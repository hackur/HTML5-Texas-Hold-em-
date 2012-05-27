from tornado.httpclient import HTTPClient
from tornado.httpclient import AsyncHTTPClient
from time import gmtime, strftime
from poker_controller import *
import tornado.ioloop
import urllib
import json
import pprint
import argparse
import sys
import random
import time
import pika

(A_ALLIN,A_CALLSTAKE,A_RAISESTAKE,A_CHECK,A_DISCARDGAME,A_BIGBLIND,A_SMALLBLIND,A_STANDUP) = (1,2,3,4,5,6,7,8)
class Seat:
    def __init__(self, seat_id = -1, stake = 0, table = 0):
        self.id            = seat_id
        self.stake        = stake
        self.table        = table
        self.hand_cards    = []

class FoolDecisionMaker:
    Fold    = 100
    Call    = 7500
    Raise    = 9500
    All_In    = 10000
    def __init__(self):
        self.poker    = Poker(2)
        pass

    def convert_to_deck(self, card):
        _suit = 0
        _value= 0
        if len(card) == 2:
            _value= card[0]
            _suit = card[1]
        elif len(card) == 3:
            _value= "10"
            _suit = card[2]

        if _value.isdigit():
            _value = int(_value)
        else:
            if _value == "J":
                _value = 11
            elif _value == "Q":
                _value = 12
            elif _value == "K":
                _value = 13
            elif _value == "A":
                _value = 14

        if _suit == "C":
            _suit = 0
        elif _suit == "D":
            _suit = 1
        elif _suit == "H":
            _suit = 2
        elif _suit == "S":
            _suit = 3
        return Card(_suit, _value)

    def _rank(self, cards):
        cards.sort()
        return self.poker.score(cards)

    def _chen_score(self, card):
        if card.value == 14:
            return 10
        elif card.value == 13:
            return 8
        elif card.value == 12:
            return 7
        elif card.value == 11:
            return 6
        else:
            return card.value / 2.0

    def _chen_formula(self, cards):
        baseScore = max(self._chen_score(cards[0]), self._chen_score(cards[1]))
        if cards[0].value == cards[1].value:
            baseScore = max(5, baseScore * 2)

        if cards[0].symbol == cards[1].symbol:
            baseScore += 2

        gap = abs(cards[0].value - cards[1].value)
        if gap == 0:
            pass
        elif gap == 1:
            baseScore    += 1
        elif gap == 2:
            baseScore    -= 1
        elif gap == 3:
            baseScore    -= 2
        elif gap == 4:
            baseScore    -= 4
        else:
            baseScore    -= 5

        return baseScore;


    def make_decision(self, robot_cards, opp_cards_list, board_cards, current_pot, call_stake, min_raise, max_raise, rights):
        action    = A_DISCARDGAME
        amount    = -1
        value = random.randint(1, 10000)
        print "call %f, min raise %f, max raise %f" %(call_stake, min_raise, max_raise)
        if value < FoolDecisionMaker.Fold:
            action    = A_DISCARDGAME
            amount    = 0
        elif value < FoolDecisionMaker.Call:
            if A_CALLSTAKE in rights:
                action    = A_CALLSTAKE
                amount    = call_stake
            elif A_ALLIN in rights:
                action    = A_ALLIN
                amount    = min_raise
            else:
                action    = A_DISCARDGAME
                amount    = 0
        elif value < FoolDecisionMaker.Raise:
            if A_CALLSTAKE in rights:
                action    = A_CALLSTAKE
                amount    = call_stake
            elif A_RAISESTAKE in rights:
                action    = A_RAISESTAKE
                amount    = min_raise
            elif A_ALLIN in rights:
                action    = A_ALLIN
                amount    = min_raise
            else:
                action    = A_DISCARDGAME
                amount    = 0
        elif value < FoolDecisionMaker.All_In:
            if A_ALLIN in rights:
                action    = A_ALLIN
                amount    = max_raise
            elif A_RAISESTAKE in rights:
                action  = A_RAISESTAKE
                amount  = min_raise
            elif A_CALLSTAKE in rights:
                action  = A_CALLSTAKE
                amount  = call_stake
            else:
                action  = A_DISCARDGAME
                amount  = 0

        if action == A_ALLIN or amount == max(max_raise,min_raise, call_stake):
            robot_decks = []
            board_decks    = []
            for card in robot_cards:
                robot_decks.append(self.convert_to_deck(card))
            for card in board_cards:
                board_decks.append(self.convert_to_deck(card))

            if len(board_cards) >= 3:
                robot_rank    = self._rank(robot_decks+board_decks)
                if robot_rank[0] <= 4:
                    if A_CHECK in rights:
                        action = A_CHECK
                        amount = 0
                    else:
                        action = A_DISCARDGAME
                        amount = 0
            else:
                chen_score    = self._chen_formula(robot_decks)
                if chen_score < 9:
                    action = A_DISCARDGAME
                    amount = 0

        if action == A_DISCARDGAME and A_CHECK in rights:
            action = A_CHECK
            amount = 0

        return (action, amount)

class DecisionMaker:
    def __init__(self):
        self.ranks    = {}
        self.poker    = Poker(2)
        self.cards    = []
        suit        = 0x8000;
        index        = 0
        for i in xrange(4):
            for j in xrange(2,15):
                self.cards.append(Card(i,j))

    def _rank_compare(self, left,right):
        if left[0] != right[0] :
            return left[0] - right[0]
        else:
            for i in xrange(len(left[1])):
                if left[1][i] != right[1][i]:
                    return left[1][i] - right[1][i]
        return 0

    def convert_to_deck(self, card):
        _suit = 0
        _value= 0
        if len(card) == 2:
            _value= card[0]
            _suit = card[1]
        elif len(card) == 3:
            _value= "10"
            _suit = card[2]

        if _value.isdigit():
            _value = int(_value)
        else:
            if _value == "J":
                _value = 11
            elif _value == "Q":
                _value = 12
            elif _value == "K":
                _value = 13
            elif _value == "A":
                _value = 14

        if _suit == "C":
            _suit = 0
        elif _suit == "D":
            _suit = 1
        elif _suit == "H":
            _suit = 2
        elif _suit == "S":
            _suit = 3
        return Card(_suit, _value)


    def _rank(self, cards):
        cards.sort()
        return self.poker.score(cards)

    def filter(self,source, exclude_list):
        result    = []
        flag    = False
        for element in source:
            for item in exclude_list:
                if element.symbol == item.symbol and  element.value == item.value :
                    flag = True
                    break;
            if flag == False:
                result.append(element)
            flag = False
        return result
    def _chen_score(self, card):
        if card.value == 14:
            return 10
        elif card.value == 13:
            return 8
        elif card.value == 12:
            return 7
        elif card.value == 11:
            return 6
        else:
            return card.value / 2.0

    def _chen_formula(self, cards):
        baseScore = max(self._chen_score(cards[0]), self._chen_score(cards[1]))
        if cards[0].value == cards[1].value:
            baseScore = max(5, baseScore * 2)

        if cards[0].symbol == cards[1].symbol:
            baseScore += 2

        gap = abs(cards[0].value - cards[1].value)
        if gap == 0:
            pass
        elif gap == 1:
            baseScore    += 1
        elif gap == 2:
            baseScore    -= 1
        elif gap == 3:
            baseScore    -= 2
        elif gap == 4:
            baseScore    -= 4
        else:
            baseScore    -= 5

        return baseScore;


    def _hand_potential(self, robot_cards, opp_cards_list, board_cards):
        total_cases    = 0
        win_counter    = 0
        robot_all_cards = robot_cards + board_cards
        remain_cards    = self.filter(self.cards, robot_all_cards)
        for opp_cards in opp_cards_list:
            remain_cards= self.filter(remain_cards, opp_cards)

        if len(board_cards) == 3:
            for k in xrange(len(remain_cards)-1):
                for o in xrange(k + 1, len(remain_cards)):
                    counter = 0
                    for opp_cards in opp_cards_list:
                        temp_board    = board_cards + [remain_cards[k], remain_cards[o]]
                        robot_best    = self._rank(temp_board + robot_cards)
                        opp_best    = self._rank(temp_board + opp_cards)
                        best_comparison = self._rank_compare(robot_best, opp_best)
                        if best_comparison >= 0:
                            counter += 1
                total_cases += 1.0
                if counter == len(opp_cards_list):
                    win_counter += 1.0

        elif len(board_cards) == 4:
            for k in xrange(len(remain_cards)):
                counter = 0
                for opp_cards in opp_cards_list:
                    temp_board    = board_cards + [remain_cards[k]]
                    robot_best    = self._rank(temp_board + robot_cards)
                    opp_best    = self._rank(temp_board + opp_cards)
                    best_comparison = self._rank_compare(robot_best, opp_best)
                    if best_comparison >= 0:
                        counter += 1
                total_cases += 1.0
                if counter == len(opp_cards_list):
                    win_counter += 1.0
        elif len(board_cards) == 5:
            remain_cards= self.filter(self.cards, robot_all_cards)
            no_opp        = len(opp_cards_list)
            robot_best    = self._rank(robot_all_cards)
            for i in xrange(len(remain_cards) - no_opp - 1):
                for j in xrange(i + 1, len(remain_cards) - no_opp ):
                    counter = 0
                    for k in xrange(no_opp):
                        opp_cards    = board_cards + [remain_cards[i], remain_cards[j + k]]
                        opp_best    = self._rank(opp_cards)
                        best_comparison = self._rank_compare(robot_best, opp_best)
                        if best_comparison >= 0:
                            counter += 1
                    total_cases += 1.0
                if counter == no_opp:
                    win_counter += 1.0
            board_rank = self._rank(board_cards)
            win_counter += (total_cases/10)*(robot_best[0] - board_rank[0] + 1)
        print (win_counter*1.0)/total_cases
        return (win_counter*1.0)/total_cases

    def _chen_strategy(self, robot_decks, call_stake, min_raise, max_raise, rights):
        chen_value = self._chen_formula(robot_decks)

        if chen_value >= 8:
            if A_RAISESTAKE in rights:
                action = A_RAISESTAKE
                amount = min_raise
            elif A_CALLSTAKE in rights:
                amount = call_stake
                action = A_CALLSTAKE
            elif A_ALLIN in rights:
                action = A_ALLIN
                amount = min_raise
            else:
                action = A_DISCARDGAME
                amount = -1

        else:
            action = A_DISCARDGAME
            amount = -1

        if amount == -1 and A_CHECK in rights:
            amount = -1
            action = A_CHECK
        print "(%d, %d)" %(action, amount)
        return (action, amount)

    def _normal_strategy(self, win_odds, current_pot, call_stake, min_raise, max_raise, rights):
        amount = -1
        action = A_DISCARDGAME
        print win_odds
        if A_CALLSTAKE in rights and A_ALLIN in rights and A_RAISESTAKE not in rights:
            if current_pot / call_stake > win_odds :
                if current_pot / max_raise > win_odds:
                    print "max raise all in"
                    amount = max_raise
                    action = A_ALLIN
                else:
                    print "call stake"
                    amount = call_stake
                    action = A_CALLSTAKE
            else:
                print "fold"
                amount = -1
                action = A_DISCARDGAME

        elif A_CALLSTAKE in rights and A_RAISESTAKE in rights:
            if current_pot / call_stake > win_odds :
                if current_pot / max_raise > win_odds:
                    print "max raise all in"
                    amount = max_raise
                    action = A_RAISESTAKE
                elif current_pot / min_raise > win_odds:
                    print "min raise"
                    amount = min_raise
                    action = A_RAISESTAKE
                else:
                    print "call stake"
                    amount = call_stake
                    action = A_CALLSTAKE
            else:
                print "fold"
                amount = -1
                action = A_DISCARDGAME

        elif A_CALLSTAKE not in rights and A_ALLIN in rights:
            if current_pot / min_raise > win_odds:
                print "min raise"
                amount = min_raise
                action = A_ALLIN
            else:
                print "fold"
                amount = -1
                action = A_DISCARDGAME

        if amount == -1 and A_CHECK in rights:
            amount = -1
            action = A_CHECK

        print "amount = ",amount
        return (action, amount)


    def make_decision(self, robot_cards, opp_cards_list, board_cards, current_pot, call_stake, min_raise, max_raise, rights):
        robot_decks        = []
        board_decks        = []
        opp_decks_list    = []
        for card in robot_cards:
            robot_decks.append(self.convert_to_deck(card))

        for card in board_cards:
            board_decks.append(self.convert_to_deck(card))

        for cards in opp_cards_list:
            temp_list    = []
            for card in cards:
                temp_list.append(self.convert_to_deck(card))
            opp_decks_list.append(temp_list)


        if len(board_cards) == 0:
            return self._chen_strategy(robot_decks, call_stake, min_raise, max_raise, rights)
        else:
            win_probability = self._hand_potential(robot_decks, opp_decks_list, board_decks)
            win_probability += 0.005
            if win_probability > 1.0:
                win_probability = 1.0
            win_odds = 1.0 / (win_probability)
            print "win probability =>%d"%(win_probability)
            return self._normal_strategy(win_odds, current_pot, call_stake, min_raise, max_raise, rights)


class Robot:
    Login_URL_Template                    = "http://%s:%d/login"
    List_Room_URL_Template                = "http://%s:%d/list_room"
    Enter_Room_URL_Template                = "http://%s:%d/enter"
    User_Info_URL_Template                = "http://%s:%d/userinfo"
    Sit_Down_URL_Template                = "http://%s:%d/sit-down"
    Post_Board_Message_URL_Template        = "http://%s:%d/post-board-message"
    Listen_Board_Message_URL_Template    = "http://%s:%d/listen-board-message"
    Refill_URL_Template                    = "http://%s:%d/refill"
    Action_ALL            = 1
    Action_Call_Stake    = 2
    Action_Raise_Stake    = 3
    Action_Check_Stake    = 4
    Action_Discard_Game    = 5
    Action_Stand_Up        = 8
    def __init__(self, ip='127.0.0.1', port = 80, username=None, password=None, room=None, iq="low"):
        self.ip            = ip
        self.port        = port
        self.username    = username
        self.password    = password
        self.room            = None
        self.timestamp        = -1
        self.public_cards    = []
        self.seats            = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.seat            = -1
        self.pot_amount        = 0
        self.min_raise        = 0
        self.max_raise        = 0
        self.call_amount    = 0
        self.hand_cards        = []
        self.rights            = []
        self.opp_cards        = []
        self.http_client    = AsyncHTTPClient()
        self.is_sit_down    = False

        if iq == "low":
            self.decision_maker    = FoolDecisionMaker()
        else:
            self.decision_maker = DecisionMaker()

        self.login_url        = Robot.Login_URL_Template % (ip, port)
        self.enter_url        = Robot.Enter_Room_URL_Template % (ip, port)
        self.user_info_url    = Robot.User_Info_URL_Template % (ip, port)
        self.refill_url        = Robot.Refill_URL_Template % (ip, port)
        self.list_room_url    = Robot.List_Room_URL_Template % (ip, port)
        self.sit_down_url                = Robot.Sit_Down_URL_Template % (ip, port)
        self.post_board_message_url        = Robot.Post_Board_Message_URL_Template % (ip ,port)
        self.listen_board_message_url    = Robot.Listen_Board_Message_URL_Template % (ip, port)

    def start(self):
        print "Robot login [start]"
        post_data    = {"username":self.username, "password":self.password}
        body        = urllib.urlencode(post_data)
        self.http_client.fetch(self.login_url,
                                self.login_handle,
                                method='POST',
                                headers=None,
                                body=body)
        print "Robot login [end]"

    def login_handle(self,response):
        print "Robot login handle [start]"
        content        = json.loads(response.body)
        print content
        if content["status"] == "success":
            self.cookies= response.headers['Set-Cookie'];
            self.get_user_info()
        else:
            print "Failed",content
            pass
        print "Robot login handle [end]"

    def get_user_info(self):
        headers    = {"Cookie":self.cookies}
        self.http_client.fetch(    self.user_info_url,
                                self.user_info_handle,
                                method='GET',
                                headers=headers)

    def user_info_handle(self,response):
        print "user info [start]"
        try:
            content        = json.loads(response.body)
            print content
        except e as Exception:
            print response.body
            raise e

        self.asset    = content['s']
        self.user_id= content['id']
        if self.asset < 3000:
            self.refill()
        else:
            self.list_room()
        print "user info [end]"

    def list_room(self):
        headers    = {"Cookie":self.cookies}
        body    = urllib.urlencode({"type":0})
        self.http_client.fetch(    self.list_room_url,
                                self.list_room_handle,
                                method='POST',
                                headers=headers,
                                body=body)

    def list_room_handle(self, response):
        def sorter(left, right):
            return left[2] - right[2]

        print "List Room Handle[start]"
        content = json.loads(response.body)
        available_list = filter(lambda x: x[2] > 0 and x[2] < x[3],content["rooms"])
        print available_list
        if len(available_list) > 0:
            available_list.sort(sorter)
            self.room = available_list[0][0]
        else:
            self.room = content["rooms"][0][0]

        self.enter()
        print "List Room Hanlde[end]"

    def enter(self):
        print "Robot enter [start]"
        print "enter "+self.room
        post_data    = {"room_id":self.room}
        body        = urllib.urlencode(post_data)
        headers        = {"Cookie":self.cookies}
        self.http_client.fetch(    self.enter_url,
                                self.enter_handle,
                                method='POST',
                                headers=headers,
                                body=body)
        print "Robot enter [end]"

    def enter_handle(self, response):
        print "Robot enter handle [start]"
        print response.body
        content        = json.loads(response.body)
        if content["status"] == "success":
            self.cookies= response.headers['Set-Cookie'];
            self.min_stake    = content["room"]["min_stake"]
            self.max_stake    = content["room"]["max_stake"]
            for i in xrange(len(content["room"]["seats"])):
                if content["room"]["seats"][i] == None:
                    self.seat = i

            if self.asset > (self.min_stake+self.max_stake)/2:
                self.stake    = (self.min_stake+self.max_stake)/2
            else:
                self.stake    = self.min_stake

            self.asset        -= self.stake
            self.timestamp    = content["room"]["timestamp"]
            print "current time stamp ", self.timestamp
            self.sit_down()
        else:
            self.list_room()
        print "Robot enter handle [end]"


    def sit_down(self):
        print "Robot sit_down  [start]"
        post_data    = {"seat": self.seat, "stake":self.stake}
        body        = urllib.urlencode(post_data)
        headers        = {"Cookie":self.cookies}
        self.http_client.fetch(    self.sit_down_url,
                                self.sit_down_handle,
                                method    = "POST",
                                headers    = headers,
                                body    = body)
        print "Robot sit_down [end]"

    def sit_down_handle(self,response):
        print "Robot sit_down handle [start]"
        print response
        content        = json.loads(response.body)
        print content
        if content["status"] == "success":
            self.cookies= response.headers['Set-Cookie'];
            self.listen_board_message()
            self.is_sit_down = True
        else:
            self.refill()
        print "Robot sit_down handle [end]"

    def listen_board_message(self):
        pika.log.info( "Robot Listen Board Message [Start]")

        post_data    = {"timestamp": self.timestamp}
        body        = urllib.urlencode(post_data)
        headers        = {"Cookie":self.cookies}

        print post_data
        self.http_client.fetch(    self.listen_board_message_url,
                                self.listen_board_message_handle,
                                method    = "POST",
                                headers    = headers,
                                body    = body)

        pika.log.info( "Robot Listen Board Message [End]")

    def listen_board_message_handle(self, response):
        def _sorter(left, right):
            return left["timestamp"] - right["timestamp"]

        pika.log.info( "Robot Handle Listen Board Message [Start]")

        try:
            content    = json.loads(response.body)
        except:
            print sys.exc_info()
            print "content is :"
            print response.body
            if self.is_sit_down == True:
                self.listen_board_message()
            return
        content.sort(_sorter)
        self.cookies= response.headers['Set-Cookie'];
        for i in xrange(len(content)):
            message            = content[i]
            if message["timestamp"] > self.timestamp:
                print message
                self.timestamp    = message["timestamp"]
                if hasattr(self,"handle_" + message['msgType']):
                    method = getattr(self,"handle_" + message['msgType'])
                    method(message)
                else:
                    print message['msgType'],"is not supported"

        if self.is_sit_down == True:
            self.listen_board_message()

        pika.log.info( "Robot Handle Listen Board Message [End]")


    def send_post_message(self):
        pika.log.info( "Send Post Message [Start]")
        (action, amount)  = self.decision_maker.make_decision(
                                            self.hand_cards,
                                            self.opp_cards,
                                            self.public_cards,
                                            self.pot_amount,
                                            self.call_amount,
                                            self.min_raise,
                                            self.max_raise,
                                            self.rights)

        post_data    = {"message":json.dumps({"action": action, "amount":amount})}
        body        = urllib.urlencode(post_data)
        headers        = {"Cookie":self.cookies}
        self.http_client.fetch(    self.post_board_message_url,
                                self.handle_post_board,
                                method    = "POST",
                                headers    = headers,
                                body    = body)

        pika.log.info( "Send Post Message [End]")


    def handle_post_board(self, data):
        pika.log.info( "Handle Post Message [Start]")
        pika.log.info( "Handle Post Message [End]")

    def handle_chat(self,data):
        pass

    def handle_sit(self,data):
        pika.log.info( "Handle Sit [Start]")
        self.seats[data["seat_no"]] = Seat()
        self.seats[data["seat_no"]].seat_id = data["seat_no"]
        self.seats[data["seat_no"]].stake = data["info"]["player_stake"]
        self.seats[data["seat_no"]].table = 0
        pika.log.info( "Handle Sit [End]")

    def handle_bot_card(self, data):
        pika.log.info( "Handle Bot Card [Start]")
        if data['cards'] not in self.opp_cards:
            if data['cards'] != self.hand_cards:
                self.opp_cards.append(data['cards'])

        pika.log.info( "Handle Bot Card [End]")

    def handle_bhc(self,data):
        pika.log.info( "Handle bhc [Start]")
        pika.log.info("\t\t %s", data)
        pika.log.info( "Handle bhc [End]")

    def handle_phc(self,data):
        pika.log.info( "Handle phc [Start]")
        pika.log.info( "\t\t %s", data)
        self.hand_cards = data["cards"]
        pika.log.info( "Handle phc [End]")

    def handle_winner(self,data):
        pika.log.info( "Handle winner [Start]")
        pika.log.info( "\t\t %s", data)
        if self.user_id in data:
            self.asset    += data[self.user_id]['stake'] - self.stake
            self.stake    = data[self.user_id]['stake']
        pika.log.info( "Handle winner [End]")

    def handle_next(self,data):
        pika.log.info( "Handle next [Start]")
        pika.log.info( "\t\t %s", data)

        if data["seat_no"] == self.seat:
            if A_CALLSTAKE in data["rights"]:
                self.call_amount= data["amount_limits"]['2']
            if A_RAISESTAKE in data["rights"]:
                self.min_raise    = data["amount_limits"]['3'][0]
                self.max_raise    = data["amount_limits"]['3'][1]
            self.rights = data["rights"]
            time.sleep(random.randint(2,5))
            self.send_post_message()

        pika.log.info( "Handle next [End]")

    def handle_action(self, data):
        pika.log.info( "Handle action [Start]")
        pika.log.info( "\t\t %s", data)

        if data["seat_no"] == self.seat:
            self.stake = data["stake"]

        pika.log.info( "Handle action [End]")

    def handle_public(self,data):
        pika.log.info( "Handle public [Start]")
        pika.log.info( "\t\t %s", data)

        self.public_cards = []
        for i in xrange(len(data["cards"])):
            self.public_cards.append(data["cards"][i]);

        pika.log.info( "Handle public [End]")

    def handle_start(self,data):
        pika.log.info( "Handle start game [Start]")
        pika.log.info( "\t\t %s", data)

        self.public_cards    = []
        self.opp_cards        = []
        self.hand_cards        = []
        self.pot_amount        = 0

        print "stake =>",self.stake
        pika.log.info( "Handle start game [End]")

    def handle_pot(self, data):
        pika.log.info( "Handle pot [Start]")
        pika.log.info( "\t\t %s", data)

        self.pot_amount = 0
        for pot in data["pot"]:
            self.pot_amount += pot[1]["amount"]

        pika.log.info( "Handle pot [End]")


    def handle_standup(self, data):
        pika.log.info( "Handle stand up [Start]")
        pika.log.info( "\t\t %s", data)

        if self.user_id in data:
            if data[self.user_id]["seat_no"]==self.seat:
                self.stake = 0
                if self.asset <= 200:
                    ioloop    = tornado.ioloop.IOLoop.instance()
                    ioloop.add_timeout(time.time() + 10, self.refill)
                else:
                    ioloop    = tornado.ioloop.IOLoop.instance()
                    ioloop.add_timeout(time.time() + 10, self.list_room)

                self.is_sit_down = False


        pika.log.info( "Handle stand up [End]")

    def refill(self):
        pika.log.info( "Re-fill [Start]")

        headers    = {"Cookie":self.cookies}
        self.http_client.fetch(    self.refill_url,
                                self.refill_handle,
                                method='GET',
                                headers=headers)

        pika.log.info( "Re-fill [End]")

    def refill_handle(self, response):
        pika.log.info( "Handle Re-fill [Start]")
        pika.log.info( "\t\t %s", response.body)

        self.asset = float(response.body)
        self.list_room()

        pika.log.info( "Handl Re-fill [End]")


import argparse
if __name__=="__main__":
    import time
    parser = argparse.ArgumentParser(description='Bot...')
    parser.add_argument('--port','-P',default=8888,type=int)
    parser.add_argument('--username','-U',default="human1")
    parser.add_argument('--password','-E',default="123321")
    parser.add_argument('--server','-S',default="127.0.0.1")
    parser.add_argument('--wait','-W',default=0,type=int)
    parser.add_argument('--iq','-I',default="low")

    args = parser.parse_args()
    time.sleep(args.wait)

    debug = True
    pika.log.setup(color=debug)
    host    = args.server
    port    = args.port
    username= args.username
    password= args.password
    iq        = args.iq
    robot    = Robot(ip=host,port=port,username=username,password=password,iq=iq)
    robot.start()
    ioloop    = tornado.ioloop.IOLoop.instance()
    ioloop.start()


    '''
    decision_maker    = DecisionMaker()
    cards    = ["2C", "2D"]
    p_cards    = ["5H", "4S", "6C",]
    opp_card_list = [["3D","KD"], ["3S","4H"], ["2S","AD"]]
    print strftime("%Y-%m-%d %H:%M:%S", gmtime())
    print decision_maker.make_decision(cards, opp_card_list, p_cards, 200, 10,20,100,["call", "raise"])
    print strftime("%Y-%m-%d %H:%M:%S", gmtime())
    print decision_maker.make_decision(cards, opp_card_list, p_cards, 200, 40,80,100,["call", "raise"])
    print strftime("%Y-%m-%d %H:%M:%S", gmtime())
    '''
