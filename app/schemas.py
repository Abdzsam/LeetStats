from typing import Optional

from pydantic import BaseModel

class StatsResponse(BaseModel):
    username: str
    total_solved: int
    easy_solved: int
    medium_solved: int
    hard_solved: int
    current_streak: Optional[int] = None
    longest_streak: Optional[int] = None
