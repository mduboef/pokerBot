import random as rand

SUIT = ['C', 'D', 'H', 'S']
CARD = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

def generateDeck(suit, card, holeCards, commCards):
    deck = []
    for suit in SUIT:
        for card in CARD:
            suitCard = suit + card
            if suitCard not in holeCards and suitCard not in commCards:
                deck.append(suitCard)
    return deck

def sampleDeck(deck, knownCards):
    sample = [i for i in knownCards]
    revieledCards = rand.sample(deck, 7 - len(knownCards))
    for card in revieledCards:
        sample.append(card)
    return sample

def sortCards(cards):
    sortedCards = []
    for card in CARD:
        for i in range(len(cards)):
            if card == cards[i]:
                sortedCards.append(card)
    return sortedCards

def processCards(cards):
    clubs = []
    diamonds = []
    hearts = []
    spades = []
    values = []
    for card in cards:
        if card[0] == 'C':
            clubs.append(card[1:])
        elif card[0] == 'D':
            diamonds.append(card[1:])
        elif card[0] == 'H':
            hearts.append(card[1:])
        else:
            spades.append(card[1:])
        values.append(card[1:])
    return {'cards':cards, 'C':sortCards(clubs), 'D':sortCards(diamonds), 'H':sortCards(hearts), 'S':sortCards(spades), 'values':sortCards(values)}

def checkRoyalFlush(processedCards):
    royalFlush = ['10', 'J', 'Q', 'K', 'A']
    clubs = True
    diamonds = True
    hearts = True
    spades = True
    for suit in SUIT:
        for card in royalFlush:
            if card not in processedCards[suit]:
                if suit == 'C':
                    clubs = False
                elif suit == 'D':
                    diamonds = False
                elif suit == 'H':
                    hearts = False
                else:
                    spades = False
    return clubs or diamonds or hearts or spades

def checkStraightFlush(processedCards):
    for suit in SUIT:
        if len(processedCards[suit]) > 4:
            for myCardIndex in range(len(processedCards[suit])):
                succesiveCards = 0
                trueCardIndex = 0
                while CARD[trueCardIndex] is not processedCards[suit][myCardIndex]:
                    trueCardIndex += 1
                while CARD[trueCardIndex] is processedCards[suit][myCardIndex]:
                    myCardIndex += 1
                    trueCardIndex += 1
                    succesiveCards += 1
                    if myCardIndex >= len(processedCards[suit]) or trueCardIndex >= len(CARD):
                        break
                if succesiveCards > 4:
                    return True
    return False
                
def checkFourKind(processedCards):
    for card in processedCards['C']:
        if card in processedCards['D'] and card in processedCards['H'] and card in processedCards['S']:
            return True
    return False

def checkFullHouse(processedCards):
    two = False
    three = False
    for card in CARD:
        count = 0
        for i in range(len(processedCards['values'])):
            if card is processedCards['values'][i]:
                count += 1
        if count > 2:
            three = True
        elif count > 1:
            two = True
        if three and two:
            return True
    return False

def checkFlush(processedCards):
    for suit in SUIT:
        if len(processedCards[suit]) > 4:
            return True
    return False

def checkStraight(processedCards):
    for myCardIndex in range(len(processedCards['values'])):
        succesiveCards = 0
        trueCardIndex = 0
        while CARD[trueCardIndex] is not processedCards['values'][myCardIndex]:
            trueCardIndex += 1
        while CARD[trueCardIndex] is processedCards['values'][myCardIndex]:
            while myCardIndex + 1 < len(processedCards['values']) and processedCards['values'][myCardIndex] is processedCards['values'][myCardIndex + 1]:
                myCardIndex += 1
                if myCardIndex + 1 >= len(processedCards['values']):
                    break
            myCardIndex +=1
            trueCardIndex +=1
            succesiveCards += 1
            if myCardIndex >= len(processedCards['values']) or trueCardIndex >= len(CARD):
                break
        if succesiveCards > 4:
            return True
    return False

def checkThreeKind(processedCards):
    for card in processedCards['values']:
        count = 0
        for cardIndex in range(len(processedCards['values'])):
            if card is processedCards['values'][cardIndex]:
                count += 1
                if count > 2:
                    return True
    return False

def checkTwoPair(processedCards):
    pairCount = 0
    for card in CARD:
        count = 0
        for i in range(len(processedCards['values'])):
            if card is processedCards['values'][i]:
                count += 1
        if count > 1:
            pairCount += 1
            if pairCount > 1:
                return True
    return False

def checkPair(processedCards):
    for card in CARD:
        count = 0
        for i in range(len(processedCards['values'])):
            if card is processedCards['values'][i]:
                count += 1
        if count > 0:
            return True
    return False

def checkHigh(processedCards):
    return True

def handDistribution(SUIT, CARD, holeCards, commCards, n, myDict):
    knownCards = [i for i in holeCards]
    for card in commCards:
        knownCards.append(card)
    knownCardsKey = tuple(knownCards)
    if knownCardsKey in myDict.keys():
        return myDict
    royalFlush = 0
    straightFlush = 0
    fourKind = 0
    fullHouse = 0
    flush = 0
    straight = 0
    threeKind = 0
    twoPair = 0
    pair = 0
    high = 0
    deck = generateDeck(SUIT, CARD, holeCards, commCards)
    
    for _ in range(n):
        sample = processCards(sampleDeck(deck, knownCards))
        if checkRoyalFlush(sample) is True:
            royalFlush += 1
        elif checkStraightFlush(sample) is True:
            straightFlush += 1
        elif checkFourKind(sample) is True:
            fourKind += 1
        elif checkFullHouse(sample) is True:
            fullHouse += 1
        elif checkFlush(sample) is True:
            flush += 1
        elif checkStraight(sample) is True:
            straight += 1
        elif checkThreeKind(sample) is True:
            threeKind += 1
        elif checkTwoPair(sample) is True:
            twoPair += 1
        elif checkPair(sample) is True:
            pair += 1
        elif checkHigh(sample) is True:
            high += 1
    myDict.update({knownCardsKey:{'Royal Flush':royalFlush/n, 'Straight Flush':straightFlush/n, 'Four Kind':fourKind/n, 'Full House':fullHouse/n, 'Flush':flush/n, 'Straight':straight/n, 'Three Kind':threeKind/n, 'Two Pair':twoPair/n, 'Pair':pair/n, 'High':high/n}})
    return myDict

if __name__ == '__main__':
    dict = handDistribution(SUIT, CARD, ['C6', 'DK'], [], 100000, {})
    print(dict)
    dict = handDistribution(SUIT, CARD, ['CA', 'H7'], [], 100000, dict)
    print(dict)
