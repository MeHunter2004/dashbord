from pathlib import Path
from threading import RLock

import pandas as pd

from app.repositories.base_repository import RequestRepository


REQUIRED_COLUMNS = {
    'ReqID', 'Yr', 'Mth', 'Tech', 'TechGroup', 'Category', 'RequestType',
    'Priority', 'DueTime', 'ReqStatus', 'Elapsed_hrs', 'Violation_hrs',
}
TEXT_COLUMNS = ['Tech', 'TechGroup', 'Category', 'RequestType', 'Priority', 'DueTime', 'ReqStatus']


class ExcelRequestRepository(RequestRepository):
    def __init__(self, file_path: str, sheet_name: str):
        self.file_path = Path(file_path)
        self.sheet_name = sheet_name
        self._cache: pd.DataFrame | None = None
        self._fingerprint: tuple[int, int] | None = None
        self._lock = RLock()

    @property
    def data_version(self) -> str:
        if self._fingerprint is None:
            return ''
        return f'{self._fingerprint[0]}:{self._fingerprint[1]}'

    def _file_fingerprint(self) -> tuple[int, int]:
        if not self.file_path.is_file():
            raise FileNotFoundError(f'Excel file not found: {self.file_path.resolve()}')
        stat = self.file_path.stat()
        return stat.st_mtime_ns, stat.st_size

    def _read_file(self) -> pd.DataFrame:
        df = pd.read_excel(self.file_path, sheet_name=self.sheet_name)
        missing = REQUIRED_COLUMNS - set(df.columns)
        if missing:
            raise ValueError(f'Missing required columns: {sorted(missing)}')
        df = df[list(REQUIRED_COLUMNS)].copy()
        for column in TEXT_COLUMNS:
            df[column] = (
                df[column].fillna('نامشخص').astype(str).str.strip()
                .replace({'': 'نامشخص', 'nan': 'نامشخص'})
            )
        for column in ['ReqID', 'Yr', 'Mth', 'Elapsed_hrs', 'Violation_hrs']:
            df[column] = pd.to_numeric(df[column], errors='coerce').fillna(0)
        df['ReqID'] = df['ReqID'].astype(int)
        df['Yr'] = df['Yr'].astype(int)
        df['Mth'] = df['Mth'].astype(int)
        return df

    def load_requests(self) -> pd.DataFrame:
        fingerprint = self._file_fingerprint()
        if self._cache is not None and fingerprint == self._fingerprint:
            return self._cache

        with self._lock:
            fingerprint = self._file_fingerprint()
            if self._cache is None or fingerprint != self._fingerprint:
                dataframe = self._read_file()
                if self._file_fingerprint() != fingerprint:
                    dataframe = self._read_file()
                    fingerprint = self._file_fingerprint()
                self._cache = dataframe
                self._fingerprint = fingerprint
            return self._cache
