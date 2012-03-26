import sys,random
from random import shuffle

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
    
    #===============================================
    #------------------Constructor-----------------
    #===============================================
    def __init__(self, number_of_players, debug = False):
        self.deck = deck()
        if number_of_players < 2 or number_of_players > 10:
            sys.exit("*** ERROR ***: Invalid number of players. It must be between 2 and 10.")
        self.number_of_players = number_of_players
        self.debug = debug  #This will print out the debug statements during execution
        #Here is were we would extend and add betting, number of players etc....
    
    #===============================================
    #------------------Shuffle----------------------
    #===============================================    
    def shuffle(self):
        self.deck.shuffle()    
        
    #===============================================
    #------------------Cut----------------------
    #===============================================    
    def cut(self, amount):
        return self.deck.cut(amount)
    
    #===============================================
    #------------------Get Flop---------------------
    #===============================================    
    def getFlop(self):  
        #Burns 3 cards, then returns the flop
        if not self.deck.deal(3):
            return False
        return self.deck.deal(3)
    
    #===============================================
    #------------------Get One----------------------
    #===============================================
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
                    
        #Returns a lists of all the hands, which is a list of cards
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
        
        score = 0
        kicker = []
        
        #------------------------------------------------
        #-------------Checking for Pairs-----------------
        #------------------------------------------------
        pairs = {}
        prev = 0
        
        #Keeps track of all the pairs in a dictionary where the key is the pair's card value
        #and the value is the number occurrences. Eg. If there are 3 Kings -> {"13":3} 
        for card in hand:
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
                
            else:           #Has Only 3 of A Kind
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
                kicker.reverse()        #reverses the key so highest pairs are used
                
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
                if counter == 4: #A straight has been recognized
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
        if score == 0:      #If the score is 0 then high card is the best possible hand
            
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
        
        '''
        for hand in players_hands:
            hand.extend(community_cards)
            hand.sort()
    	'''

    	for user in users:
    		user.handcards.extend(community_cards)
    		user.handcards.sort()

        results = []
        if self.debug:      #Outputs the debug statements
            print "---- Determining Scores----"
        '''
        for hand in players_hands:
                     
            overall = self.score(hand)
            results.append([overall[0], overall[1]])    # Stores the results

            
            
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
        '''
        for user in users:
                     
            overall = self.score(user.handcards)
            results.append([overall[0], overall[1]])    # Stores the results
            #user.addCalResult(overall)
            user.calResult=overall
            
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
            if r[0] > high:
                high = r[0]
            
            if self.debug:
                print r
        
        kicker = {}    
        counter = 0
        #Only the kickers of the player's hands that are tied for the win are analysed
        for r in results:
            if r[0] == high:
                kicker[counter] = r[1]
                
            counter += 1
        
        #if the kickers of multiple players are in the list then we have a tie and need
        #to begin comparing kickers 
        if(len(kicker) > 1):
            
            if self.debug: #Outputs the debug statements
                print "---- Tie Braker ----"
                print "---- Kicker ----"
                for k, v in kicker.items():
                    print str(k) + " : " + str(v)
            
            #Iterate through all the kickers
            #It is important to the number of kickers differ based on the type of hand
            number_of_kickers = len(kicker[kicker.keys().pop()])
            for i in range (0, number_of_kickers):
                high = 0
                for k, v in kicker.items():
                    if v[i] > high:
                        high = v[i]
                
                #only hands matching the highest kicker remain in the list to be compared
                kicker = {k:v for k, v in kicker.items() if v[i] == high}
                
                if self.debug: #Outputs the debug statements of which
                    print "---- " + "Round " + str(i) + " ----"
                    for k in kicker:
                        print k
                        
                #if only one the kickers of one player remains that they are the winner
                if( len(kicker) <= 1):
                    return kicker.keys().pop()
                
        else:   # A clear winner was found
            return kicker.keys().pop()
        
        # A tie occurred, a list of the winners is returned
        return kicker.keys()

class PokerController(object):
	poker=None
	publicCard=[]
	players_hands=[]
	users=[]
	@staticmethod
	def init(users,debug=False):
		number_of_players=len(users)
		#init the poker game ,set debug=True to view the produce
		PokerController.users=users
		PokerController.poker=Poker(number_of_players,debug)
		#Shuffle
		PokerController.poker.shuffle()
		
		#Cutting? I dont get the rule of it
		#poker.cut(random.randint(1,51))

		#Distributing 
		PokerController.players_hands=PokerController.poker.distribute()
		
		for i in range(number_of_players):
			#users[i].addHands(PokerController.players_hands[i])
			users[i].handcards=PokerController.players_hands[i]




		'''
		# @@warning deprecated
		for i in range(len(userIdArr)):
			PokerController.players_hands[i].extend([userIdArr[i]])
				
		for k in range(5):
			print PokerController.players_hands[k][2],"======"
		'''
		


		if debug:
			print "In Players Hands"
			print "-----------------------"
			for hand in PokerController.players_hands:
				text='Player - '
				for card in hand:
					text+=str(card)+ " "
				print text
			print "-----------------------"

	#get 3 cards
	@staticmethod  
	def getFlop():
		if PokerController.poker:
			card=PokerController.poker.getFlop()
			PokerController.publicCard.extend(card)

	#get 1 card
	@staticmethod
	def getOne():
		if PokerController.poker and PokerController.publicCard:
			card=PokerController.poker.getOne()
			PokerController.publicCard.extend(card)

	#def __determine_score(cls,publicCard,players_hands):


	@staticmethod
	def getWinner():
		winnerArr=[]
		loserArr=[]
		if PokerController.poker:
			#results=PokerController.poker.determine_score(PokerController.publicCard, PokerController.players_hands)
			results=PokerController.poker.determine_score(PokerController.publicCard, PokerController.users)
			winner=PokerController.poker.determine_winner(results)
			tie = True
			try:
			    len(winner)
			except:
			    tie = False

			if not tie:
			    counter = 0
			    print "-------- Winner has Been Determined --------"
			    for hand in PokerController.players_hands:
			        if counter == winner:
			            text = "Winner ** "
			            #winnerArr.extend([results[counter]])
			            for ur in PokerController.users:
			            	if ur.calResult == results[counter]:
			            		winnerArr.append(PokerController.users[counter])
			            		#print "tie ",tie,"winner here"

			        else:
			            text = "Loser  -- "
			            #loserArr.extend([results[counter]])
			            loserArr.append(PokerController.users[counter])
			        for c in hand:
			            text += str(c) + "  "

			        text += " --- " + PokerController.poker.name_of_hand(results[counter][0])
			        counter += 1
			        print text

			else:
			    counter = 0
			    print "--------- Tie has Been Determined --------"
			    for hand in PokerController.players_hands:
			        if counter in winner:

			            text = "Winner ** "
			            #winnerArr.extend([results[counter]])
			            for ur in PokerController.users:
			            	if ur.calResult == results[counter]:
				            		winnerArr.append(PokerController.users[counter])
				            		winnerArr=list(set(winnerArr))
				            		#print "tie ",tie,"winner here"

			        else:
			            text = "Loser  -- "
			            #loserArr.extend([results[counter]])
			            loserArr.append(PokerController.users[counter])
			        for c in hand:
			            text += str(c) + "  "

			        text += " --- " + PokerController.poker.name_of_hand(results[counter][0])
			        counter += 1
			        print text

			return {
				"winners":winnerArr,
				"losers":loserArr
			}



class User:

	def __init__(self):
		self.calResult=[]
		self.handcards=[]


users=[]
for i in range(7):
	users.append(User())
debug=False
#generate 2 cards for each users
#get it from PokerController.player_hands
PokerController.init(users)

'''
e.g.
for hc in PokerController.players_hands:
	userInstances[i].hands=hc
	#hc is an array with 2 cards instance
	#hc is short term of handcard
'''



#get the first 3 cards
PokerController.getFlop()

#get the next one 
PokerController.getOne()

#get the next final card
PokerController.getOne()

'''
#All the public card saved here:
PokerController.publicCard
'''


print len(PokerController.users)
r=PokerController.getWinner()
print len(r['winners']),len(r['losers'])








