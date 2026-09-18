import axios from 'axios';
export const api = axios.create({ baseURL: 'http://127.0.0.1:8000/api' });
export type Filters = { years:number[]; months:number[]; statuses:string[]; request_types:string[]; priorities:string[]; tech_groups:string[]; techs:string[]; categories:string[]; only_sla_violated:boolean; only_open:boolean };
export const emptyFilters: Filters = { years:[],months:[],statuses:[],request_types:[],priorities:[],tech_groups:[],techs:[],categories:[],only_sla_violated:false,only_open:false };
