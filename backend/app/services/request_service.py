from threading import RLock

import pandas as pd

from app.core.statuses import high_level_status
from app.repositories.base_repository import RequestRepository
from app.schemas.common import FilterPayload, PagePayload


class RequestService:
    def __init__(self, repository: RequestRepository):
        self.repository = repository
        self._dataframe_cache: pd.DataFrame | None = None
        self._options_cache: dict | None = None
        self._cache_version = ''
        self._lock = RLock()

    def dataframe(self) -> pd.DataFrame:
        source = self.repository.load_requests()
        version = self.repository.data_version
        if self._dataframe_cache is not None and version == self._cache_version:
            return self._dataframe_cache

        with self._lock:
            if self._dataframe_cache is None or version != self._cache_version:
                self._dataframe_cache = source.assign(
                    HighLevelStatus=source['ReqStatus'].map(high_level_status),
                    Period=source['Yr'].astype(str) + '/' + source['Mth'].astype(str).str.zfill(2),
                )
                self._options_cache = None
                self._cache_version = version
            return self._dataframe_cache

    def filter(self, payload: FilterPayload) -> pd.DataFrame:
        dataframe = self.dataframe()
        selections = [
            ('Yr', payload.years), ('Mth', payload.months), ('ReqStatus', payload.statuses),
            ('RequestType', payload.request_types), ('Priority', payload.priorities),
            ('TechGroup', payload.tech_groups), ('Tech', payload.techs), ('Category', payload.categories),
        ]
        for column, values in selections:
            if values:
                dataframe = dataframe[dataframe[column].isin(values)]
        if payload.only_sla_violated:
            dataframe = dataframe[dataframe['Violation_hrs'] > 0]
        if payload.only_open:
            dataframe = dataframe[dataframe['HighLevelStatus'] == 'باز / در جریان']
        return dataframe

    def options(self) -> dict:
        dataframe = self.dataframe()
        if self._options_cache is None:
            self._options_cache = {
                'years': sorted(dataframe['Yr'].unique().tolist(), reverse=True),
                'months': sorted(dataframe['Mth'].unique().tolist()),
                'statuses': sorted(dataframe['ReqStatus'].unique().tolist()),
                'request_types': sorted(dataframe['RequestType'].unique().tolist()),
                'priorities': sorted(dataframe['Priority'].unique().tolist()),
                'tech_groups': sorted(dataframe['TechGroup'].unique().tolist()),
                'techs': sorted(dataframe['Tech'].unique().tolist()),
                'categories': sorted(dataframe['Category'].unique().tolist()),
            }
        return self._options_cache

    def kpis(self, payload: FilterPayload) -> dict:
        dataframe = self.filter(payload)
        total = len(dataframe)
        return {
            'total': total,
            'open': int((dataframe.HighLevelStatus == 'باز / در جریان').sum()),
            'closed': int((dataframe.HighLevelStatus == 'رسیدگی‌شده').sum()),
            'rejected': int((dataframe.HighLevelStatus == 'ردشده').sum()),
            'sla_violated': int((dataframe.Violation_hrs > 0).sum()),
            'violation_hours_sum': round(float(dataframe.Violation_hrs.sum()), 2),
            'elapsed_hours_avg': round(float(dataframe.Elapsed_hrs.mean()), 2) if total else 0,
            'high_urgent': int(dataframe.Priority.isin(['زیاد', 'اضطراری']).sum()),
        }

    def charts(self, payload: FilterPayload) -> dict:
        dataframe = self.filter(payload)

        def count(column: str) -> list[dict]:
            return [{'name': str(name), 'value': int(value)} for name, value in dataframe[column].value_counts().items()]

        monthly = dataframe.groupby('Period', sort=True).agg(
            total=('ReqID', 'count'),
            sla=('Violation_hrs', lambda values: int((values > 0).sum())),
        ).reset_index()
        matrix = dataframe.groupby(['RequestType', 'HighLevelStatus']).size().unstack(fill_value=0)
        return {
            'status': count('HighLevelStatus'),
            'status_details': count('ReqStatus'),
            'priority': count('Priority'),
            'top_categories': count('Category')[:10],
            'technicians': count('Tech'),
            'monthly': monthly.to_dict(orient='records'),
            'request_type_stacked': {
                'categories': matrix.index.tolist(),
                'series': [{'name': str(column), 'data': matrix[column].astype(int).tolist()} for column in matrix.columns],
            },
        }

    def requests(self, payload: PagePayload) -> dict:
        dataframe = self.filter(payload)
        if payload.search.strip():
            needle = payload.search.strip().casefold()
            columns = ['ReqID', 'Tech', 'TechGroup', 'Category', 'ReqStatus']
            mask = pd.Series(False, index=dataframe.index)
            for column in columns:
                mask |= dataframe[column].astype(str).str.casefold().str.contains(needle, regex=False)
            dataframe = dataframe[mask]
        sort_by = payload.sort_by if payload.sort_by in dataframe.columns else 'ReqID'
        dataframe = dataframe.sort_values(sort_by, ascending=not payload.sort_desc)
        total = len(dataframe)
        start = (payload.page - 1) * payload.page_size
        rows = dataframe.iloc[start:start + payload.page_size].to_dict(orient='records')
        return {'total': total, 'page': payload.page, 'page_size': payload.page_size, 'rows': rows}
