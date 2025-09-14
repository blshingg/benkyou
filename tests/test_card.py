
from datetime import timedelta
import pytest
from spaced_repetition.card import Card

def test_card_initialization():
    card = Card()
    assert card.status == "learning"
    assert card.interval is None
    assert card.ease == 2.5
    assert card.step == 0
    assert card.level == 0

def test_card_initialization_with_params():
    card = Card(status="reviewing", interval=timedelta(days=1), ease=3.0, step=1, level=2)
    assert card.status == "reviewing"
    assert card.interval == timedelta(days=1)
    assert card.ease == 3.0
    assert card.step == 1
    assert card.level == 2

def test_card_ease_lower_bound():
    card = Card(ease=1.0)
    assert card.ease == 1.3

def test_card_repr():
    card = Card()
    assert repr(card) == "Card(status=learning, step=0, interval=None, ease=2.5, level=0)"

def test_card_options_learning_step0():
    card = Card()
    options = card.options(1)
    assert len(options) == 4
    assert options[0][0] == "again"
    assert options[1][0] == "hard"
    assert options[2][0] == "good"
    assert options[3][0] == "easy"
    assert options[0][1].status == "learning"
    assert options[0][1].interval == timedelta(minutes=1)
    assert options[1][1].status == "learning"
    assert options[1][1].interval == timedelta(minutes=3)
    assert options[2][1].status == "learning"
    assert options[2][1].interval == timedelta(minutes=5)
    assert options[3][1].status == "reviewing"
    assert options[3][1].interval == timedelta(days=4)

def test_card_options_learning_step1():
    card = Card(step=1)
    options = card.options(1)
    assert len(options) == 4
    assert options[2][1].status == "reviewing"
    assert options[2][1].interval == timedelta(days=1)

def test_card_options_reviewing():
    card = Card(status="reviewing", interval=timedelta(days=10))
    options = card.options(1)
    assert len(options) == 4
    assert options[0][1].status == "relearning"
    assert options[0][1].ease == 2.3
    assert options[1][1].status == "reviewing"
    assert options[1][1].interval == timedelta(days=12)
    assert options[2][1].status == "reviewing"
    assert options[2][1].interval == timedelta(days=25)
    assert options[3][1].status == "reviewing"
    assert options[3][1].interval == timedelta(days=37.5)

def test_card_options_relearning():
    card = Card(status="relearning")
    options = card.options(1)
    assert len(options) == 4
    assert options[0][1].status == "relearning"
    assert options[0][1].interval == timedelta(minutes=1)
    assert options[1][1].status == "relearning"
    assert options[1][1].interval == timedelta(minutes=6)
    assert options[2][1].status == "reviewing"
    assert options[2][1].interval == timedelta(days=1)
    assert options[3][1].status == "reviewing"
    assert options[3][1].interval == timedelta(days=4)

def test_card_to_dict():
    card = Card(status="reviewing", interval=timedelta(days=10), ease=3.0, step=1, level=2)
    card_dict = card.to_dict()
    assert card_dict["status"] == "reviewing"
    assert card_dict["interval"] == 864000.0
    assert card_dict["ease"] == 3.0
    assert card_dict["step"] == 1
    assert card_dict["level"] == 2

def test_card_from_dict():
    card_dict = {
        "status": "reviewing",
        "interval": 864000.0,
        "ease": 3.0,
        "step": 1,
        "level": 2
    }
    card = Card.from_dict(card_dict)
    assert card.status == "reviewing"
    assert card.interval == timedelta(days=10)
    assert card.ease == 3.0
    assert card.step == 1
    assert card.level == 2
