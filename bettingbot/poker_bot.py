# File: poker_bot.py
from typing import Tuple
import statistics
from models import GameState, Card
from enums import Action, Suit
from hand_evaluator import HandEvaluator
from opponent_tracking import EnhancedOpponentTracker
from strategy import StrategyAdjustor

class AdvancedPokerBot:
    def __init__(self):
        self.hand_evaluator = HandEvaluator()
        self.opponent_tracker = EnhancedOpponentTracker()
        self.initial_credits = 10000
        self.all_in_threshold = 6000
        self.min_hands_for_stats = 20
        self.strategy_adjustor = StrategyAdjustor()
        self.hand_history = deque(maxlen=1000)
    
    # [Include AdvancedPokerBot implementation...]