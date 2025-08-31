
###
# MIT License

# Copyright (c) 2024 Víctor López Ferrando

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
###
from datetime import timedelta as td
from typing import Self


class Card:
    def __init__(self, status="learning", interval=None, ease=2.5, step=0, level=0):
        self.status, self.interval, self.step = status, interval, step
        self.ease = max(ease, 1.3)
        self.level = level

    def __repr__(self):
        return f"Card(status={self.status}, step={self.step}, interval={self.interval}, ease={self.ease}, level={self.level})"

    def options(self) -> list[tuple[str, Self]]:
        if self.status == "learning":
            options = [
                Card("learning", td(minutes=1), level=0),
                Card("learning", td(minutes=3), step=1, level=self.level + 1),
                Card("learning", td(minutes=5), step=1, level=self.level + 1)
                if self.step == 0
                else Card("reviewing", td(days=1), level=self.level + 1),
                Card("reviewing", td(days=4), level=self.level + 1),
            ]
        elif self.status == "reviewing":
            options = [
                Card("relearning", td(minutes=10), self.ease - 0.2, level=self.level - 1),
                Card("reviewing", self.interval * 1.2, self.ease - 0.15, level=self.level - 1),
                Card("reviewing", self.interval * self.ease, self.ease, level=self.level - 1),
                Card("reviewing", self.interval * self.ease * 1.5, self.ease + 0.15, level=self.level + 1),
            ]
        elif self.status == "relearning":
            options = [
                Card("relearning", td(minutes=1), self.ease, level=self.level - 1),
                Card("relearning", td(minutes=6), self.ease, level=self.level - 1),
                Card("reviewing", td(days=1), self.ease, level=self.level - 1),
                Card("reviewing", td(days=4), self.ease, level=self.level + 1),
            ]
        return list(zip(["again", "hard", "good", "easy"], options))

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "step": self.step,
            "interval": self.interval.total_seconds() if self.interval else None,
            "ease": self.ease,
            "level": self.level,
        }
        
    @classmethod
    def from_dict(cls, card_dict: dict) -> Self:
        return cls(
            status=card_dict["status"],
            interval=td(seconds=card_dict["interval"]) if card_dict["interval"] else None,
            ease=card_dict["ease"],
            step=card_dict["step"],
            level=card_dict["level"],
        )