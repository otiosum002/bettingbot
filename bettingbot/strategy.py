# File: strategy.py
from typing import Dict
from models import GameState

class StrategyAdjustor:
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

    # [Include rest of the StrategyAdjustor implementation...]