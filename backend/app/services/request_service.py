import pandas as pd
from app.core.statuses import high_level_status
from app.repositories.base_repository import RequestRepository
from app.schemas.common import FilterPayload, PagePayload

class RequestService:
    def __init__(self, repository: RequestRepository):
        self.repository = repository

    def dataframe(self) -> pd.DataFrame:
        df = self.repository.load_requests()
        df['HighLevelStatus'] = df['ReqStatus'].map(high_level_status)
        df['Period'] = df['Yr'].astype(str) + '/' + df['Mth'].astype(str).str.zfill(2)
        return df

    def filter(self, payload: FilterPayload) -> pd.DataFrame:
        df = self.dataframe()
        selections = [
            ('Yr', payload.years), ('Mth', payload.months), ('ReqStatus', payload.statuses),
            ('RequestType', payload.request_types), ('Priority', payload.priorities),
            ('TechGroup', payload.tech_groups), ('Tech', payload.techs), ('Category', payload.categories),
        ]
        for column, values in selections:
            if values:
                df = df[df[column].isin(values)]
        if payload.only_sla_violated:
            df = df[df['Violation_hrs'] > 0]
        if payload.only_open:
            df = df[df['HighLevelStatus'] == 'باز / در جریان']
        return df

    def options(self) -> dict:
        df = self.dataframe()
        return {
            'years': sorted(df['Yr'].unique().tolist(), reverse=True),
            'months': sorted(df['Mth'].unique().tolist()),
            'statuses': sorted(df['ReqStatus'].unique().tolist()),
            'request_types': sorted(df['RequestType'].unique().tolist()),
            'priorities': sorted(df['Priority'].unique().tolist()),
            'tech_groups': sorted(df['TechGroup'].unique().tolist()),
            'techs': sorted(df['Tech'].unique().tolist()),
            'categories': sorted(df['Category'].unique().tolist()),
        }

    def kpis(self, payload: FilterPayload) -> dict:
        df = self.filter(payload)
        total = len(df)
        return {
            'total': total,
            'open': int((df.HighLevelStatus == 'باز / در جریان').sum()),
            'closed': int((df.HighLevelStatus == 'رسیدگی‌شده').sum()),
            'rejected': int((df.HighLevelStatus == 'ردشده').sum()),
            'sla_violated': int((df.Violation_hrs > 0).sum()),
            'violation_hours_sum': round(float(df.Violation_hrs.sum()), 2),
            'elapsed_hours_avg': round(float(df.Elapsed_hrs.mean()), 2) if total else 0,
            'high_urgent': int(df.Priority.isin(['زیاد', 'اضطراری']).sum()),
        }

    def charts(self, payload: FilterPayload) -> dict:
        df = self.filter(payload)
        def count(column):
            return [{'name': str(k), 'value': int(v)} for k, v in df[column].value_counts().items()]
        monthly = df.groupby('Period', sort=True).agg(total=('ReqID', 'count'), sla=('Violation_hrs', lambda x: int((x > 0).sum()))).reset_index()
        matrix = df.groupby(['RequestType', 'HighLevelStatus']).size().unstack(fill_value=0)
        return {
            'status': count('HighLevelStatus'),
            'status_details': count('ReqStatus'),
            'priority': count('Priority'),
            'top_categories': count('Category')[:10],
            'monthly': monthly.to_dict(orient='records'),
            'request_type_stacked': {
                'categories': matrix.index.tolist(),
                'series': [{'name': str(col), 'data': matrix[col].astype(int).tolist()} for col in matrix.columns],
            },
        }

    def requests(self, payload: PagePayload) -> dict:
        df = self.filter(payload)
        if payload.search.strip():
            needle = payload.search.strip().casefold()
            cols = ['ReqID', 'Tech', 'TechGroup', 'Category', 'ReqStatus']
            mask = pd.Series(False, index=df.index)
            for col in cols:
                mask |= df[col].astype(str).str.casefold().str.contains(needle, regex=False)
            df = df[mask]
        allowed = set(df.columns)
        sort_by = payload.sort_by if payload.sort_by in allowed else 'ReqID'
        df = df.sort_values(sort_by, ascending=not payload.sort_desc)
        total = len(df)
        start = (payload.page - 1) * payload.page_size
        rows = df.iloc[start:start + payload.page_size].to_dict(orient='records')
        return {'total': total, 'page': payload.page, 'page_size': payload.page_size, 'rows': rows}
