from treys import Card as TreysCard, Evaluator

def card_to_str(card):
    return f"{card.rank}{card.suit[0].lower()}"

def evaluate_hand(hand, community_cards):
    """
    Evaluates hand strength using Treys. Lower score = stronger hand.
    """
    treys_hand = [TreysCard.new(card_to_str(c)) for c in hand]
    treys_board = [TreysCard.new(card_to_str(c)) for c in community_cards]
    evaluator = Evaluator()
    score = evaluator.evaluate(treys_board, treys_hand)
    return score