
import pytest
from utils.fuzzy_match import fuzzy_match


def test_fuzzy_match_exact():
    assert fuzzy_match("apple", "apple")


def test_fuzzy_match_partial():
    assert fuzzy_match("aple", "apple")


def test_fuzzy_match_case_insensitive():
    assert fuzzy_match("Apple", "apple")


def test_fuzzy_match_no_match():
    assert not fuzzy_match("banana", "apple")


def test_fuzzy_match_empty_query():
    assert fuzzy_match("", "apple")


def test_fuzzy_match_empty_target():
    assert not fuzzy_match("apple", "")


def test_fuzzy_match_empty_both():
    assert fuzzy_match("", "")


def test_fuzzy_match_with_spaces():
    assert fuzzy_match("a p l", "a p p l e")
