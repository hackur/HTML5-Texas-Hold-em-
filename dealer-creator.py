import os
import sys
from optparse import OptionParser
from dealer import Dealer

parser = OptionParser()
parser.add_option('-q', '--queue', action='store', dest='queue_id', help='name of the queue to be assigned')
parser.add_option('-e', '--exchange', action='store', dest='exchange_id', help='name of the exchange to be assigned')
(options, args) = parser.parse_args(sys.argv)

if(options.queue_id):
	print "queue :" + options.queue_id
if(options.exchange_id):
	print "queue :" + options.exchange_id

newpid = os.fork()
if newpid == 0:
	dealer = Dealer(queue = options.queue_id, exchange = options.exchange_id)
	dealer.start()
else:
	pids = (os.getpid(), newpid)
	print "parent: %d, child: %d" % pids
