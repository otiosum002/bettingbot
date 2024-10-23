import random
from enum import Enum, auto
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from collections import deque
import statistics

class Suit(Enum):
    HEARTS = auto()
    DIAMONDS = auto()
    CLUBS = auto()
    SPADES = auto()

# [Previous Card, HandRank, and base Action classes remain the same...]

@dataclass
class PlayerProfile:
    vpip: float = 0  # Voluntarily Put Money In Pot
    pfr: float = 0   # Pre-Flop Raise
    af: float = 0    # Aggression Factor
    total_hands: int = 0
    three_bet_freq: float = 0
    fold_to_three_bet: float = 0
    avg_bet_size: float = 0
    position_stats: Dict[int, Dict] = None
    
    def __post_init__(self):
        if self.position_stats is None:
            self.position_stats = {i: {'vpip': 0, 'pfr': 0, 'hands': 0} for i in range(9)}

@dataclass
class GameState:
    position: int
    stack_size: float
    pot_size: float
    current_bet: float
    num_players: int
    hand: List[Card]
    credits_remaining: float = 10000
    all_in_strategy: bool = True
    initial_strategy_used: bool = False
    street: str = 'preflop'  # preflop, flop, turn, river
    community_cards: List[Card] = None
    active_players: int = None
    position_relative_to_button: int = None
    last_action: Optional[Tuple[Action, float]] = None
    round_history: List[Tuple[int, Action, float]] = None

    def __post_init__(self):
        if self.community_cards is None:
            self.community_cards = []
        if self.active_players is None:
            self.active_players = self.num_players
        if self.round_history is None:
            self.round_history = []

class AdvancedPokerBot:
    def __init__(self):
        self.hand_evaluator = HandEvaluator()
        self.opponent_tracker = EnhancedOpponentTracker()
        self.initial_credits = 10000
        self.all_in_threshold = 6000
        self.min_hands_for_stats = 20
        self.strategy_adjustor = StrategyAdjustor()
        self.hand_history = deque(maxlen=1000)
        
    def decide_action(self, game_state: GameState) -> Tuple[Action, float]:
        # Get basic hand strength
        hand_strength = self._calculate_hand_strength(game_state)
        
        # Get position-based adjustment
        position_multiplier = self._get_position_multiplier(game_state.position)
        
        # Get opponent-based adjustment
        opponent_adjustment = self._get_opponent_adjustment(game_state)
        
        # Combine all factors
        final_strength = hand_strength * position_multiplier * opponent_adjustment
        
        # Get recommended action based on street
        if game_state.street == 'preflop':
            return self._handle_preflop(game_state, final_strength)
        else:
            return self._handle_postflop(game_state, final_strength)

    def _handle_preflop(self, game_state: GameState, strength: float) -> Tuple[Action, float]:
        # Implementation of preflop ranges based on position
        position_ranges = {
            0: 0.2,  # Button
            1: 0.3,  # Small Blind
            2: 0.25, # Big Blind
            3: 0.4,  # UTG
            4: 0.35, # UTG+1
            5: 0.3,  # MP
            6: 0.25, # MP+1
            7: 0.2,  # CO
        }
        
        min_strength = position_ranges.get(game_state.position, 0.3)
        
        if strength < min_strength:
            return Action.FOLD, 0
            
        # Calculate raise size based on stack depth and position
        stack_to_pot_ratio = game_state.stack_size / game_state.pot_size
        
        if stack_to_pot_ratio < 5:  # Short stack
            if strength > 0.8:
                return Action.ALL_IN, game_state.stack_size
            elif strength > 0.6:
                return Action.RAISE, game_state.pot_size * 2.5
                
        elif stack_to_pot_ratio < 15:  # Medium stack
            if strength > 0.7:
                return Action.RAISE, game_state.pot_size * 3
            elif strength > 0.5:
                return Action.CALL, game_state.current_bet
                
        else:  # Deep stack
            if strength > 0.6:
                return Action.RAISE, game_state.pot_size * 3.5
            elif strength > 0.4:
                return Action.CALL, game_state.current_bet
                
        return Action.FOLD, 0

    def _handle_postflop(self, game_state: GameState, strength: float) -> Tuple[Action, float]:
        pot_odds = self._calculate_pot_odds(game_state)
        implied_odds = self._calculate_implied_odds(game_state)
        
        # Calculate betting line based on previous action
        if not game_state.round_history:
            return self._lead_betting(game_state, strength)
            
        last_action = game_state.round_history[-1]
        if last_action[1] in [Action.RAISE, Action.ALL_IN]:
            return self._handle_aggression(game_state, strength, last_action)
            
        return self._continue_betting(game_state, strength)

    def _lead_betting(self, game_state: GameState, strength: float) -> Tuple[Action, float]:
        if strength > 0.8:
            bet_size = self._calculate_value_bet(game_state)
            return Action.RAISE, bet_size
        elif strength > 0.6:
            return Action.RAISE, game_state.pot_size * 0.6
        elif strength > 0.4:
            return Action.CHECK, 0
        else:
            return Action.CHECK, 0

    def _handle_aggression(self, game_state: GameState, strength: float, last_action: Tuple) -> Tuple[Action, float]:
        required_call = last_action[2] - game_state.current_bet
        pot_odds = required_call / (game_state.pot_size + required_call)
        
        if strength > 0.9:
            return Action.RAISE, game_state.pot_size * 3
        elif strength > pot_odds + 0.1:
            return Action.CALL, required_call
        else:
            return Action.FOLD, 0

    def _calculate_value_bet(self, game_state: GameState) -> float:
        stack_to_pot = game_state.stack_size / game_state.pot_size
        if stack_to_pot > 20:  # Deep
            return game_state.pot_size * 0.75
        elif stack_to_pot > 10:  # Medium
            return game_state.pot_size * 0.66
        else:  # Short
            return game_state.pot_size * 0.5

    def _get_position_multiplier(self, position: int) -> float:
        position_multipliers = {
            0: 1.2,  # Button
            1: 0.9,  # Small Blind
            2: 0.8,  # Big Blind
            3: 0.85, # UTG
            4: 0.9,  # UTG+1
            5: 0.95, # MP
            6: 1.0,  # MP+1
            7: 1.1,  # CO
        }
        return position_multipliers.get(position, 1.0)

    def _get_opponent_adjustment(self, game_state: GameState) -> float:
        # Get stats for all active opponents
        opponent_stats = [self.opponent_tracker.get_stats(i) for i in range(game_state.num_players)
                         if i != game_state.position]
        
        # Calculate adjustment based on opponent tendencies
        adjustments = []
        for stats in opponent_stats:
            if stats.total_hands >= self.min_hands_for_stats:
                if stats.vpip > 0.4:  # Loose player
                    adjustments.append(1.2)
                elif stats.vpip < 0.15:  # Tight player
                    adjustments.append(0.8)
                if stats.af > 2.0:  # Aggressive player
                    adjustments.append(0.9)
                elif stats.af < 0.5:  # Passive player
                    adjustments.append(1.1)
                    
        return statistics.mean(adjustments) if adjustments else 1.0

class EnhancedOpponentTracker:
    def __init__(self):
        self.player_profiles = {}
        self.session_stats = {}
        self.hand_history = deque(maxlen=1000)
        
    def track_action(self, player_id: int, action: Action, bet_amount: float, game_state: GameState):
        if player_id not in self.player_profiles:
            self.player_profiles[player_id] = PlayerProfile()
            
        profile = self.player_profiles[player_id]
        profile.total_hands += 1
        
        # Update VPIP
        if action in [Action.CALL, Action.RAISE, Action.ALL_IN] and game_state.street == 'preflop':
            profile.vpip = ((profile.vpip * (profile.total_hands - 1)) + 1) / profile.total_hands
            
        # Update PFR
        if action in [Action.RAISE, Action.ALL_IN] and game_state.street == 'preflop':
            profile.pfr = ((profile.pfr * (profile.total_hands - 1)) + 1) / profile.total_hands
            
        # Update AF
        if action in [Action.RAISE, Action.ALL_IN]:
            profile.af = ((profile.af * (profile.total_hands - 1)) + 2) / profile.total_hands
        elif action == Action.CALL:
            profile.af = ((profile.af * (profile.total_hands - 1)) + 1) / profile.total_hands
            
        # Update position stats
        pos_stats = profile.position_stats[game_state.position]
        pos_stats['hands'] += 1
        if action in [Action.CALL, Action.RAISE, Action.ALL_IN]:
            pos_stats['vpip'] = ((pos_stats['vpip'] * (pos_stats['hands'] - 1)) + 1) / pos_stats['hands']
        if action in [Action.RAISE, Action.ALL_IN]:
            pos_stats['pfr'] = ((pos_stats['pfr'] * (pos_stats['hands'] - 1)) + 1) / pos_stats['hands']
            
        # Track bet sizing
        if action in [Action.RAISE, Action.ALL_IN]:
            profile.avg_bet_size = ((profile.avg_bet_size * (profile.total_hands - 1)) + 
                                  (bet_amount / game_state.pot_size)) / profile.total_hands
            
        # Store hand history
        self.hand_history.append((player_id, action, bet_amount, game_state))

    def get_stats(self, player_id: int) -> PlayerProfile:
        return self.player_profiles.get(player_id, PlayerProfile())

    def get_tendencies(self, player_id: int) -> Dict:
        profile = self.get_stats(player_id)
        return {
            'aggression': 'high' if profile.af > 2.0 else 'low' if profile.af < 0.5 else 'medium',
            'looseness': 'loose' if profile.vpip > 0.4 else 'tight' if profile.vpip < 0.15 else 'medium',
            'raising': 'aggressive' if profile.pfr/profile.vpip > 0.7 else 'passive',
            'bet_sizing': 'large' if profile.avg_bet_size > 0.75 else 'small' if profile.avg_bet_size < 0.4 else 'medium'
        }

def run_comprehensive_tests():
    bot = AdvancedPokerBot()
    
    # Test case 1: Premium hand in late position
    hand1 = [
        Card(14, Suit.HEARTS),  # Ace
        Card(14, Suit.SPADES),  # Ace
    ]
    
    game_state1 = GameState(
        position=0,  # Button
        stack_size=1000,
        pot_size=100,
        current_bet=20,
        num_players=6,
        hand=hand1,
        street='preflop'
    )
    
    # Test case 2: Marginal hand in early position
    hand2 = [
        Card(10, Suit.HEARTS),  # Ten
        Card(10, Suit.DIAMONDS),  # Ten
    ]
    
    game_state2 = GameState(
        position=3,  # UTG
        stack_size=1000,
        pot_size=100,
        current_bet=20,
        num_players=6,
        hand=hand2,
        street='preflop'
    )
    
    # Test case 3: Drawing hand on flop
    hand3 = [
        Card(11, Suit.HEARTS),  # Jack
        Card(10, Suit.HEARTS),  # Ten
    ]
    
    community_cards3 = [
        Card(9, Suit.HEARTS),
        Card(2, Suit.DIAMONDS),
        Card(7, Suit.CLUBS)
    ]
    
    game_state3 = GameState(
        position=0,
        stack_size=1000,
        pot_size=300,
        current_bet=0,
        num_players=4,
        hand=hand3,
        street='flop',
        community_cards=community_cards3
    )
    
    # Test case 4: Monster hand vs aggressive opponent
    hand4 = [
        Card(14, Suit.HEARTS),  # Ace
        Card(14, Suit.DIAMONDS),  # Ace
    ]
    
    community_cards4 = [
        Card(14, Suit.CLUBS),
        Card(2, Suit.DIAMONDS),
        Card(7, Suit.CLUBS)
    ]
    
    game_state4 = GameState(
        position=2,
        stack_size=1000,
        pot_size=500,
        current_bet=200,
        num_players=3,
        hand=hand4,
        street='flop',
        community_cards=community_cards4
    )
    
    # Run tests and print results
    test_cases = [
        ("Premium hand on button", game_state1),
        ("Marginal hand UTG", game_state2),
        ("Drawing hand on flop", game_state3),
        ("Monster hand vs aggression", game_state4)
    ]
    
    for test_name, game_state in test_cases:
        action, amount = bot.decide_action(game_state)
        print(f"\nTest: {test_name}")
        print(f"Hand: {game_state.hand}")
        if game_state.community_cards:
            print(f"Community cards: {game_state.community_cards}")
        print(f"Position: {game_state.position}")
        print(f"Action: {action}, Amount: {amount}")
        print(f"Pot size: {game_state.pot_size}, Current bet: {game_state.current_bet}")



class StrategyAdjustor:
    """Adjusts strategy based on tournament stage, stack sizes, and table dynamics"""
    
    def __init__(self):
        self.strategy_weights = {
            'early_tournament': {
                'aggression': 0.7,
                'bluff_frequency': 0.2,
                'call_threshold': 0.6
            },
            'middle_tournament': {
                'aggression': 0.9,
                'bluff_frequency': 0.3,
                'call_threshold': 0.5
            },
            'bubble': {
                'aggression': 1.2,
                'bluff_frequency': 0.4,
                'call_threshold': 0.4
            },
            'final_table': {
                'aggression': 1.1,
                'bluff_frequency': 0.35,
                'call_threshold': 0.45
            }
        }
    
    def get_tournament_stage_adjustments(self, stack_size: float, avg_stack: float, 
                                       players_remaining: int, total_players: int) -> Dict[str, float]:
        """Calculate adjustments based on tournament stage"""
        stage = self._determine_tournament_stage(players_remaining, total_players)
        stack_ratio = stack_size / avg_stack
        
        adjustments = self.strategy_weights[stage].copy()
        
        # Adjust based on stack size
        if stack_ratio < 0.5:  # Short stack
            adjustments['aggression'] *= 1.3
            adjustments['bluff_frequency'] *= 0.7
        elif stack_ratio > 2.0:  # Big stack
            adjustments['aggression'] *= 0.9
            adjustments['bluff_frequency'] *= 1.2
            
        return adjustments
    
    def _determine_tournament_stage(self, players_remaining: int, total_players: int) -> str:
        """Determine current tournament stage"""
        ratio = players_remaining / total_players
        
        if ratio > 0.7:
            return 'early_tournament'
        elif ratio > 0.3:
            return 'middle_tournament'
        elif ratio > 0.15:
            return 'bubble'
        else:
            return 'final_table'
    
    def adjust_for_icm(self, game_state: GameState, tournament_info: Dict) -> float:
        """Adjust decisions based on ICM considerations"""
        if not tournament_info.get('is_tournament', False):
            return 1.0
            
        stack_ratio = game_state.stack_size / tournament_info.get('avg_stack', game_state.stack_size)
        position_in_money = tournament_info.get('position_in_money', 1.0)
        
        # Basic ICM pressure calculation
        icm_pressure = 1.0
        
        if position_in_money < 1.0:  # Not yet in the money
            if stack_ratio < 0.5:  # Short stack
                icm_pressure = 0.7  # More willing to gamble
            elif stack_ratio > 2.0:  # Big stack
                icm_pressure = 1.3  # More conservative
        else:  # In the money
            if stack_ratio < 0.5:
                icm_pressure = 0.8
            elif stack_ratio > 2.0:
                icm_pressure = 1.2
                
        return icm_pressure

class HandStrengthCalculator:
    """Advanced hand strength calculator considering more factors"""
    
    def __init__(self):
        self.hand_evaluator = HandEvaluator()
        
    def calculate_full_strength(self, game_state: GameState) -> float:
        """Calculate complete hand strength including drawing potential"""
        if not game_state.community_cards:  # Preflop
            return self._calculate_preflop_strength(game_state.hand)
            
        current_strength = self._calculate_made_hand_strength(game_state)
        drawing_strength = self._calculate_drawing_strength(game_state)
        
        # Combine made hand and drawing strength
        return max(current_strength, current_strength * 0.7 + drawing_strength * 0.3)
    
    def _calculate_preflop_strength(self, hand: List[Card]) -> float:
        """Calculate preflop hand strength"""
        if len(hand) != 2:
            raise ValueError("Preflop hand must contain exactly 2 cards")
            
        # Sort hand by value
        sorted_hand = sorted(hand, key=lambda x: x.value, reverse=True)
        
        # Check for pairs
        if sorted_hand[0].value == sorted_hand[1].value:
            # Scale pair strength from 0.5 (pair of 2s) to 1.0 (pair of Aces)
            return 0.5 + (sorted_hand[0].value - 2) / 24
            
        # Check for suited cards
        suited = sorted_hand[0].suit == sorted_hand[1].suit
        
        # Calculate gap between cards
        gap = sorted_hand[0].value - sorted_hand[1].value - 1
        
        # Base strength on high card
        strength = 0.3 + (sorted_hand[0].value - 2) / 24
        
        # Adjust for suitedness
        if suited:
            strength += 0.1
            
        # Adjust for connectedness
        if gap == 0:  # Consecutive cards
            strength += 0.1
        elif gap == 1:  # One gap
            strength += 0.05
            
        # Adjust for high cards
        if sorted_hand[1].value >= 10:
            strength += 0.1
            
        return min(1.0, strength)
    
    def _calculate_made_hand_strength(self, game_state: GameState) -> float:
        """Calculate current hand strength"""
        all_cards = game_state.hand + game_state.community_cards
        hand_rank, best_cards = self.hand_evaluator.evaluate(all_cards)
        
        # Base strength on hand rank
        base_strength = {
            HandRank.HIGH_CARD: 0.1,
            HandRank.PAIR: 0.2,
            HandRank.TWO_PAIR: 0.4,
            HandRank.THREE_OF_A_KIND: 0.6,
            HandRank.STRAIGHT: 0.7,
            HandRank.FLUSH: 0.8,
            HandRank.FULL_HOUSE: 0.9,
            HandRank.FOUR_OF_A_KIND: 0.95,
            HandRank.STRAIGHT_FLUSH: 0.98,
            HandRank.ROYAL_FLUSH: 1.0
        }[hand_rank]
        
        # Adjust for hand quality within its rank
        quality_adjustment = self._calculate_quality_adjustment(hand_rank, best_cards)
        
        return base_strength * quality_adjustment
    
    def _calculate_drawing_strength(self, game_state: GameState) -> float:
        """Calculate drawing hand strength"""
        if len(game_state.community_cards) >= 5:  # River
            return 0.0
            
        draws = self._identify_draws(game_state.hand + game_state.community_cards)
        
        if not draws:
            return 0.0
            
        # Calculate drawing strength based on outs and remaining cards
        strength = 0.0
        for draw_type, outs in draws.items():
            if draw_type == 'flush_draw':
                strength = max(strength, 0.4)
            elif draw_type == 'straight_draw':
                strength = max(strength, 0.35 if outs >= 8 else 0.25)
            elif draw_type == 'two_pair_draw':
                strength = max(strength, 0.2)
                
        return strength
    
    def _identify_draws(self, cards: List[Card]) -> Dict[str, int]:
        """Identify possible draws and their outs"""
        draws = {}
        
        # Check for flush draws
        suits = {}
        for card in cards:
            suits[card.suit] = suits.get(card.suit, 0) + 1
        for suit, count in suits.items():
            if count == 4:
                draws['flush_draw'] = 9
                
        # Check for straight draws
        values = sorted(set(card.value for card in cards))
        gaps = []
        for i in range(len(values) - 1):
            gaps.append(values[i+1] - values[i])
        
        # Open-ended straight draw
        if len(values) >= 4 and sum(gaps[:3]) == 3:
            draws['straight_draw'] = 8
        # Gutshot straight draw
        elif len(values) >= 4 and sum(gaps[:3]) == 4:
            draws['straight_draw'] = 4
            
        return draws
    
    def _calculate_quality_adjustment(self, hand_rank: HandRank, best_cards: List[Card]) -> float:
        """Calculate quality adjustment within a hand rank"""
        if hand_rank == HandRank.HIGH_CARD:
            return (best_cards[0].value - 2) / 12
        elif hand_rank == HandRank.PAIR:
            return (best_cards[0].value - 2) / 12
        elif hand_rank == HandRank.TWO_PAIR:
            return ((best_cards[0].value - 2) + (best_cards[2].value - 2)) / 24
        else:
            return 1.0

def run_performance_tests():
    """Run performance tests with multiple scenarios"""
    bot = AdvancedPokerBot()
    
    # Create test scenarios
    scenarios = [
        {
            'name': 'Basic preflop decision',
            'game_state': GameState(
                position=0,
                stack_size=1000,
                pot_size=100,
                current_bet=20,
                num_players=6,
                hand=[Card(14, Suit.HEARTS), Card(13, Suit.HEARTS)],
                street='preflop'
            )
        },
        {
            'name': 'Complex postflop decision',
            'game_state': GameState(
                position=2,
                stack_size=800,
                pot_size=300,
                current_bet=100,
                num_players=4,
                hand=[Card(10, Suit.HEARTS), Card(9, Suit.HEARTS)],
                street='flop',
                community_cards=[
                    Card(8, Suit.HEARTS),
                    Card(2, Suit.DIAMONDS),
                    Card(3, Suit.CLUBS)
                ]
            )
        },
        # Add more test scenarios here
    ]
    
    # Run tests
    for scenario in scenarios:
        print(f"\nTesting scenario: {scenario['name']}")
        try:
            action, amount = bot.decide_action(scenario['game_state'])
            print(f"Decision: {action} {amount}")
            # Add additional metrics and analysis here
        except Exception as e:
            print(f"Error in scenario {scenario['name']}: {str(e)}")

if __name__ == "__main__":
    # Run comprehensive tests
    run_comprehensive_tests()
    
    # Run performance tests
    run_performance_tests()