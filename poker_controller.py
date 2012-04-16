import sys,random
from random import shuffle
#from dealer import Dealer
#from game_room import Seat

class Card:
	def __init__(self, symbol, value):
		self.symbol = symbol
		self.value = value

	def __cmp__(self, other):
		if self.value < other.value:
			return -1
		elif self.value == other.value:
			return 0
		return 1

	def __str__(self):
		text = ""
		if self.value < 0:
			return "Joker";
		elif self.value == 11:
			text = "J"
		elif self.value == 12:
			text = "Q"
		elif self.value == 13:
			text = "K"
		elif self.value == 14:
			text = "A"
		else:
			text = str(self.value)

		if self.symbol == 0:    #D-Diamonds
			text += "D"
		elif self.symbol == 1:  #H-Hearts
			text += "H"
		elif self.symbol == 2:  #S-Spade
			text += "S"
		else:   #C-Clubs
			text += "C"
		return text
class deck:
    #Initializes the deck, and adds jokers if specified
	def __init__(self, addJokers = False):
		self.cards = []
		self.inplay = []
		self.addJokers = addJokers
		for symbol in range(0,4):
			for value in range (2,15):
				self.cards.append( Card(symbol, value) )
		if addJokers:
			self.total_cards = 54
			self.cards.append( Card(-1, -1) )
			self.cards.append( Card(-1, -1) )
		else:
			self.total_cards = 52

    #Shuffles the deck
	def shuffle(self):
		self.cards.extend( self.inplay )
		self.inplay = []
		shuffle( self.cards )

    #Cuts the deck by the amount specified
    #Returns true if the deck was cut successfully and false otherwise
	def cut(self, amount):
		if not amount or amount < 0 or amount >= len(self.cards):
			return False #returns false if cutting by a negative number or more cards than in the deck
		temp = []
		for i in range(0,amount):
			temp.append( self.cards.pop(0) )
		self.cards.extend(temp)
		return True

    #Returns a data dictionary
	def deal(self, number_of_cards):
		if(number_of_cards > len(self.cards) ):
			return False #Returns false if there are insufficient cards

		inplay = []
		for i in range(0, number_of_cards):
			inplay.append( self.cards.pop(0) )

		self.inplay.extend(inplay)
		return inplay

	def cards_left(self):
		return len(self.cards)

class Poker:
	def __init__(self, number_of_players, debug = False):
		self.deck = deck()
		if number_of_players < 2 or number_of_players > 10:
			sys.exit("*** ERROR ***: Invalid number of players. It must be between 2 and 10.")
		self.number_of_players = number_of_players
		self.debug = debug  #This will print out the debug statements during execution

	def shuffle(self):
		self.deck.shuffle()

	def cut(self, amount):
		return self.deck.cut(amount)

	def getFlop(self):
        #Burns 3 cards, then returns the flop
		if not self.deck.deal(3):
			return False
		return self.deck.deal(3)

	def getOne(self):
	#Burns 1 card, then returns the flop
		if not self.deck.deal(1):
			return False
		return self.deck.deal(1)

    #===============================================
    #------------------Distribute-------------------
    #===============================================
	def distribute(self):
		number_of_cards = 2 #Each player gets 2 cards when playing by Texas Hold Em rules
		if(number_of_cards*self.number_of_players > self.deck.cards_left() ):
			return False

		inplay = []
		for i in range(0, self.number_of_players):
			inplay.append( [] )

        #Deals each player one card at a time
        #Has greater complexity, but simulates real life better
		for i in range(0, number_of_cards):
			for j in range(0, self.number_of_players):
				inplay[j].append( self.deck.deal(1).pop() )

		return inplay

	#===============================================
	#------------------Name of Hand-----------------
	#===============================================
	def name_of_hand(self, type_of_hand):
		if type_of_hand == 0:
			return "High Card"
		elif type_of_hand == 1:
			return "Pair"
		elif type_of_hand == 2:
			return "2 Pair"
		elif type_of_hand == 3:
			return "3 of a Kind"
		elif type_of_hand == 4:
			return "Straight"
		elif type_of_hand == 5:
			return "Flush"
		elif type_of_hand == 6:
			return "Full House"
		elif type_of_hand == 7:
			return "Four of a Kind"
		elif type_of_hand == 8:
			return "Straight Flush"
		else:
			return "Royal Flush"
	#===============================================
	#---------------------Score---------------------
	#===============================================
	def score(self, hand):
		score	= 0
		kicker	= []
		pairs	= {}
		prev	= 0

        #Keeps track of all the pairs in a dictionary where the key is the pair's card value
        #and the value is the number occurrences. Eg. If there are 3 Kings -> {"13":3}
		for i in range(len(hand)):
			card = hand[i]
			if prev == card.value:
				key = card.value
				if key in pairs:
					pairs[key] += 1
				else:
					pairs[key] = 2
			prev = card.value

        #Keeps track of the number of pairs and sets. The value of the previous dictionary
        #is the key. Therefore if there is a pair of 4s and 3 kings -> {"2":1,"3":1}
		nop = {}
		for k, v in pairs.iteritems():
			if v in nop:
				nop[v] += 1
			else:
				nop[v] = 1

        #Here we determine the best possible combination the hand can be knowing if the
        #hand has a four of a kind, three of a kind, and multiple pairs.

		if 4 in nop:        #Has 4 of a kind, assigns the score and the value of the
			score = 7
			kicker = pairs.keys()
			#ensures the first kicker is the value of the 4 of a kind
			kicker = [key for key in kicker if pairs[key] == 4]
			key = kicker[0]

			#Gets a list of all the cards remaining once the the 4 of a kind is removed
			temp = [card.value for card in hand if card.value != key]
			#Gets the last card in the list which is the highest remaining card to be used in
			#the event of a tie
			card_value = temp.pop()
			kicker.append(card_value)

			return [score, kicker] # Returns immediately because this is the best possible hand
			#doesn't check get the best 5 card hand if all users have a 4 of a kind

		elif 3 in nop:      #Has At least 3 of A Kind
			if nop[3] == 2 or 2 in nop:     #Has two 3 of a kind, or a pair and 3 of a kind (fullhouse)
				score = 6

				#gets a list of all the pairs and reverses it
				kicker = pairs.keys()
				kicker.reverse()
				temp = kicker

				#ensures the first kicker is the value of the highest 3 of a king
				kicker = [key for key in kicker if pairs[key] == 3]
				if( len(kicker) > 1):   # if there are two 3 of a kinds, take the higher as the first kicker
					kicker.pop() #removes the lower one from the kicker

				#removes the value of the kicker already in the list
				temp.remove(kicker[0])
				#Gets the highest pair or 3 of kind and adds that to the kickers list
				card_value = temp[0]
				kicker.append(card_value)

			else:  #Has Only 3 of A Kind
				score = 3

				kicker = pairs.keys()       #Gets the value of the 3 of a king
				key = kicker[0]

				#Gets a list of all the cards remaining once the three of a kind is removed
				temp = [card.value for card in hand if card.value != key]
				#Get the 2 last cards in the list which are the 2 highest to be used in the
				#event of a tie
				card_value = temp.pop()
				kicker.append(card_value)

				card_value = temp.pop()
				kicker.append(card_value)

		elif 2 in nop:      #Has at Least a Pair
			if nop[2] >= 2:     #Has at least 2  or 3 pairs
				score = 2

				kicker = pairs.keys()   #Gets the card value of all the pairs
			#	kicker.reverse()        #reverses the key so highest pairs are used
				kicker.sort(reverse=True)
				if ( len(kicker) == 3 ):    #if the user has 3 pairs takes only the highest 2
					kicker.pop()
				key1 = kicker[0]
				key2 = kicker[1]

				#Gets a list of all the cards remaining once the the 2 pairs are removed
				temp = [card.value for card in hand if card.value != key1 and card.value != key2]
				#Gets the last card in the list which is the highest remaining card to be used in
				#the event of a tie
				card_value = temp.pop()
				kicker.append(card_value)

			else:           #Has only a pair
				score = 1

				kicker = pairs.keys()   #Gets the value of the pair
				key = kicker[0]

				#Gets a list of all the cards remaining once pair are removed
				temp = [card.value for card in hand if card.value != key]
				#Gets the last 3 cards in the list which are the highest remaining cards
				#which will be used in the event of a tie
				card_value = temp.pop()
				kicker.append(card_value)

				card_value = temp.pop()
				kicker.append(card_value)

				card_value = temp.pop()
				kicker.append(card_value)


        #------------------------------------------------
        #------------Checking for Straight---------------
        #------------------------------------------------
		#Doesn't check for the ace low straight
		counter = 0
		high = 0
		straight = False

#Checks to see if the hand contains an ace, and if so starts checking for the straight
#using an ace low
		if (hand[6].value == 14):
			prev = 1
		else:
			prev = None

        #Loops through the hand checking for the straight by comparing the current card to the
        #the previous one and tabulates the number of cards found in a row
        #***It ignores pairs by skipping over cards that are similar to the previous one
		for card in hand:
			if prev and card.value == (prev + 1):
				counter += 1
				if counter >= 4: #A straight has been recognized
					straight = True
					high = card.value
			elif prev and prev == card.value: #ignores pairs when checking for the straight
				pass
			else:
				counter = 0
			prev = card.value

	#If a straight has been realized and the hand has a lower score than a straight
		if (straight or counter >= 4) and score < 4:
			straight = True
			score = 4
			kicker = [high] #Records the highest card value in the straight in the event of a tie


        #------------------------------------------------
        #-------------Checking for Flush-----------------
        #------------------------------------------------
		flush = False
		total = {}

        #Loops through the hand calculating the number of cards of each symbol.
        #The symbol value is the key and for every occurrence the counter is incremented
		for card in hand:
			key = card.symbol
			if key in total:
				total[key] += 1
			else:
				total[key] = 1

        #key represents the suit of a flush if it is within the hand
		key = -1
		for k, v in total.iteritems():
			if v >= 5:
				key = int(k)

        #If a flush has been realized and the hand has a lower score than a flush
		if key != -1 and score < 5:
			flush = True
			score = 5
			kicker = [card.value for card in hand if card.symbol == key]


        #------------------------------------------------
        #-----Checking for Straight & Royal Flush--------
        #------------------------------------------------
		if flush and straight:
            #Doesn't check for the ace low straight
			counter = 0
			high = 0
			straight_flush = False

            #Checks to see if the hand contains an ace, and if so starts checking for the straight
            #using an ace low
			if (kicker[len(kicker)-1] == 14):
				prev = 1
			else:
				prev = None

            #Loops through the hand checking for the straight by comparing the current card to the
            #the previous one and tabulates the number of cards found in a row
            #***It ignores pairs by skipping over cards that are similar to the previous one
			for card in kicker:
				if prev and card == (prev + 1):
					counter += 1
					if counter >= 4: #A straight has been recognized
						straight_flush = True
						high = card
				elif prev and prev == card: #ignores pairs when checking for the straight
					pass
				else:
					counter = 0
				prev = card
	#If a straight has been realized and the hand has a lower score than a straight
			if straight_flush:
				if high == 14:
					score = 9
				else:
					score = 8
				kicker = [high]
				return [score, kicker]

		if flush:     #if there is only a flush then determines the kickers
			kicker.reverse()
			#This ensures only the top 5 kickers are selected and not more.
			length = len(kicker) - 5
			for i in range (0,length):
				kicker.pop() #Pops the last card of the list which is the lowest

			#------------------------------------------------
			#-------------------High Card--------------------
			#------------------------------------------------
		if score == 0: #If the score is 0 then high card is the best possible hand

		#It will keep track of only the card's value
			kicker = [int(card.value) for card in hand]
		#Reverses the list for easy comparison in the event of a tie
			kicker.reverse()
		#Since the hand is sorted it will pop the two lowest cards position 0, 1 of the list
			kicker.pop()
			kicker.pop()
		#The reason we reverse then pop is because lists are inefficient at popping from
		#the beginning of the list, but fast at popping from the end therefore we reverse
		#the list and then pop the last two elements which will be the two lowest cards
		#in the hand
		#Return the score, and the kicker to be used in the event of a tie
		return [score, kicker]



#===============================================
#---------------Determine Score-----------------
#===============================================
	def determine_score(self, community_cards, users):
		for user in users:
			user.handcards.extend(community_cards)
			user.handcards.sort()

		results = []
		if self.debug:      #Outputs the debug statements
			print "---- Determining Scores----"
		for user in users:
			overall = self.score(user.handcards)
			results.append([overall[0], overall[1]])
			user.combination=overall

			if self.debug:      #Outputs the debug statements
				text = "Hand -- "
				for c in hand:
					text += str(c) + "  "
				kicker = ""
				for c in overall.pop(1):
					try:
						kicker += str(c) + "  "
					except:
						kicker += str(c) + "  "
				print text + "Score: " + str(overall.pop(0)) + ", Kicker: " + kicker
		return results

    #===============================================
    #---------------Determine Winner----------------
    #===============================================
	def determine_winner(self, results):
		if self.debug:
			print "---- Determining Winner----"

		#the highest score if found
		high = 0
		for r in results:
			if r.combination[0] > high:
				high = r.combination[0]

			if self.debug:
				print r

		kicker = {}
		counter = 0
		#Only the kickers of the player's hands that are tied for the win are analysed
		for r in results:
			if r.combination[0] == high:
				kicker[counter] = r.combination[1]

			counter += 1
		if(len(kicker) > 1):
			print "high", high
			print kicker
			number_of_kickers = len(kicker[kicker.keys().pop()])
			print "number of kickers",number_of_kickers
			print kicker[0]

			for i in range (0, number_of_kickers):
				high = 0
				for k, v in kicker.items():
					if v[i] > high:
						high = v[i]

				kicker = {k:v for k, v in kicker.items() if v[i] == high}

				print "---- " + "Round " + str(i) + " ----"
				for k in kicker:
					print k

				if( len(kicker) <= 1):
					return kicker.keys().pop()

		else:   # A clear winner was found
			return kicker.keys().pop()

		return kicker.keys()

class PokerController(object):
	def __init__(self, seats, debug=False):
		self.seats	= seats
		self.debug	= debug

	def start(self):
		self.users			= filter(lambda seat: seat.is_waiting(), self.seats)
		number_of_players	= len(self.users)
		print "length of users in poker controller %d" % number_of_players
		self.publicCard		= []
		self.poker			= Poker(number_of_players, self.debug)
		self.poker.shuffle()
		self.players_hands	= self.poker.distribute()
		for i in range(number_of_players):
			self.users[i].handcards = self.players_hands[i]


	def getFlop(self):
		card = self.poker.getFlop()
		self.publicCard.extend(card)

	def getOne(self):
		card = self.poker.getOne()
		self.publicCard.extend(card)

	def _compare(self, element_1, element_2):
		hand_card_1 = element_1.combination
		hand_card_2 = element_2.combination
		if hand_card_1[0] != hand_card_2[0] :
			return hand_card_1[0] - hand_card_2[0]
		else:
			for i in xrange(len(hand_card_1[1])):
				if hand_card_1[1][i] != hand_card_2[1][i]:
					return hand_card_1[1][i] - hand_card_2[1][i]
		return 0

	def rank_users(self):
		rank	= []
		matured	= False
		self.poker.determine_score(self.publicCard, self.users)
		self.users.sort(self._compare, reverse=True)
		for i in xrange(len(self.users)):
			matured = False
			for k in xrange(len(rank)):
				if self._compare(self.users[i], rank[k][0]) == 0:
					rank[k].append(self.users[i])
					matured = True
					break
			if not matured:
				rank.append( [self.users[i]])
		return rank

	def get_winner(self):
		winner_list	= []
		loser_list	= []
		if self.poker:
			#score_list	= self.poker.determine_score(self.publicCard, self.users)
			self.users.sort(self._compare, reverse=True)
			winner	= self.poker.determine_winner(self.users)
			tie		= True
			if not isinstance(winner,list):
				winner_list.append(self.users[0])
				loser_list = self.users[1:]
			else:
				for win_id in winner:
					winner_list.append(self.users[win_id])
				loser_list = self.users[winner[len(winner)-1]+1:]


			for win in winner_list:
				text = "Winner ** "
				for c in win.handcards:
					text += str(c) + "  "
				text += " --- " + self.poker.name_of_hand(win.combination[0])
				print text
			for loser in loser_list:
				text = "Loser  -- "
				for c in loser.handcards:
					text += str(c) + "  "
				text += " --- " + self.poker.name_of_hand(loser.combination[0])
				print text

			return { "winners":winner_list, "losers":loser_list }
'''
class User:
	def __init__(self):
		self.combination=[]
		self.handcards=[]


users=[]
for i in range(2):
	users.append(User())
debug = False
#generate 2 cards for each users
#get it from PokerController.player_hands
pokerController = PokerController(users)
pokerController.start()
#get the first 3 cards
pokerController.getFlop()

#get the next one
pokerController.getOne()

#get the next final card
pokerController.getOne()
print pokerController.rank_users()
r = pokerController.get_winner()
print len(r['winners']),len(r['losers'])
'''
