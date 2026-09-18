from pathlib import Path
import pandas as pd
from app.repositories.base_repository import RequestRepository

REQUIRED_COLUMNS = {
    'ReqID', 'Yr', 'Mth', 'Tech', 'TechGroup', 'Category', 'RequestType',
    'Priority', 'DueTime', 'ReqStatus', 'Elapsed_hrs', 'Violation_hrs'
}
TEXT_COLUMNS = ['Tech', 'TechGroup', 'Category', 'RequestType', 'Priority', 'DueTime', 'ReqStatus']

class ExcelRequestRepository(RequestRepository):
    def __init__(self, file_path: str, sheet_name: str):
        self.file_path = Path(file_path)
        self.sheet_name = sheet_name
        self._cache: pd.DataFrame | None = None

    def load_requests(self) -> pd.DataFrame:
        if self._cache is not None:
            return self._cache.copy()
        if not self.file_path.exists():
            raise FileNotFoundError(f'Excel file not found: {self.file_path.resolve()}')
        df = pd.read_excel(self.file_path, sheet_name=self.sheet_name)
        missing = REQUIRED_COLUMNS - set(df.columns)
        if missing:
            raise ValueError(f'Missing required columns: {sorted(missing)}')
        df = df[list(REQUIRED_COLUMNS)].copy()
        for col in TEXT_COLUMNS:
            df[col] = df[col].fillna('نامشخص').astype(str).str.strip().replace({'': 'نامشخص', 'nan': 'نامشخص'})
        for col in ['ReqID', 'Yr', 'Mth', 'Elapsed_hrs', 'Violation_hrs']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        df['ReqID'] = df['ReqID'].astype(int)
        df['Yr'] = df['Yr'].astype(int)
        df['Mth'] = df['Mth'].astype(int)
        self._cache = df
        return df.copy()
