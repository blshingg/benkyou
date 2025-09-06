import time
from collections import deque
from spaced_repetition.card import Card
from spaced_repetition.card_data import CardData
from spaced_repetition.deck import Deck
import pytest

@pytest.fixture
def deck():
    return Deck()

def test_deck_initialization(deck):
    assert deck.levels == {0: deque(), 1: deque(), 2: deque(), 3: deque()}
    assert deck.review_deck == deque()
    assert deck.waiting_deck == deque()

def test_add_card_to_level(deck):
    card_data = CardData(card=Card(level=1), japanese="Q", english="A")
    deck.add_card(card_data)
    assert card_data in deck.levels[1]

def test_add_card_to_review_deck(deck):
    card_data = CardData(card=Card(level=4), japanese="Q", english="A")
    deck.add_card(card_data)
    assert card_data in deck.review_deck

def test_get_next_card_from_levels(deck):
    card_data_1 = CardData(card=Card(level=1), japanese="Q1", english="A1")
    card_data_2 = CardData(card=Card(level=2), japanese="Q2", english="A2")
    deck.add_card(card_data_1)
    deck.add_card(card_data_2)
    next_card = deck.get_next_card()
    assert next_card == card_data_2
    next_card = deck.get_next_card()
    assert next_card == card_data_1

def test_get_next_card_from_review_deck(deck):
    card_data = CardData(card=Card(level=4), japanese="Q", english="A")
    deck.add_card(card_data)
    next_card = deck.get_next_card()
    assert next_card == card_data

def test_get_next_card_empty(deck):
    assert deck.get_next_card() is None

def test_requeue_card(deck):
    card_data = CardData(card=Card(), japanese="Q", english="A", last_reviewed_time=0)
    deck.requeue_card(card_data)
    assert card_data in deck.waiting_deck

def test_requeue_card_moves_to_levels(deck):
    card_data = CardData(card=Card(), japanese="Q", english="A", last_reviewed_time=time.time() - 100)
    deck.requeue_card(card_data)
    deck.check_waiting_deck()
    assert not any(c.japanese == 'Q' for c in deck.waiting_deck)
    assert any(c.japanese == 'Q' for c in deck.levels[0])

def test_get_all_cards(deck):
    card_data_1 = CardData(card=Card(level=1), japanese="Q1", english="A1")
    card_data_2 = CardData(card=Card(level=4), japanese="Q2", english="A2")
    card_data_3 = CardData(card=Card(), japanese="Q3", english="A3", last_reviewed_time=0)
    deck.add_card(card_data_1)
    deck.add_card(card_data_2)
    deck.requeue_card(card_data_3)
    all_cards = deck.get_all_cards()
    assert len(all_cards) == 3
    assert card_data_1 in all_cards
    assert card_data_2 in all_cards
    assert card_data_3 in all_cards

def test_requeue_card_no_last_reviewed_time(deck):
    card_data = CardData(card=Card(), japanese="Q", english="A", last_reviewed_time=None)
    deck.requeue_card(card_data)
    deck.check_waiting_deck()
    assert not any(c.japanese == 'Q' for c in deck.waiting_deck)
    assert any(c.japanese == 'Q' for c in deck.levels[0])

def test_requeue_card_wait_time_zero(deck):
    card_data = CardData(card=Card(interval=0), japanese="Q", english="A", last_reviewed_time=time.time())
    deck.requeue_card(card_data)
    deck.check_waiting_deck()
    assert not any(c.japanese == 'Q' for c in deck.waiting_deck)
    assert any(c.japanese == 'Q' for c in deck.levels[0])

def test_get_next_card_level_order(deck):
    card_data_0 = CardData(card=Card(level=0), japanese="Q0", english="A0")
    card_data_1 = CardData(card=Card(level=1), japanese="Q1", english="A1")
    card_data_2 = CardData(card=Card(level=2), japanese="Q2", english="A2")
    card_data_3 = CardData(card=Card(level=3), japanese="Q3", english="A3")
    deck.add_card(card_data_1)
    deck.add_card(card_data_3)
    deck.add_card(card_data_0)
    deck.add_card(card_data_2)
    assert deck.get_next_card() == card_data_3
    assert deck.get_next_card() == card_data_2
    assert deck.get_next_card() == card_data_1
    assert deck.get_next_card() == card_data_0

def test_get_next_card_review_deck_after_levels(deck):
    card_data_level = CardData(card=Card(level=1), japanese="Q_level", english="A_level")
    card_data_review = CardData(card=Card(level=4), japanese="Q_review", english="A_review")
    deck.add_card(card_data_level)
    deck.add_card(card_data_review)
    assert deck.get_next_card() == card_data_level
    assert deck.get_next_card() == card_data_review

def test_get_all_cards_empty(deck):
    assert deck.get_all_cards() == []