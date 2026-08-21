from abc import ABC, abstractmethod


class BaseAIProvider(ABC):
    @abstractmethod
    def generate_response(self, message: str) -> str:
        """
        Generate a response for the user's message.
        """
        pass
