import time
from threading import Timer
from poker_controller import PokerController
import sys

class Seat(object):
    (SEAT_EMPTY,SEAT_WAITING,SEAT_PLAYING) = (0,1,2)

    def __init__(self):
        self._user = None
        self._cards = None
        self._inAmount = 0
        self._status = Seat.SEAT_EMPTY
        self._rights = []
        self._direct_key = None
        self._role = None
        self.combination = []
        self.handcards = []
        self.table_amount = 0
        pass

    def is_empty(self):
        return self._status == Seat.SEAT_EMPTY

    def sit(self, user, direct_key, private_key):
        self._user = user
        self._status = Seat.SEAT_WAITING
        self._direct_key = direct_key
        self._private_key= private_key

    def get_user(self):
        return self._user

    def get_direct_key(self):
        return self._direct_key

    def get_private_key(self):
        return self._private_key


    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        self._status = status

    @property
    def rights(self):
        return self._rights

    @rights.setter
    def rights(self, rights):
        self._rights = rights

    @property
    def inAmount(self):
        return self._inAmount

    @inAmount.setter
    def inAmount(self, inAmount):
        self._inAmount = inAmount

    def get_role(self):
        return self._role
    def set_role(self, role):
        self._role = role
    def is_waiting(self):
        return self.status == Seat.SEAT_WAITING

class GameRoom(object):
    (GAME_WAIT,GAME_PLAY) = (0,1)
    def __init__(self, room_id, owner, dealer, num_of_seats = 9, blind = 10):
        self.room_id        = room_id
        self.owner      = owner
        self.status     = GameRoom.GAME_WAIT
        self.dealer     = dealer
        self.broadcast_key  = "broadcast_%s_%d.testing" %(self.dealer.exchange, self.room_id)
        self.audit_list     = []
        self.seats          = []
        self.player_stake   = []
        self.occupied_seat  = 0
        self.suit = ["DIAMOND", "HEART", "SPADE", "CLUB"]
        self.face = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        self.msg_count= 0
        self.blind = blind
        self.min_amount = 0
        self.current_dealer = 0
        self.small_blind = 0
        self.big_blind = 0
        self.current_seat = None
        self.flop_flag = False
        self.prize_pool = 0
        self.num_of_checks = 0

        for x in xrange(num_of_seats):
            self.seats.append(Seat())
            self.player_stake.append(None)
        self.current_seat = None

        self.poker_controller = PokerController(self.seats)

    def broadcast(self,msg):
        self.msg_count += 1
        msg['timestamp'] = self.msg_count
        self.dealer.broadcast(self.broadcast_key, msg)

    def direct_message(self, msg, destination):
        self.msg_count += 1
        msg['timestamp'] = self.msg_count
        self.dealer.broadcast(destination, msg)
#####
    def sit(self, player, seat_no, direct_key, private_key):
        print "direct_key.........................................", direct_key
        seat_no = int(seat_no)
        print "seat request =>%d\n" % (seat_no)
        if seat_no > len(self.seats):
            return (False, "Seat number is too large: %s we have %s" % (seat_no,len(self.seats)))
        if not self.seats[seat_no].is_empty():
            return (False, "Seat Occupied")
        if self.status == GameRoom.GAME_PLAY:
            return (False, "Game Ongoing")


        self.seats[seat_no].sit(player, direct_key, private_key)
        self.player_stake[seat_no] = player.stake   # read user's money
        self.occupied_seat += 1
        message = {'status':'success', 'seat_no': seat_no, "username": self.seats[seat_no].get_user().username}
        self.broadcast(message)

        if self.occupied_seat == 3:
            t = Timer(5, self.start_game)
            t.start()
        return ( True, "" )


    def start_game(self):
        self.status = GameRoom.GAME_PLAY
        self.poker_controller.start()
        self.assign_role()

        #Distribute cards to each player
        for seat in self.seats:
            if seat.status != Seat.SEAT_EMPTY:
                seat.status = Seat.SEAT_PLAYING
                card_list   = []
                for card in seat.handcards:
                    card_list.append(str(card))
                msg_sent = {"Cards in hand": card_list}
                self.direct_message(msg_sent,seat.get_private_key())

        # bet in big blind and small blind by default
        print self.player_stake[self.small_blind]
        if self.player_stake[self.small_blind] < self.blind/2:
            self.player_stake[self.small_blind] = 0
        else:
            self.player_stake[self.small_blind] -= self.blind/2
            self.seats[self.small_blind].table_amount = self.blind/2
            print "small_blind stake: ", self.player_stake[self.small_blind]

        if self.player_stake[self.big_blind] < self.blind:
            self.player_stake[self.big_blind] = 0
        else:
            self.player_stake[self.big_blind] -= self.blind
            self.seats[self.big_blind].table_amount = self.blind
            print "big_blind stake: ", self.player_stake[self.big_blind]

        self.current_seat = self.info_next(self.big_blind, [2,3,5])
        print "next seat in action =>", self.current_seat
        self.min_amount = self.blind

    def get_seat(self, user_id):
        return filter(lambda seat: seat.get_user() != None and seat.get_user().id == user_id, self.seats)[0]

    def is_valid_seat(self, user_id, current_seat):
        request_seat = self.get_seat(user_id)
        valid_seat = self.seats[current_seat]
        if valid_seat == request_seat:
            return True
        else:
            return False

    def is_valid_rights(self, command, seat_no):
        if command not in self.seats[seat_no].rights:
            print "INVALID ACTION!"
            self.discard_game(seat_no)
            return False
        else:
            print "valid action"
            return True

    def call_stake(self, user_id, private_key):
        print "CALL!"
        if self.num_of_checks != 0:
            self.num_of_checks = 0
        print "num_of_checks: ", self.num_of_checks
        command = 2
        seat_no = self.current_seat
        amount  = self.min_amount - self.seats[seat_no].table_amount
        if self.is_valid_seat(user_id, seat_no) and self.is_valid_rights(command, seat_no):
            self.countdown.cancel()
            self.player_stake[seat_no] -= amount
            self.seats[seat_no].table_amount = self.min_amount
            if self.flop_flag == False:
                if self.same_amount_on_table():
                    self.current_seat = self.info_next(seat_no, [3,4,5])
                else:
                    self.current_seat = self.info_next(seat_no, self.seats[seat_no].rights)
            else:
                if self.same_amount_on_table():
                    self.poker_controller.getOne()
                    self.round_finish()
                else:
                    self.current_seat = self.info_next(seat_no, self.seats[seat_no].rights)
            print "--------------------self.min_amount in call_stake: ", self.min_amount

            card_list = []
            for card in self.poker_controller.publicCard:
                card_list.append(str(card))
                print str(card)

            broadcast_message = {"status": "success", "public cards": card_list, "username": self.seats[seat_no].get_user().username, "stake": self.player_stake[seat_no]}
            next_player_message = {"status":"active", "username": self.seats[self.current_seat].get_user().username, "rights":self.seats[self.current_seat].rights}

            self.broadcast(broadcast_message)
            self.direct_message(next_player_message, self.seats[self.current_seat].get_private_key())

    def raise_stake(self, user_id, private_key, amount):
        print "RAISE!"
        if self.num_of_checks != 0:
            self.num_of_checks = 0
        print "num_of_checks: ", self.num_of_checks
        amount          = int(amount)
        command         = 3
        seat_no         = self.current_seat
        if self.is_valid_seat(user_id, seat_no) and self.is_valid_rights(command, seat_no):
            self.countdown.cancel()
            if self.is_proper_amount(3, amount, seat_no):
                print "This is a proper amount"
                self.player_stake[seat_no] -= amount
                self.seats[seat_no].table_amount += amount
                self.min_amount     = self.seats[seat_no].table_amount
                print "------------------self.min_amount in raise_stake: ", self.min_amount
                self.current_seat   = self.info_next(seat_no, [2, 3, 5])
                print self.current_seat

                broadcast_message   = {'status':'success', 'username': self.seats[seat_no].get_user().username, 'stake':self.player_stake[seat_no]}
                next_player_message = {'status':'active', 'username': self.seats[self.current_seat].get_user().username, 'rights':[2, 3, 5]}

                self.broadcast(broadcast_message)
                self.direct_message(next_player_message, self.seats[self.current_seat].get_private_key())

    def check(self, user_id, private_key):
        print "CHECK!"
        print "flop_flag: ", self.flop_flag
        command = 4
        seat_no = self.current_seat
        player_list = filter(lambda seat: seat.status == Seat.SEAT_PLAYING, self.seats)
        if self.is_valid_seat(user_id, seat_no) and self.is_valid_rights(command, seat_no):
            self.countdown.cancel()
            if self.flop_flag == False:         #Before flop, sb. called check
                self.poker_controller.getFlop()
                self.flop_flag = True
                print "------------------------------", self.flop_flag
                self.round_finish()
            else:
                self.num_of_checks += 1
                print "num_of_checks: ", self.num_of_checks
                if self.num_of_checks < len(player_list):
                    self.current_seat = self.info_next(seat_no, self.seats[seat_no].rights)
                else:
                    self.num_of_checks = 0
                    self.poker_controller.getOne()
                    self.round_finish()

            card_list = []
            for card in self.poker_controller.publicCard:
                card_list.append(str(card))
                print str(card)

            broadcast_message = {"status": "success", "public cards": card_list, "username": self.seats[seat_no].get_user().username, "stake": self.player_stake[seat_no]}
            next_player_message = {"status":"active", "username": self.seats[self.current_seat].get_user().username, "rights":self.seats[self.current_seat].rights}

            self.broadcast(broadcast_message)
            self.direct_message(next_player_message, self.seats[self.current_seat].get_private_key())

    def discard_game(self, private_key):
        self.countdown.cancel()
        seat_no = self.current_seat
        print self.current_seat
        self.seats[seat_no].status = Seat.SEAT_WAITING  # set the status of this seat to empty
                                                        # remove the player from player list
        user = self.seats[seat_no].get_user()           # get user info from database
        user.stake = self.player_stake[seat_no]         # update user's stake
        self.add_audit(self.seats[seat_no].get_user())  # add the user to audit list
        self.current_seat = self.info_next(self.current_seat, self.seats[self.current_seat].rights)

        broadcast_message = {"status": "success", "username": self.seats[seat_no].get_user().username, "stake": self.player_stake[seat_no]}
        next_player_message = {"status": "active", "username": self.seats[self.current_seat].get_user().username, "rights": self.seats[self.current_seat].rights}

        self.broadcast(broadcast_message)
        self.direct_message(next_player_message, self.seats[self.current_seat].get_private_key())

    def info_next(self, current_position, rights):
        next = self.check_next(current_position)
        self.seats[next].rights = rights
        self.countdown = Timer(20, self.discard_game, args=[self.seats[next].get_private_key()])
        print "seat no. for next player: ", self.seats[next].get_user().username
        self.countdown.start()
        return next


    def add_audit(self, player):
        self.audit_list.append(player)

    def same_amount_on_table(self):
        player_list = filter(lambda seat: seat.status == Seat.SEAT_PLAYING, self.seats)
        for seat in player_list:
            if seat.table_amount != self.min_amount:
                return False
        return True

    def round_finish(self):
        print "ROUND FINISHED!!!!"
        self.countdown.cancel()
        player_list = filter(lambda seat: seat.status == Seat.SEAT_PLAYING, self.seats)
        if len(self.poker_controller.publicCard) == 5:
            print "We have a winner!"
            print "Amount in prize_pool: ", self.prize_pool
            self.poker_controller.getWinner()
            sys.exit()
        else:
            for seat in player_list:
                if seat.status == Seat.SEAT_PLAYING:
                    self.prize_pool += seat.table_amount
                    seat.table_amount   = 0
            print "Amount in prize_pool: ", self.prize_pool
            self.min_amount = self.blind/2
            self.current_seat = self.info_next(self.current_dealer, [3,4,5])
            return

    def is_proper_amount(self, command, amount, seat_no):
        if command == 3:
            print "self.min_amount in proper amount: ", self.min_amount
            min_amount = 2 * self.min_amount - self.seats[seat_no].table_amount
        else:
            min_amount = self.min_amount - self.seats[seat_no].table_amount
        max_amount = min(max(self.player_stake), self.player_stake[seat_no])
        print "---------------min_amount: ", min_amount
        print "---------------max_amount: ", max_amount
        if amount > max_amount:
            return False
        elif amount < min_amount:
            return False
        else:
            return True


    def check_next(self, current_position):
        num_of_players = 0
        next = (current_position + 1) % len(self.seats)
        for x in xrange(9):
            if self.seats[next].status == Seat.SEAT_PLAYING:
                num_of_players += 1
                break
            else:
                next = (next + 1) % len(self.seats)

        if num_of_players < 1:
            print "no more players in this room"
            exit()
        return next

    def assign_role(self):
        number      = 0
        dealer      = -1
        small_blind = -1
        big_blind   = -1
        index       = (self.current_dealer + 1) % len(self.seats)
        for counter in xrange(9):
            if not self.seats[index].is_empty():
                number += 1
                if dealer == -1:
                    dealer = index
                elif small_blind == -1:
                    small_blind = index
                elif big_blind == -1:
                    big_blind   = index
                    break
            index = (index + 1) % len(self.seats)

        if number == 2:
            big_blind   = small_blind
            small_blind = dealer

        self.current_dealer = dealer
        self.small_blind    = small_blind
        self.big_blind      = big_blind
        print "current_dealer: ",   dealer
        print "small_blind: ",      small_blind
        print "big_blind: ",        big_blind
