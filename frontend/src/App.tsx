import { useEffect, useMemo, useState } from 'react';
import ReactECharts from 'echarts-for-react';
import { api, emptyFilters, Filters } from './api';

type OptionValue = string | number;
type Options = Record<string, OptionValue[]>;
type ChartItem = { name: string; value: number };
type Charts = { status?: ChartItem[]; status_details?: ChartItem[]; technicians?: ChartItem[]; top_categories?: ChartItem[]; monthly?: { Period: string; total: number; sla: number }[]; request_type_stacked?: { categories: string[]; series: { name: string; data: number[] }[] } };
type Requests = { rows: Record<string, string | number>[]; total: number };

const labels: Record<string, string> = { years: 'سال', months: 'ماه', statuses: 'وضعیت', request_types: 'نوع درخواست', priorities: 'اولویت', tech_groups: 'گروه مسئول', techs: 'کارشناس', categories: 'دسته‌بندی' };
const selectToFilter: Record<string, keyof Filters> = { years: 'years', months: 'months', statuses: 'statuses', request_types: 'request_types', priorities: 'priorities', tech_groups: 'tech_groups', techs: 'techs', categories: 'categories' };
const kpiNames: Record<string, string> = { total: 'کل درخواست‌ها', open: 'باز / در جریان', closed: 'رسیدگی‌شده', rejected: 'ردشده', sla_violated: 'دارای نقض SLA', violation_hours_sum: 'مجموع ساعات نقض', elapsed_hours_avg: 'میانگین ساعت سپری‌شده', high_urgent: 'زیاد و اضطراری' };

function FilterSelect({ label, options, value, onChange }: { label: string; options: OptionValue[]; value: OptionValue[]; onChange: (value: OptionValue[]) => void }) {
  const [query, setQuery] = useState('');
  const searchable = options.length > 10 && label !== 'ماه';
  const visibleOptions = useMemo(() => {
    const normalizedQuery = query.trim().toLocaleLowerCase('fa-IR');
    return normalizedQuery ? options.filter((option) => String(option).toLocaleLowerCase('fa-IR').includes(normalizedQuery)) : options;
  }, [options, query]);

  return <label className="filter-control">
    <span>{label}</span>
    {searchable && <input aria-label={`جستجوی ${label}`} className="filter-search" type="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder={`جستجوی ${label}...`} />}
    <select multiple size={Math.min(6, Math.max(3, visibleOptions.length))} value={value.map(String)} onChange={(event) => {
      const selected = Array.from(event.target.selectedOptions).map((option) => {
        const matched = options.find((item) => String(item) === option.value);
        return matched ?? option.value;
      });
      onChange(selected);
    }}>
      {visibleOptions.map((option) => <option key={String(option)} value={String(option)}>{String(option)}</option>)}
    </select>
    {searchable && <small>{visibleOptions.length} از {options.length} گزینه</small>}
  </label>;
}

export default function App() {
  const [filters, setFilters] = useState<Filters>(emptyFilters);
  const [options, setOptions] = useState<Options>({});
  const [kpis, setKpis] = useState<Record<string, number>>({});
  const [charts, setCharts] = useState<Charts>({});
  const [requests, setRequests] = useState<Requests>({ rows: [], total: 0 });
  const [drill, setDrill] = useState<'main' | 'details'>('main');
  const [search, setSearch] = useState('');
  const [refreshKey, setRefreshKey] = useState(0);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isDark, setIsDark] = useState(() => localStorage.getItem('dashboard-theme') === 'dark');
  const [error, setError] = useState('');

  useEffect(() => {
    document.documentElement.dataset.theme = isDark ? 'dark' : 'light';
    localStorage.setItem('dashboard-theme', isDark ? 'dark' : 'light');
  }, [isDark]);

  useEffect(() => {
    api.get<Options>('/filters/options').then((response) => setOptions(response.data)).catch(() => setError('دریافت گزینه‌های فیلتر ناموفق بود.'));
  }, [refreshKey]);

  useEffect(() => {
    let active = true;
    setIsRefreshing(true);
    setError('');
    Promise.all([
      api.post<Record<string, number>>('/dashboard/kpis', filters),
      api.post<Charts>('/dashboard/charts', filters),
      api.post<Requests>('/requests/search', { ...filters, page: 1, page_size: 20, search }),
    ]).then(([kpiResponse, chartResponse, requestResponse]) => {
      if (!active) return;
      setKpis(kpiResponse.data);
      setCharts(chartResponse.data);
      setRequests(requestResponse.data);
    }).catch(() => active && setError('ارتباط با سرویس داده برقرار نشد.')).finally(() => active && setIsRefreshing(false));
    return () => { active = false; };
  }, [filters, search, refreshKey]);

  const update = (key: keyof Filters, values: Filters[keyof Filters]) => setFilters((current) => ({ ...current, [key]: values }));
  const technicianChartWidth = Math.max(820, (charts.technicians?.length ?? 0) * 62);
  const donutData = drill === 'main' ? charts.status : charts.status_details;
  const chartText = isDark ? '#e7edf8' : '#334155';
  const chartLine = isDark ? '#46556d' : '#cbd5e1';
  const chartAxis = { axisLabel: { color: chartText }, axisLine: { lineStyle: { color: chartLine } }, splitLine: { lineStyle: { color: chartLine, opacity: isDark ? 0.45 : 0.65 } } };

  return <main dir="rtl">
    <header>
      <div><b>داشبورد پایش درخواست‌ها</b><small>منبع داده: Excel · به‌روزرسانی خودکار هنگام تغییر فایل</small></div>
      <div className="header-actions">
        <button className="secondary" onClick={() => setIsDark((current) => !current)}>{isDark ? 'حالت روشن' : 'حالت تیره'}</button>
        <button className="secondary" disabled={isRefreshing} onClick={() => setRefreshKey((current) => current + 1)}>بروزرسانی داده‌ها</button>
        <button onClick={() => setFilters(emptyFilters)}>پاک‌کردن فیلترها</button>
      </div>
    </header>
    <section className="layout">
      <aside>
        <div className="filter-heading"><h3>فیلترها</h3><span>برای انتخاب چند گزینه، `Ctrl` را نگه دارید.</span></div>
        {Object.keys(labels).map((key) => <FilterSelect key={key} label={labels[key]} options={options[key] || []} value={filters[selectToFilter[key]] as OptionValue[]} onChange={(values) => update(selectToFilter[key], values as never)} />)}
        <label className="switch"><input type="checkbox" checked={filters.only_open} onChange={(event) => update('only_open', event.target.checked)} /> فقط درخواست‌های باز</label>
        <label className="switch"><input type="checkbox" checked={filters.only_sla_violated} onChange={(event) => update('only_sla_violated', event.target.checked)} /> فقط نقض SLA</label>
      </aside>
      <div className="content">
        {error && <div className="alert">{error}</div>}
        <section className="kpis">{Object.entries(kpis).map(([key, value]) => <article key={key}><span>{kpiNames[key]}</span><strong>{Number(value || 0).toLocaleString('fa-IR')}</strong></article>)}</section>
        <section className="charts">
          <article><div className="chart-title">وضعیت درخواست‌ها <button onClick={() => setDrill(drill === 'main' ? 'details' : 'main')}>{drill === 'main' ? 'نمایش جزئیات' : 'بازگشت'}</button></div><ReactECharts style={{ height: 300 }} option={{ textStyle: { color: chartText }, tooltip: { trigger: 'item' }, legend: { bottom: 0, textStyle: { color: chartText } }, series: [{ type: 'pie', radius: ['45%', '72%'], data: donutData || [], label: { color: chartText, formatter: '{b}: {c}' } }] }} onEvents={{ click: (params: { name: string }) => { if (drill === 'main' && params.name === 'باز / در جریان') setDrill('details'); } }} /></article>
          <article><div className="chart-title">نوع درخواست بر اساس وضعیت</div><ReactECharts style={{ height: 300 }} option={{ textStyle: { color: chartText }, tooltip: { trigger: 'axis' }, legend: { bottom: 0, textStyle: { color: chartText } }, xAxis: { type: 'category', data: charts.request_type_stacked?.categories || [], ...chartAxis }, yAxis: { type: 'value', ...chartAxis }, series: (charts.request_type_stacked?.series || []).map((series) => ({ ...series, type: 'bar', stack: 'all' })) }} /></article>
        </section>
        <section className="charts">
          <article><div className="chart-title">روند ماهانه</div><ReactECharts style={{ height: 300 }} option={{ textStyle: { color: chartText }, tooltip: { trigger: 'axis' }, legend: { bottom: 0, textStyle: { color: chartText } }, xAxis: { type: 'category', data: (charts.monthly || []).map((item) => item.Period), ...chartAxis }, yAxis: { type: 'value', ...chartAxis }, series: [{ name: 'کل', type: 'line', smooth: true, data: (charts.monthly || []).map((item) => item.total) }, { name: 'نقض SLA', type: 'line', smooth: true, data: (charts.monthly || []).map((item) => item.sla) }] }} /></article>
          <article><div className="chart-title">۱۰ دسته‌بندی پرتکرار</div><ReactECharts style={{ height: 300 }} option={{ textStyle: { color: chartText }, xAxis: { type: 'value', ...chartAxis }, yAxis: { type: 'category', data: (charts.top_categories || []).map((item) => item.name), axisLabel: { color: chartText, width: 160, overflow: 'truncate' }, axisLine: { lineStyle: { color: chartLine } } }, series: [{ type: 'bar', data: (charts.top_categories || []).map((item) => item.value), itemStyle: { color: '#4f46e5' } }] }} /></article>
        </section>
        <section className="chart-card technicians-card"><div className="chart-title">تعداد درخواست‌ها به تفکیک کارشناس</div><div className="chart-scroll"><ReactECharts style={{ height: 350, width: technicianChartWidth }} option={{ textStyle: { color: chartText }, tooltip: { trigger: 'axis' }, grid: { left: 48, right: 20, top: 32, bottom: 105 }, xAxis: { type: 'category', data: (charts.technicians || []).map((item) => item.name), axisLabel: { color: chartText, rotate: 48, interval: 0 }, axisLine: { lineStyle: { color: chartLine } } }, yAxis: { type: 'value', minInterval: 1, ...chartAxis }, dataZoom: [{ type: 'inside' }, { type: 'slider', bottom: 22, textStyle: { color: chartText } }], series: [{ name: 'تعداد درخواست', type: 'bar', data: (charts.technicians || []).map((item) => item.value), itemStyle: { color: '#0f766e', borderRadius: [4, 4, 0, 0] } }] }} /></div></section>
        <section className="table-card"><div className="table-top"><div><h3>درخواست‌ها ({Number(requests.total || 0).toLocaleString('fa-IR')})</h3><small>{isRefreshing ? 'در حال به‌روزرسانی…' : 'نتایج با فیلترهای انتخاب‌شده'}</small></div><input placeholder="جستجو: شناسه، کارشناس، گروه..." value={search} onChange={(event) => setSearch(event.target.value)} /></div><div className="scroll"><table><thead><tr>{['ReqID', 'Yr', 'Mth', 'TechGroup', 'Tech', 'Category', 'RequestType', 'Priority', 'ReqStatus', 'Elapsed_hrs', 'Violation_hrs'].map((header) => <th key={header}>{header}</th>)}</tr></thead><tbody>{requests.rows.map((row) => <tr key={String(row.ReqID)}>{['ReqID', 'Yr', 'Mth', 'TechGroup', 'Tech', 'Category', 'RequestType', 'Priority', 'ReqStatus', 'Elapsed_hrs', 'Violation_hrs'].map((column) => <td key={column}>{['Priority', 'ReqStatus'].includes(column) ? <span className="badge">{row[column]}</span> : row[column]}</td>)}</tr>)}</tbody></table></div></section>
      </div>
    </section>
  </main>;
}
