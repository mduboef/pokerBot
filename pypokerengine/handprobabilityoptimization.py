import random as rand
import time as time

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
    sample = [*knownCards]
    revieledCards = rand.sample(deck, 7 - len(knownCards))
    sample += revieledCards
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
            clubs.append(cardToIndex(card[1:]))
        elif card[0] == 'D':
            diamonds.append(cardToIndex(card[1:]))
        elif card[0] == 'H':
            hearts.append(cardToIndex(card[1:]))
        else:
            spades.append(cardToIndex(card[1:]))
        values.append(cardToIndex(card[1:]))
    clubs.sort()
    diamonds.sort()
    hearts.sort()
    spades.sort()
    values.sort()
    return {'cards':cards, 'C':clubs, 'D':diamonds, 'H':hearts, 'S':spades, 'values':values}

def cardToIndex(card):
    if card == '2':
        return 0
    elif card == '3':
        return 1
    elif card == '4':
        return 2
    elif card == '5':
        return 3
    elif card == '6':
        return 4
    elif card == '7':
        return 5
    elif card == '8':
        return 6
    elif card == '9':
        return 7
    elif card == '10':
        return 8
    elif card == 'J':
        return 9
    elif card == 'Q':
        return 10
    elif card == 'K':
        return 11
    elif card == 'A':
        return 12

def checkRoyalFlushOpt(processedCards):
    royalFlush = {8, 9, 10, 11, 12}
    for suit in SUIT:
        if set(royalFlush).issubset(set(processedCards[suit])):
            return True
    return False

def checkStraightFlushOpt(processedCards):
    for suit in SUIT:
        if len(processedCards[suit]) > 4:
            for cardIndex in processedCards[suit]:
                straightFlush = list(range(cardIndex, cardIndex + 5))
                if set(straightFlush).issubset(set(processedCards[suit])):
                    return True
    return False
                
def checkFourKindOpt(processedCards):
    for card in processedCards['C']:
        if card in processedCards['D'] and card in processedCards['H'] and card in processedCards['S']:
            return True
    return False

def checkFullHouseOpt(processedCards):
    two = False
    three = False
    valuesSet = set(processedCards['values'])
    for value in valuesSet:
        if processedCards['values'].count(value) > 1:
            if processedCards['values'].count(value) > 2:
                three = True
            else:
                two = True
    return two and three

def checkFlush(processedCards):
    for suit in SUIT:
        if len(processedCards[suit]) > 4:
            return True
    return False

def checkStraightOpt(processedCards):
    for cardIndex in processedCards['values']:
        straight = set(range(cardIndex, cardIndex + 5))
        if straight.issubset(set(processedCards['values'])):
            return True
    return False

def checkThreeKindOpt(processedCards):
    for card in processedCards['values']:
        if processedCards['values'].count(card) > 2:
            return True
    return False

def checkTwoPairOpt(processedCards):
    one = False
    for card in set(processedCards['values']):
        if processedCards['values'].count(card) > 1 and one:
            return True
        elif processedCards['values'].count(card) > 1:
            one = True
    return False

def checkPairOpt(processedCards):
    for card in processedCards['values']:
        if processedCards['values'].count(card) > 1:
            return True
    return False

def checkHigh(processedCards):
    return True

def handDistribution(SUIT, CARD, holeCards, commCards, n, myDict):
    startTime = time.time()
    knownCards = [*holeCards]
    knownCards += commCards
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
        isFlush = False
        if checkFlush(sample) is True:
            if checkStraightFlushOpt(sample) is True:
                if checkRoyalFlushOpt(sample) is True:
                    royalFlush += 1
                else:
                    straightFlush += 1
            else:
                isFlush = True
        elif checkFourKindOpt(sample) is True:
            fourKind += 1
        elif checkFullHouseOpt(sample) is True:
            fullHouse += 1
        elif isFlush is True:
            flush += 1
        elif checkStraightOpt(sample) is True:
            straight += 1
        elif checkThreeKindOpt(sample) is True:
            threeKind += 1
        elif checkTwoPairOpt(sample) is True:
            twoPair += 1
        elif checkPairOpt(sample) is True:
            pair += 1
        else:
            high += 1
    myDict.update({knownCardsKey:{'Royal Flush':royalFlush/n, 'Straight Flush':straightFlush/n, 'Four Kind':fourKind/n, 'Full House':fullHouse/n, 'Flush':flush/n, 'Straight':straight/n, 'Three Kind':threeKind/n, 'Two Pair':twoPair/n, 'Pair':pair/n, 'High':high/n}})
    print("RUNTIME (NEW): ", time.time() - startTime)
    return myDict

if __name__ == '__main__':
    for i in range(1):
        dict = handDistribution(SUIT, CARD, ['C6', 'DK'], [], 10000, {})
        print(dict)

    #processedCards = processCards(sampleDeck(generateDeck(SUIT, CARD, [], []), []))
    #while checkTwoPairOpt(processedCards) == False:
    #    processedCards = processCards(sampleDeck(generateDeck(SUIT, CARD, [], []), []))
    #print(processedCards)
    #checkTwoPairOpt(processedCards)
    #print()
