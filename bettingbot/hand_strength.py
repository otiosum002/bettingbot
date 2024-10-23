# File: hand_strength.py
from typing import Dict, List
from models import Card, GameState
from enums import HandRank
from hand_evaluator import HandEvaluator

class HandStrengthCalculator:
    def __init__(self):
        self.hand_evaluator = HandEvaluator()
    
    # [Include HandStrengthCalculator implementation...]