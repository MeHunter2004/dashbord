from abc import ABC, abstractmethod
import pandas as pd

class RequestRepository(ABC):
    @abstractmethod
    def load_requests(self) -> pd.DataFrame:
        """Return normalized request-level records."""
        raise NotImplementedError

    @property
    @abstractmethod
    def data_version(self) -> str:
        """Return a stable identifier for the loaded data snapshot."""
        raise NotImplementedError
