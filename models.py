"""
Data models for the Kata Execution Platform
"""

from pydantic import BaseModel
from typing import List


class Kata(BaseModel):
    id: str
    title: str
    description: str
    starter_code: str


class Submission(BaseModel):
    kata_id: str
    code: str


class Result(BaseModel):
    status: str  # "PASS", "FAIL", or "ERROR"
    message: str = ""