from abc import ABC, abstractmethod
import pandas as pd

class BaseModel(ABC):

    @abstractmethod
    def train(self, X: pd.DataFrame, y: pd.Series):
        pass

    @abstractmethod
    def predict_proba(self, X: pd.DataFrame) -> pd.Series:
        pass
