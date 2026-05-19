from typing import TypeVar, Generic

T = TypeVar("T")


class BaseService(Generic[T]):
    def __init__(self, repo: T):
        self.repo = repo

