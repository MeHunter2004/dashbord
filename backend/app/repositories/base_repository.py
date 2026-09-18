from abc import ABC, abstractmethod
import pandas as pd

class RequestRepository(ABC):
    @abstractmethod
    def load_requests(self) -> pd.DataFrame:
        """Return normalized request-level records."""
        raise NotImplementedError
