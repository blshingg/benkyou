from collections import deque
import time

from spaced_repetition.card import Card 

class Deck:

    levels: dict[int, deque[dict[str, Card | str | int]]]
    review_deck: deque[dict[str, Card | str | int]]
    waiting_deck: deque[dict[str, Card | str | int]]

    def __init__(self):
        self.levels = {0: deque(), 1: deque(), 2: deque(), 3: deque()}
        self.review_deck = deque()
        self.waiting_deck = deque()

    def add_card(self, card_data: dict[str, Card | str | int]):
        level = card_data["card"].level
        if 0 <= level <= 3:
            self.levels[level].append(card_data)
        else:
            self.review_deck.append(card_data)

    def get_next_card(self) -> dict[str, Card | str | int] | None:
        for level in reversed(sorted(self.levels.keys())):
            if self.levels[level]:
                return self.levels[level].popleft()
        
        if self.review_deck:
            return self.review_deck.popleft()
        
        return None # No more cards

    def requeue_card(self, card_data: dict[str, Card | str | int]):
        to_remove = []
        for card in self.waiting_deck:
            wait_time = card['card'].interval.total_seconds() if card['card'].interval else 0
            last_reviewed_time = card['last_reviewed_time'] if card['last_reviewed_time'] else 0
            if last_reviewed_time + wait_time <= time.time() or wait_time == 0 or last_reviewed_time == 0:
                self.add_card(card)
                to_remove += [card]
        
        [self.waiting_deck.remove(card) for card in to_remove]
        self.waiting_deck.append(card_data)

    def get_all_cards(self) -> list[dict[str, Card | str | int]]:
        all_cards = []
        for level in self.levels.values():
            all_cards.extend(level)
        all_cards.extend(self.review_deck)
        all_cards.extend(self.waiting_deck)
        return all_cards
