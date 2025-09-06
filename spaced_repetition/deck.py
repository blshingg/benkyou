from collections import deque
import time
from typing import Optional

from spaced_repetition.card import Card
from spaced_repetition.card_data import CardData 

class Deck:

    levels: dict[int, deque[CardData]]
    review_deck: deque[CardData]
    waiting_deck: deque[CardData]

    def __init__(self):
        self.levels = {0: deque(), 1: deque(), 2: deque(), 3: deque()}
        self.review_deck = deque()
        self.waiting_deck = deque()

    def add_card(self, card_data: CardData):
        level = card_data.card.level
        if 0 <= level <= 3:
            self.levels[level].appendleft(card_data)
        else:
            self.review_deck.appendleft(card_data)

    def get_next_card(self) -> Optional[CardData]:
        self.check_waiting_deck()
        for level in reversed(sorted(self.levels.keys())):
            if self.levels[level]:
                return self.levels[level].popleft()
        
        if self.review_deck:
            return self.review_deck.popleft()
        
        return None # No more cards
    
    def check_waiting_deck(self):
        to_remove = []
        for card in self.waiting_deck:
            wait_time = card.card.interval.total_seconds() if card.card.interval else 0
            last_reviewed_time = card.last_reviewed_time if card.last_reviewed_time else 0
            if last_reviewed_time + wait_time <= time.time() or wait_time == 0 or last_reviewed_time == 0:
                self.add_card(card)
                to_remove += [card]
        
        [self.waiting_deck.remove(card) for card in to_remove]

    def requeue_card(self, card_data: CardData):
        self.waiting_deck.append(card_data)

    def get_all_cards(self) -> list[CardData]:
        all_cards = []
        for level in self.levels.values():
            all_cards.extend(level)
        all_cards.extend(self.review_deck)
        all_cards.extend(self.waiting_deck)
        return all_cards
