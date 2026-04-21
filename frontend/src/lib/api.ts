const BASE = process.env.NEXT_PUBLIC_API_URL || '';

async function fetchJSON<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${url}`, {
    headers: { 'Content-Type': 'application/json', ...init?.headers },
    ...init,
  });
  if (!res.ok) throw new Error(`API ${res.status}: ${res.statusText}`);
  return res.json();
}

// Analytics
export const getOverview = (days = 7) =>
  fetchJSON<any>(`/api/analytics/overview?days=${days}`);
export const getTrend = (days = 7) =>
  fetchJSON<any>(`/api/analytics/trend?days=${days}`);
export const getCategories = (days = 7) =>
  fetchJSON<any>(`/api/analytics/categories?days=${days}`);
export const getChannels = (days = 7) =>
  fetchJSON<any>(`/api/analytics/channels?days=${days}`);
export const getSeverityDistribution = (days = 7) =>
  fetchJSON<any>(`/api/analytics/severity-distribution?days=${days}`);

// Posts
export const queryPosts = (params: Record<string, any>) => {
  const qs = new URLSearchParams(
    Object.fromEntries(Object.entries(params).filter(([_, v]) => v != null))
  ).toString();
  return fetchJSON<any>(`/api/monitor/query?${qs}`);
};

// Incidents
export const getIncidents = (params: Record<string, any> = {}) => {
  const qs = new URLSearchParams(
    Object.fromEntries(Object.entries(params).filter(([_, v]) => v != null))
  ).toString();
  return fetchJSON<any>(`/api/incidents?${qs}`);
};
export const getIncident = (id: number) =>
  fetchJSON<any>(`/api/incidents/${id}`);
export const updateIncident = (id: number, data: any) =>
  fetchJSON<any>(`/api/incidents/${id}`, { method: 'PATCH', body: JSON.stringify(data) });

// Alerts
export const getAlerts = (params: Record<string, any> = {}) => {
  const qs = new URLSearchParams(
    Object.fromEntries(Object.entries(params).filter(([_, v]) => v != null))
  ).toString();
  return fetchJSON<any>(`/api/alerts?${qs}`);
};
export const acknowledgeAlert = (id: number) =>
  fetchJSON<any>(`/api/alerts/${id}/ack`, { method: 'POST' });

// Feedback
export const getFeedback = (params: Record<string, any> = {}) => {
  const qs = new URLSearchParams(
    Object.fromEntries(Object.entries(params).filter(([_, v]) => v != null))
  ).toString();
  return fetchJSON<any>(`/api/feedback?${qs}`);
};
export const createFeedback = (data: any) =>
  fetchJSON<any>('/api/feedback', { method: 'POST', body: JSON.stringify(data) });

// Taxonomy
export const getTaxonomyCategories = () =>
  fetchJSON<any[]>('/api/taxonomy/categories');
export const getTaxonomySubIssues = () =>
  fetchJSON<any[]>('/api/taxonomy/sub-issues');

// Crawler
export const triggerCrawl = (platform: string, lookback_hours = 24) =>
  fetchJSON<any>('/api/crawler/run', {
    method: 'POST',
    body: JSON.stringify({ platform, lookback_hours }),
  });

// Auth
export const login = (email: string, password: string) =>
  fetchJSON<any>('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
export const register = (data: any) =>
  fetchJSON<any>('/api/auth/register', { method: 'POST', body: JSON.stringify(data) });
