import time
import pika
import sys
from optparse import OptionParser
import random
# import PokerController
import poker_controller
from game_room import GameRoom
from sqlalchemy.orm import sessionmaker,relationship, backref
from database import DatabaseConnection,User,Room,MessageQueue
try:
    import cpickle as pickle
except:
    import pickle




class Cards(object):
    def __init__(self):
        self._cards = []
        self._cardCount = 52
        for i in xrange(4):
            self._cards.append(range(1,14))

    def next(self):
        ram = random.randint(0,self._cardCount)
        for i in xrange(4):
            if ram >= len(self._cards[i]):
                ram -= len(self._cards[i])
            else:
                self._cardCount -= 1
                return self._cards[i][ram]

class Dealer(object):
#   users = []
    # waiting_list = {}
    suit = ["DIAMOND", "HEART", "SPADE", "CLUB"]
    face = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
#   room_list = []
    number_of_players = 9

    def __init__(self,queue,exchange,num_of_seats=9,blind=100,host='localhost',port=5672):
        self.queue      = queue
        self.exchange   = exchange
        self.host       = host
        self.port       = port
        self.room_list  = {}
        self.users      = []


    def init_database(self):
        self.db_connection  = DatabaseConnection()
        self.db_connection.init("sqlite:///:memory:")
        self.db_connection.connect()
        self.db_connection.start_session()
        room        = Room(exchange="dealer_exchange_1")
        queue1      = MessageQueue(queue_name="queue_1",room = room)
        queue2      = MessageQueue(queue_name="queue_2",room = room)
        queue3      = MessageQueue(queue_name="queue_3",room = room)
        queue4      = MessageQueue(queue_name="queue_4",room = room)
        queue5      = MessageQueue(queue_name="queue_5",room = room)
        queue6      = MessageQueue(queue_name="queue_6",room = room)
        queue7      = MessageQueue(queue_name="queue_7",room = room)
        queue8      = MessageQueue(queue_name="queue_8",room = room)
        queue9      = MessageQueue(queue_name="queue_9",room = room)
        ting        = User(username="ting", password="123", stake = 100)
        mile        = User(username="mile", password="123", stake = 500)
        mamingcao   = User(username="mamingcao", password="123", stake = 200)
        huaqin      = User(username="huaqin", password="123", stake = 500)
        self.db_connection.addItem(ting)
        self.db_connection.addItem(mile)
        self.db_connection.addItem(huaqin)
        self.db_connection.addItem(mamingcao)
        self.db_connection.addItem(room)
        self.db_connection.addItem(queue1)
        self.db_connection.addItem(queue2)
        self.db_connection.addItem(queue3)
        self.db_connection.addItem(queue4)
        self.db_connection.addItem(queue5)
        self.db_connection.addItem(queue6)
        self.db_connection.addItem(queue7)
        # ting.friends = [mile, mamingcao]
        # mile.friends = [ting]
        self.db_connection.commit_session()

    def start(self):
        self.connection = pika.BlockingConnection(
        pika.ConnectionParameters(host = self.host,
                                    port = self.port))
        self.channel    = self.connection.channel()
        self.channel.exchange_declare(exchange      = self.exchange,
                                        type        = 'topic',
                                        auto_delete = True,
                                        durable     = False)
        self.channel.queue_declare(queue    = self.queue,
                                auto_delete = True,
                                durable     = False,
                                exclusive   = False)

        self.channel.queue_bind(exchange    = self.exchange,
                                queue       = self.queue,
                                routing_key = 'dealer')
        self.channel.basic_consume(self.on_message, self.queue, no_ack=True)
        self.channel.start_consuming()

    def cmd_action(self, args):
        print "-------------------------------------------------user trying to bet"
        self.db_connection.start_session()
        action          = args["action"]
        private_key     = args["private_key"]
        user_id         = args["user_id"]
        current_room    = self.room_list[args["room_id"]]
        if action == 1:
            current_room.all_in(user_id, private_key)
        elif action == 2:
            current_room.call_stake(user_id, private_key)
        elif action == 3:
            amount = args['amount']
            current_room.raise_stake(user_id, private_key, amount)
        elif action == 4:
            current_room.check(user_id, private_key)
        elif action == 5:
            current_room.discard_game(private_key)


    def cmd_sit(self, args):
        print "sit received"
        self.db_connection.start_session()
        source          = args['source']
        private_key     = args['private_key']
        user            = self.db_connection.query(User).filter_by(id=args['user_id']).first()
        current_room    = self.room_list[args["room_id"]]
        (status, msg)   = current_room.sit(user, int(args["seat"])-1, source, private_key)

        if status:
            message = {"status": "success" }
        else:
            message = {"status": "failed", "msg": msg}
        self.channel.basic_publish( exchange    = self.exchange,
                                    routing_key = source,
                                    body        = pickle.dumps(message))

    def broadcast(self, routing_key, msg):
        self.channel.basic_publish(exchange     = self.exchange,
                                    routing_key = routing_key,
                                    body        = pickle.dumps(msg))

    def cmd_init(self,args):
        if args['room_id'] not in self.room_list:
            self.cmd_create_room(args)
            print "Room created"

        current_room = self.room_list[args["room_id"]]
        current_room.add_audit({'user':args["user_id"]})

        routing_key = args['source']
        message     = {'status':'success', 'content':'nothing', 'timestamp':time.time()}
        self.channel.basic_publish( exchange    = self.exchange,
                                    routing_key = routing_key,
                                    body        = pickle.dumps(message))


    def cmd_create_room(self, args):
        print "creating room"
        self.room_list[args['room_id']] = GameRoom(args["room_id"], args["user_id"], self)



    def on_message(self, channel, method, header, body):
        message = "message received, thanks!"
        obj = pickle.loads(body)
        print obj['method']
        method = getattr(self,"cmd_" + obj['method'])
        method(obj)


    def close(self):
        self.connection.close()


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option('-q', '--queue', action='store', dest='queue_id', help='name of the queue to be assigned')
    parser.add_option('-e', '--exchange', action='store', dest='exchange_id', help='name of the exchange to be assigned')
    (options, args) = parser.parse_args(sys.argv)

    if not options.queue_id :
        options.queue_id = "dealer_queue_1"

    print "queue :" + options.queue_id

    if not options.exchange_id:
        options.exchange_id = "dealer_exchange_1"

    print "queue :" + options.exchange_id

    dealer = Dealer(queue = options.queue_id, exchange = options.exchange_id)
    dealer.init_database()
    dealer.start()

    # print dealer.seats


    # db = DatabaseConnection()

    # users = {}
    # for user in db.query(User):
    #   users[user.id] = user.username

    # print users
    # # print len(users)
    # players = []
    # for i in xrange(len(users)):
    #   players.append(PokerController.User())
    #   players[i].name = users[i+1]
    #   # print players[i].name
    #   i += 1

    # print len(players)
    # PokerController.PokerController.init(players)
    # PokerController.PokerController.getFlop()

    # #get the next one
    # PokerController.PokerController.getOne()

    # #get the next final card
    # PokerController.PokerController.getOne()
    # r = PokerController.PokerController.getWinner()
    # for user in r["winners"]:
    #   print "WINNER IS: " + user.name

