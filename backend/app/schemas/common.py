from pydantic import BaseModel, Field
from typing import Any

class FilterPayload(BaseModel):
    years: list[int] = []
    months: list[int] = []
    statuses: list[str] = []
    request_types: list[str] = []
    priorities: list[str] = []
    tech_groups: list[str] = []
    techs: list[str] = []
    categories: list[str] = []
    only_sla_violated: bool = False
    only_open: bool = False

class PagePayload(FilterPayload):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=25, ge=1, le=200)
    search: str = ''
    sort_by: str = 'ReqID'
    sort_desc: bool = True

class ChartItem(BaseModel):
    name: str
    value: float | int
    extra: dict[str, Any] = {}
