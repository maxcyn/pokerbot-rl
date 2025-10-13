from treys import Card as TreysCard, Evaluator

# Rank map for pre-flop evaluation
RANK_MAP = {r: i for i, r in enumerate('23456789TJQKA')}

def get_preflop_strength(hand):
    """
    Calculates a normalized pre-flop hand strength from 0.0 (worst) to 1.0 (best).
    This is based on a simplified version of the Chen Formula.
    """
    card1, card2 = hand[0], hand[1]
    rank1, rank2 = RANK_MAP[card1.rank], RANK_MAP[card2.rank]
    
    # 1. Score the high card
    high_card_rank = max(rank1, rank2)
    score = 0
    if high_card_rank == RANK_MAP['A']: score = 10
    elif high_card_rank == RANK_MAP['K']: score = 8
    elif high_card_rank == RANK_MAP['Q']: score = 7
    elif high_card_rank == RANK_MAP['J']: score = 6
    else: score = (high_card_rank + 2) / 2.0

    # 2. Multiply for pairs
    if rank1 == rank2:
        score *= 2
        if score < 5: score = 5 # Minimum score for 22-44 is 5

    # 3. Add bonus for suitedness
    if card1.suit == card2.suit:
        score += 2
    
    # 4. Subtract penalty for gaps
    gap = abs(rank1 - rank2) - 1
    if gap == 1: score -= 1
    elif gap == 2: score -= 2
    elif gap == 3: score -= 4
    elif gap > 3: score -= 5

    # 5. Add bonus for connectors and 1-gappers with low high cards
    if gap <= 1 and high_card_rank < RANK_MAP['Q']:
        score += 1
    
    # Normalize score to be between 0 and 1
    final_score = max(0, score)
    # Max possible score is 20 (for AA), min is ~0.
    return min(1.0, final_score / 20.0)

def card_to_str(card):
    return f"{card.rank}{card.suit[0].lower()}"

def evaluate_hand(hand, community_cards):
    """
    Evaluates hand strength using Treys (for post-flop only). Lower score = stronger hand.
    """
    # This function should now only be called when there are community cards.
    if not community_cards or len(hand) + len(community_cards) < 5:
        # This is a fallback. The calling function should handle the pre-flop case.
        return 7462 

    treys_hand = [TreysCard.new(card_to_str(c)) for c in hand]
    treys_board = [TreysCard.new(card_to_str(c)) for c in community_cards]
    evaluator = Evaluator()
    score = evaluator.evaluate(treys_board, treys_hand)
    return score