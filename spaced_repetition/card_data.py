from typing import Optional
from .card import Card
import random

class CardData:
    """Represents card data with question, answer, and spaced repetition information."""
    
    def __init__(
        self,
        card: Card,
        japanese: str,
        english: str,
        reading: Optional[str] = None,
        level: int = 0,
        last_reviewed_time: Optional[float] = None
    ):
        self.card = card
        self.japanese = japanese
        self.english = english
        self.reading = reading
        self.level = level
        self.last_reviewed_time = last_reviewed_time
        random.seed(self.japanese)
        self.sort_key = random.random()
    
    def __repr__(self) -> str:
        return f"CardData(card={self.card}, japanese='{self.japanese}', english='{self.english}', reading='{self.reading}', level={self.level}, last_reviewed_time={self.last_reviewed_time})"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, CardData):
            return False
        return (
            self.card == other.card and
            self.japanese == other.japanese and
            self.english == other.english and
            self.reading == other.reading and
            self.level == other.level and
            self.last_reviewed_time == other.last_reviewed_time
        )
    
    def to_dict(self) -> dict[str, Card | str | int | float | None]:
        """Convert CardData to dictionary format for backward compatibility."""
        return {
            "card": self.card,
            "japanese": self.japanese,
            "english": self.english,
            "reading": self.reading,
            "level": self.level,
            "last_reviewed_time": self.last_reviewed_time
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Card | str | int | float | None]) -> "CardData":
        """Create CardData from dictionary format."""
        return cls(
            card=data["card"],
            japanese=data["japanese"],
            english=data["english"],
            reading=data.get("reading"),
            level=data.get("level", 0),
            last_reviewed_time=data.get("last_reviewed_time")
        )
    
    @classmethod
    def from_legacy_dict(cls, data: dict[str, Card | str | int | float | None]) -> "CardData":
        """Create CardData from legacy dictionary format that uses 'question' and 'answer' keys."""
        return cls(
            card=data["card"],
            japanese=data.get("question", data.get("japanese", "")),
            english=data.get("answer", data.get("english", "")),
            reading=data.get("reading"),
            level=data.get("level", 0),
            last_reviewed_time=data.get("last_reviewed_time")
        )
