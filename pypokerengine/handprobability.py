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

if __name__ == '__main__':
    deck = generateDeck(SUIT, CARD, ['C4', 'D2'], [])
    
    count = 0
    totalFlush = 0
    while totalFlush < 11:
        count += 1
        sample = processCards(sampleDeck(deck, []))
        if checkFullHouse(sample) is True:
            totalFlush += 1
            print(sample)
    print(count)
