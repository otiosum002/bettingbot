# File: hand_evaluator.py
from typing import List, Tuple
from models import Card
from enums import HandRank

class HandEvaluator:
    def evaluate(self, hand: List[Card]) -> Tuple[HandRank, List[Card]]:
        if len(hand) < 5:
            raise ValueError("Need at least 5 cards to evaluate a poker hand")

        # Check for Royal Flush and Straight Flush
        flush_cards = self._get_flush_cards(hand)
        if flush_cards:
            straight_flush_cards = self._get_straight_cards(flush_cards)
            if straight_flush_cards:
                if straight_flush_cards[0].value == 14:  # Ace-high
                    return HandRank.ROYAL_FLUSH, straight_flush_cards
                return HandRank.STRAIGHT_FLUSH, straight_flush_cards

        # [Rest of the evaluate method implementation...]
        # Note: For brevity, I've omitted the rest of the evaluate method
        # Copy the full implementation from the original code

    def _get_flush_cards(self, hand: List[Card]) -> List[Card]:
        suits = {}
        for card in hand:
            suits.setdefault(card.suit, []).append(card)
        for suit_cards in suits.values():
            if len(suit_cards) >= 5:
                return sorted(suit_cards, key=lambda card: card.value, reverse=True)[:5]
        return []

    def _get_straight_cards(self, hand: List[Card]) -> List[Card]:
        values = sorted(set(card.value for card in hand), reverse=True)
        for i in range(len(values) - 4):
            if values[i] - values[i + 4] == 4:
                straight_cards = []
                for value in range(values[i], values[i] - 5, -1):
                    for card in hand:
                        if card.value == value:
                            straight_cards.append(card)
                            break
                return straight_cards
        return []

    # [Include other helper methods from the original HandEvaluator class...]