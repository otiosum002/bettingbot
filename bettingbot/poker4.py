import random
from enum import Enum, auto
from typing import List, Tuple, Dict
from dataclasses import dataclass

class Suit(Enum):
    HEARTS = auto()
    DIAMONDS = auto()
    CLUBS = auto()
    SPADES = auto()

class Card:
    def __init__(self, value: int, suit: Suit):
        if not 2 <= value <= 14:
            raise ValueError("Card value must be between 2 and 14 (14 = Ace)")
        self.value = value
        self.suit = suit
    
    def __str__(self):
        values = {11: 'J', 12: 'Q', 13: 'K', 14: 'A'}
        value_str = values.get(self.value, str(self.value))
        return f"{value_str}{self.suit.name[0]}"

    def __repr__(self):
        return self.__str__()

class HandRank(Enum):
    HIGH_CARD = 1
    PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10

@dataclass
class GameState:
    position: int  # 0 = button, 1 = small blind, 2 = big blind, etc.
    stack_size: float
    pot_size: float
    current_bet: float
    num_players: int
    hand: List[Card]
    credits_remaining: float = 10000
    all_in_strategy: bool = True
    initial_strategy_used: bool = False

class Action(Enum):
    FOLD = auto()
    CHECK = auto()
    CALL = auto()
    RAISE = auto()
    ALL_IN = auto()

class PokerBot:
    def __init__(self):
        self.hand_evaluator = HandEvaluator()
        self.opponent_tracker = OpponentTracker()
        self.initial_credits = 10000
        self.all_in_threshold = 6000

    def evaluate_hand(self, hand: List[Card]) -> Tuple[HandRank, List[Card]]:
        return self.hand_evaluator.evaluate(hand)

    def decide_action(self, game_state: GameState) -> Tuple[Action, float]:
        # Initial strategy: Use first 6000 credits for all-in
        if game_state.credits_remaining > (self.initial_credits - self.all_in_threshold) and not game_state.initial_strategy_used:
            if game_state.stack_size >= game_state.credits_remaining:
                return Action.ALL_IN, game_state.credits_remaining
            
        hand_rank, best_cards = self.evaluate_hand(game_state.hand)
        
        # Always raise with very strong hands
        if hand_rank in [HandRank.FOUR_OF_A_KIND, HandRank.STRAIGHT_FLUSH, HandRank.ROYAL_FLUSH]:
            if game_state.stack_size >= game_state.pot_size * 3:
                return Action.RAISE, game_state.pot_size * 3
            return Action.ALL_IN, game_state.stack_size

        # Calculate pot odds and expected value
        pot_odds = self._calculate_pot_odds(game_state)
        hand_strength = self._calculate_hand_strength(hand_rank)
        
        if hand_strength > 0.8:
            return Action.RAISE, min(game_state.pot_size * 2, game_state.stack_size)
        elif hand_strength > 0.6:
            if pot_odds > hand_strength:
                return Action.CALL, game_state.current_bet
            return Action.RAISE, min(game_state.pot_size, game_state.stack_size)
        elif hand_strength > 0.4:
            if pot_odds > hand_strength:
                return Action.CALL, game_state.current_bet
            return Action.FOLD, 0
        else:
            return Action.FOLD, 0

    def _calculate_pot_odds(self, game_state: GameState) -> float:
        if game_state.current_bet == 0:
            return 1.0
        return game_state.pot_size / (game_state.pot_size + game_state.current_bet)

    def _calculate_hand_strength(self, hand_rank: HandRank) -> float:
        strength_map = {
            HandRank.HIGH_CARD: 0.2,
            HandRank.PAIR: 0.4,
            HandRank.TWO_PAIR: 0.6,
            HandRank.THREE_OF_A_KIND: 0.7,
            HandRank.STRAIGHT: 0.8,
            HandRank.FLUSH: 0.85,
            HandRank.FULL_HOUSE: 0.9,
            HandRank.FOUR_OF_A_KIND: 0.95,
            HandRank.STRAIGHT_FLUSH: 0.98,
            HandRank.ROYAL_FLUSH: 1.0
        }
        return strength_map[hand_rank]

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

        # Check for Four of a Kind
        four_kind = self._get_n_of_a_kind(hand, 4)
        if four_kind:
            return HandRank.FOUR_OF_A_KIND, four_kind

        # Check for Full House
        full_house = self._get_full_house(hand)
        if full_house:
            return HandRank.FULL_HOUSE, full_house

        if flush_cards:
            return HandRank.FLUSH, flush_cards[:5]

        # Check for Straight
        straight = self._get_straight_cards(hand)
        if straight:
            return HandRank.STRAIGHT, straight

        # Check for Three of a Kind
        three_kind = self._get_n_of_a_kind(hand, 3)
        if three_kind:
            return HandRank.THREE_OF_A_KIND, three_kind

        # Check for Two Pair
        two_pair = self._get_two_pair(hand)
        if two_pair:
            return HandRank.TWO_PAIR, two_pair

        # Check for Pair
        pair = self._get_n_of_a_kind(hand, 2)
        if pair:
            return HandRank.PAIR, pair

        # High Card
        sorted_hand = sorted(hand, key=lambda card: card.value, reverse=True)
        return HandRank.HIGH_CARD, sorted_hand[:5]

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

    def _get_n_of_a_kind(self, hand: List[Card], n: int) -> List[Card]:
        value_groups = {}
        for card in hand:
            value_groups.setdefault(card.value, []).append(card)
        
        for value, cards in sorted(value_groups.items(), reverse=True):
            if len(cards) >= n:
                result = cards[:n]
                # Add high cards as kickers
                kickers = []
                for card in sorted(hand, key=lambda c: c.value, reverse=True):
                    if card.value != value and len(result) + len(kickers) < 5:
                        kickers.append(card)
                return result + kickers
        return []

    def _get_full_house(self, hand: List[Card]) -> List[Card]:
        three_kind = self._get_n_of_a_kind(hand, 3)
        if not three_kind:
            return []
        
        remaining_cards = [card for card in hand if card.value != three_kind[0].value]
        pair = self._get_n_of_a_kind(remaining_cards, 2)
        
        if pair:
            return three_kind[:3] + pair[:2]
        return []

    def _get_two_pair(self, hand: List[Card]) -> List[Card]:
        value_groups = {}
        for card in hand:
            value_groups.setdefault(card.value, []).append(card)
        
        pairs = []
        for value, cards in sorted(value_groups.items(), reverse=True):
            if len(cards) >= 2:
                pairs.extend(cards[:2])
                if len(pairs) >= 4:
                    # Add highest kicker
                    kickers = []
                    for card in sorted(hand, key=lambda c: c.value, reverse=True):
                        if card.value != pairs[0].value and card.value != pairs[2].value:
                            kickers.append(card)
                            break
                    return pairs[:4] + kickers
        return []

class OpponentTracker:
    def __init__(self):
        self.opponent_stats = {}

    def track_action(self, player_id: int, action: Action, bet_amount: float, game_state: GameState):
        if player_id not in self.opponent_stats:
            self.opponent_stats[player_id] = {
                'total_hands': 0,
                'aggression_factor': 0,
                'vpip': 0,
                'pfr': 0,
                'actions': []
            }
        
        stats = self.opponent_stats[player_id]
        stats['total_hands'] += 1
        stats['actions'].append((action, bet_amount, game_state))
        
        # Update aggression factor
        if action in [Action.RAISE, Action.ALL_IN]:
            stats['aggression_factor'] = (stats['aggression_factor'] * 
                (stats['total_hands'] - 1) + 1) / stats['total_hands']

def test_poker_bot():
    bot = PokerBot()
    
    # Test case 1: Royal Flush
    hand = [
        Card(14, Suit.HEARTS),  # Ace
        Card(13, Suit.HEARTS),  # King
        Card(12, Suit.HEARTS),  # Queen
        Card(11, Suit.HEARTS),  # Jack
        Card(10, Suit.HEARTS),  # 10
    ]
    
    game_state = GameState(
        position=0,
        stack_size=1000,
        pot_size=100,
        current_bet=20,
        num_players=6,
        hand=hand
    )
    
    action, amount = bot.decide_action(game_state)
    print(f"Test case 1 - Royal Flush:")
    print(f"Hand: {hand}")
    print(f"Action: {action}, Amount: {amount}\n")
    
    # Test case 2: Two Pair
    hand = [
        Card(14, Suit.HEARTS),  # Ace
        Card(14, Suit.DIAMONDS),  # Ace
        Card(10, Suit.HEARTS),  # 10
        Card(10, Suit.CLUBS),  # 10
        Card(2, Suit.SPADES),  # 2
    ]
    
    game_state = GameState(
        position=1,
        stack_size=500,
        pot_size=50,
        current_bet=10,
        num_players=6,
        hand=hand
    )
    
    action, amount = bot.decide_action(game_state)
    print(f"Test case 2 - Two Pair:")
    print(f"Hand: {hand}")
    print(f"Action: {action}, Amount: {amount}")

if __name__ == "__main__":
    test_poker_bot()