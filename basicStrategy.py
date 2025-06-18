from typing import Callable
from utils import convertStr2Deck

# This basic strategy is for 4-8 decks H17 (dealer hits soft-17), DAS (double after split), and early surrender.
# The functions are for each of the operations are coded in the order they need to be evaluated, from top to bottom.

Hand = list
Card = str
Deck = list
Shoe = list
PlayState = str

def surrender(hand:Hand, dealerUp:Card) -> bool:
    """Return true if I should surrender my hand."""
    if len(hand) > 2: return False
    if hand == ['8', '8'] and dealerUp == 'A': return True
    if hand == ['8', '8'] and dealerUp != 'A': return False
    dealerUp = convertFaceTens(dealerUp)
    myScore = getScore(hand)
    surrenderTable = {(17, 'A'),
                      (16, '9'),
                      (16, '10'),
                      (16, 'A'),
                      (15, '10'),
                      (15, 'A')}
    tableInput = (myScore, dealerUp)
    if tableInput in surrenderTable: return True
    else: return False

def convertFaceTens(card:Card) -> Card:
    """Convert jacks, queens, and kings to 10."""
    return '10' if card in {'J', 'Q', 'K'} else card

def getScore(hand:Hand) -> int:
    """Return the value of a hand of black jack."""
    handSorted = cardSorted(hand)
    score = 0
    for card in handSorted:
        cardVal = cardValue(card)
        if cardVal < 11: score += cardVal
        else:
            if score <= 10: score += cardVal
            else: score += 1
    return score

def cardSorted(hand:Hand) -> Hand:
    """Sort a hand of cards from low to high, ace is high."""
    return sorted(hand, key=cardValue)

def cardValue(card:Card) -> int:
    """Return the value of a card."""
    if card.isnumeric(): return int(card)
    elif card in {'J', 'Q', 'K'}: return 10
    else: return 11

def split(hand:Hand, dealerUp:Card) -> bool:
    """Return true if I should split my pair."""
    if len(hand) > 2: return False
    hand = [convertFaceTens(card) for card in hand]
    dealerUp = convertFaceTens(dealerUp)
    if hand[0] != hand[1]: return False
    card = hand[0]
    dealerIs8thruA = dealerUp in {'8', '9', '10', 'A'}
    dealerIs7thruA = dealerIs8thruA or dealerUp == '7'
    if card == 'A': return True
    if card == '10': return False
    if card == '9': return False if dealerUp in {'7', '10', 'A'} else True
    if card == '8': return True
    if card == '7' and dealerIs8thruA: return False
    if card == '6' and dealerIs7thruA: return False
    if card == '5': return False
    if card == '4' and (dealerIs7thruA or dealerUp in {'2', '3', '4'}): return False
    if (card == '3' or card == '2') and dealerIs8thruA: return False
    return True

def softDouble(hand:Hand, dealerUp:Card) -> bool:
    """Return true if I should double down on a soft hand."""
    if len(hand) > 2: return False
    if not isSoft(hand): return False
    dealerUp = convertFaceTens(dealerUp)
    ix = 0 if hand[1] == 'A' else 1
    card = hand[ix]
    if card == '8' and dealerUp == '6': return True
    if card == '7' and dealerUp in {'2', '3', '4', '5', '6'}: return True
    if card == '6' and dealerUp in {'3', '4', '5', '6'}: return True
    if (card == '5' or card == '4') and dealerUp in {'4', '5', '6'}: return True
    if (card == '3' or card == '2') and dealerUp in {'5', '6'}: return True
    return False

def isSoft(hand:Hand) -> bool:
    """Determine if a hand is soft or not. A hand is soft when it has an ace and the hand does not total to 21."""
    return any([card == 'A' for card in hand]) and getScore(hand) < 21

def hardDouble(hand:Hand, dealerUp:Card) -> bool:
    """Return true if the hand should double down on a hard hand."""
    if len(hand) > 2: return False
    score = getScore(hand)
    if (score > 11 or score < 8): return False
    if score == 11: return True
    if score == 8: return False
    dealerUp = convertFaceTens(dealerUp)
    hardDoubleTable = {(10, '10'),
                       (10, 'A'),
                       (9, '2'),
                       (9, '7'),
                       (9, '8'),
                       (9, '9'),
                       (9, '10'),
                       (9, 'A')}
    if (score, dealerUp) in hardDoubleTable: return False
    return True

def softHit(hand:Hand, dealerUp:Card) -> bool:
    """Return true if the hand should hit as a soft hand."""
    if not isSoft(hand): return False
    dealerUp = convertFaceTens(dealerUp)
    if len(hand) > 2:
        ix = hand.index('A')
        card = getScore(hand[:ix] + hand[ix+1:])
    else:
        ix = 0 if hand[1] == 'A' else 1
        card = hand[ix]
    if card == '7' and dealerUp in {'9', '10', 'A'}: return True
    if card == '6': return True
    return False

def hardHit(hand:Hand, dealerUp:Card) -> bool:
    """Return true if the hand should hit when it is hard."""
    dealerUp = convertFaceTens(dealerUp)
    score = getScore(hand)
    if score == 17: return False
    if (12 <= score <= 16) and dealerUp in {'7', '8', '9', '10', 'A'}: return True
    if score == 12 and dealerUp in {'2', '3'}: return True
    if score < 12: return True
    return False

def basicStrategy(hand:Hand, dealerUp:Card, allowSplit:bool=True) -> PlayState:
    """Given a hand of blackjack and a dealer's face up card, return a `PlayState` for optimal game play.
    `PlayState` can be SURRENDER, SPLIT, DOUBLE, HIT, or STAND."""
    if surrender(hand, dealerUp): return 'SURRENDER'
    if allowSplit:
        if split(hand, dealerUp): return 'SPLIT'
    if softDouble(hand, dealerUp): return 'DOUBLE'
    if hardDouble(hand, dealerUp): return 'DOUBLE'
    if softHit(hand, dealerUp): return 'HIT'
    if hardHit(hand, dealerUp): return 'HIT'
    return 'STAND'

def testMultipleDealerUps(function:Callable, hand:Hand, dealerUps:Deck, negateFunction:bool=False) -> bool:
    """Run tests on multple dealer up cards for the `function`."""
    for card in dealerUps:
        if negateFunction:
            assert not function(hand, card), f"hand {hand} and dealerUp {card} failed on megation of {function.__name__}"
        else:
            assert function(hand, card), f"hand {hand} and dealerUp {card} failed on function {function.__name__}"
    return True

def tests():
    """Unit tests."""
    print('Running unit tests for basicStrategy.py...')
    assert cardValue('A') == 11
    assert cardValue('K') == 10
    assert cardValue('Q') == 10
    assert cardValue('J') == 10
    assert cardValue('10') == 10
    assert cardValue('2') == 2
    assert cardSorted(['A', '3', 'K']) == ['3', 'K', 'A']
    assert getScore(['A', 'Q']) == 21
    assert getScore(['A', '3']) == 14
    assert getScore(['9', 'J', 'A']) == 20
    assert getScore(['8', '8']) == 16
    assert getScore(['A', 'A']) == 12
    assert convertFaceTens('J') == '10'
    assert convertFaceTens('2') == '2'
    assert convertFaceTens('A') == 'A'
    assert convertFaceTens('Q') == '10'
    assert convertFaceTens('K') == '10'
    assert surrender(['8', '8'], 'A')
    assert surrender(['10', '5'], 'J')
    assert surrender(['K', '6'], '9')
    assert surrender(['Q', '7'], 'A')
    assert surrender(['A', '5'], 'A')
    assert surrender(['Q', '6'], 'J')
    assert surrender(['A', '4'], 'A')
    assert not surrender(['10', '4'], 'A')
    assert not surrender(['K', '4'], '10')
    assert not surrender(['8', '8'], 'J')
    assert not surrender(['8', '8'], '3')
    assert not surrender(['K', '7'], 'Q')
    assert not surrender (['10', '5'], '9')
    assert not surrender(['A', '4', '2'], 'A')
    assert split(['A', 'A'], 'A')
    assert split(['9', '9'], '9')
    assert not split(['A', '2'], '3')
    assert split(['8', '8'], '10')
    assert not split(['9', '9'], '7')
    assert not split(['9', '9'], '10')
    assert not split(['9', '9'], 'A')
    assert split(['9', '9'], '6')
    assert not split(['7', '7'], '8')
    assert not split(['A', 'A', '3'], 'A')
    assert testMultipleDealerUps(split, ['7', '7'], ['9', '10', 'J', 'Q', 'K', 'A'], negateFunction=True)
    assert testMultipleDealerUps(split, ['6', '6'], ['2', '3', '4', '5', '6'])
    assert testMultipleDealerUps(split, ['6', '6'], ['7', '8', '9', '10', 'J', 'Q', 'K', 'A'], negateFunction=True)
    deck = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    assert testMultipleDealerUps(split, ['K', 'K'], deck, negateFunction=True)
    assert testMultipleDealerUps(split, ['5', '5'], deck, negateFunction=True)
    assert testMultipleDealerUps(split, ['4', '4'], ['2', '3', '4'], negateFunction=True)
    assert testMultipleDealerUps(split, ['4', '4'], ['5', '6'])
    assert testMultipleDealerUps(split, ['4', '4'], ['7', '8', '9', '10', 'J', 'Q', 'K', 'A'], negateFunction=True)
    deck = ['2', '3', '4', '5', '6', '7']
    assert testMultipleDealerUps(split, ['3', '3'], deck)
    assert testMultipleDealerUps(split, ['2', '2'], deck)
    assert testMultipleDealerUps(split, ['3', '3'], ['8', '9', '10', 'J', 'Q', 'K', 'A'], negateFunction=True)
    assert testMultipleDealerUps(split, ['2', '2'], ['8', '9', '10', 'J', 'Q', 'K', 'A'], negateFunction=True)
    assert isSoft(['A', '9'])
    assert not isSoft(['J', 'A'])
    assert isSoft(['8', 'A'])
    assert isSoft(['3', 'A', '2'])
    assert testMultipleDealerUps(softDouble, ['A', '8'], ['2', '3', '4', '5', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'], negateFunction=True)
    assert softDouble(['A', '8'], '6')
    assert not softDouble(['A', '8', 'A'], '6')
    assert testMultipleDealerUps(softDouble, ['A', '7'], ['2', '3', '4', '5', '6'])
    assert testMultipleDealerUps(softDouble, ['A', '7'], convertStr2Deck('7 8 9 10 J Q K A'), negateFunction=True)
    assert not softDouble(['A', '6'], '2')
    assert testMultipleDealerUps(softDouble, ['A', '6'], convertStr2Deck('3 4 5 6'))
    assert testMultipleDealerUps(softDouble, ['A', '6'], convertStr2Deck('7 8 9 10 J Q K A'), negateFunction=True)
    assert testMultipleDealerUps(softDouble, ['A', '5'], convertStr2Deck('2 3'), negateFunction=True)
    assert testMultipleDealerUps(softDouble, ['A', '5'], convertStr2Deck('4 5 6'))
    assert testMultipleDealerUps(softDouble, ['A', '5'], convertStr2Deck('7 8 9 10 J Q K A'), negateFunction=True)
    assert testMultipleDealerUps(softDouble, ['A', '4'], convertStr2Deck('2 3'), negateFunction=True)
    assert testMultipleDealerUps(softDouble, ['A', '4'], convertStr2Deck('4 5 6'))
    assert testMultipleDealerUps(softDouble, ['A', '4'], convertStr2Deck('7 8 9 10 J Q K A'), negateFunction=True)
    assert testMultipleDealerUps(softDouble, ['A', '3'], convertStr2Deck('2 3 4'), negateFunction=True)
    assert testMultipleDealerUps(softDouble, ['A', '3'], convertStr2Deck('5 6'))
    assert testMultipleDealerUps(softDouble, ['A', '3'], convertStr2Deck('7 8 9 10 J Q K A'), negateFunction=True)
    assert testMultipleDealerUps(softDouble, ['A', '2'], convertStr2Deck('2 3 4'), negateFunction=True)
    assert testMultipleDealerUps(softDouble, ['A', '2'], convertStr2Deck('5 6'))
    assert testMultipleDealerUps(softDouble, ['A', '2'], convertStr2Deck('7 8 9 10 J Q K A'), negateFunction=True)
    assert testMultipleDealerUps(softDouble, ['A', '9'], convertStr2Deck('2 3 4 5 6 7 8 9 10 J Q K A'), negateFunction=True)
    assert testMultipleDealerUps(hardDouble, ['7', '4'], convertStr2Deck('2 3 4 5 6 7 8 9 10 J Q K A'))
    assert testMultipleDealerUps(hardDouble, ['K', '2'], convertStr2Deck('2 3 4 5 6 7 8 9 10 J Q K A'), negateFunction=True)
    assert testMultipleDealerUps(hardDouble, ['5', '3'], convertStr2Deck('2 3 4 5 6 7 8 9 10 J Q K A'), negateFunction=True)
    assert testMultipleDealerUps(hardDouble, ['4', '6'], convertStr2Deck('2 3 4 5 6 7 8 9'))
    assert testMultipleDealerUps(hardDouble, ['3', '7'], convertStr2Deck('10 J Q K A'), negateFunction=True)
    assert not hardDouble(['5', '4'], '2')
    assert testMultipleDealerUps(hardDouble, ['2', '7'], convertStr2Deck('3 4 5 6'))
    assert not hardDouble(['2', '7', '2'], '3')
    assert testMultipleDealerUps(hardDouble, ['6', '3'], convertStr2Deck('7 8 9 10 J Q K A'), negateFunction=True)
    assert testMultipleDealerUps(softHit, ['A', '9'], convertStr2Deck('2 3 4 5 6 7 8 9 10 J Q K A'), negateFunction=True)
    assert testMultipleDealerUps(softHit, ['A', '8'], convertStr2Deck('2 3 4 5 6 7 8 9 10 J Q K A'), negateFunction=True)
    assert testMultipleDealerUps(softHit, ['A', '7'], convertStr2Deck('2 3 4 5 6 7 8'), negateFunction=True)
    assert testMultipleDealerUps(softHit, ['A', '7'], convertStr2Deck('9 10 J Q K A'))
    assert not softHit(['A', '7', '2'], '9')
    assert testMultipleDealerUps(softHit, ['A', '6'], convertStr2Deck('2 3 4 5 6 7 8 9 10 J Q K A'))
    assert testMultipleDealerUps(softHit, ['A', '5'], convertStr2Deck('2 3 4 5 6 7 8 9 10 J Q K A'), negateFunction=True)
    assert testMultipleDealerUps(hardHit, ['K', '7'], convertStr2Deck('2 3 4 5 6 7 8 9 10 J Q K A'), negateFunction=True)
    assert testMultipleDealerUps(hardHit, ['J', '6'], convertStr2Deck('2 3 4 5 6'), negateFunction=True)
    assert testMultipleDealerUps(hardHit, ['Q', '6'], convertStr2Deck('7 8 9 10 J Q K A'))
    assert testMultipleDealerUps(hardHit, ['J', '5'], convertStr2Deck('2 3 4 5 6'), negateFunction=True)
    assert testMultipleDealerUps(hardHit, ['Q', '5'], convertStr2Deck('7 8 9 10 J Q K A'))
    assert testMultipleDealerUps(hardHit, ['J', '4'], convertStr2Deck('2 3 4 5 6'), negateFunction=True)
    assert testMultipleDealerUps(hardHit, ['Q', '4'], convertStr2Deck('7 8 9 10 J Q K A'))
    assert testMultipleDealerUps(hardHit, ['J', '3'], convertStr2Deck('2 3 4 5 6'), negateFunction=True)
    assert testMultipleDealerUps(hardHit, ['Q', '3'], convertStr2Deck('7 8 9 10 J Q K A'))
    assert testMultipleDealerUps(hardHit, ['K', '2'], convertStr2Deck('2 3'))
    assert testMultipleDealerUps(hardHit, ['J', '2'], convertStr2Deck('4 5 6'), negateFunction=True)
    assert testMultipleDealerUps(hardHit, ['Q', '2'], convertStr2Deck('7 8 9 10 J Q K A'))
    assert hardHit(['3', '8', '4'], '7')
    assert testMultipleDealerUps(hardHit, ['4', '4'], convertStr2Deck('2 3 4 5 6 7 8 9 10 J Q K A'))
    print('All tests passed!')

if __name__ == "__main__":
    tests()