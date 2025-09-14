
import pytest
from translation.romaji_to_kana import (
    to_katakana,
    to_hiragana,
    to_kana,
    to_hepburn,
    to_kunrei,
    to_roma,
    normalize_double_n,
)


def test_normalize_double_n():
    assert normalize_double_n("nani") == "nani"
    assert normalize_double_n("onna") == "on'a"
    assert normalize_double_n("kannji") == "kanji"
    assert normalize_double_n("sannpo") == "sanpo"


def test_to_katakana():
    assert to_katakana("nihon") == "ニホン"
    assert to_katakana("amerika") == "アメリカ"
    assert to_katakana("konpyuutaa") == "コンピュウタア"


def test_to_hiragana():
    assert to_hiragana("nihon") == "にほん"
    assert to_hiragana("amerika") == "あめりか"
    assert to_hiragana("konpyuutaa") == "こんぴゅうたあ"


def test_to_kana():
    assert to_kana("nihon") == "ニホン"


def test_to_hepburn():
    assert to_hepburn("にほん") == "nihon"
    assert to_hepburn("しんぶん") == "shinbun"
    assert to_hepburn("ちゃ") == "cha"


def test_to_roma():
    assert to_roma("にほん") == "nihon"
    assert to_roma("しんぶん") == "shinbun"
    assert to_roma("ちゃ") == "cha"
