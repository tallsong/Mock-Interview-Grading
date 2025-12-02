from dataclasses import dataclass, field
from typing import List, Optional, Dict

@dataclass
class Question:
    id: str
    prompt: str
    ideal_answer: str

@dataclass
class EvaluationResult:
    score: int
    feedback: str
    cached: bool = False
