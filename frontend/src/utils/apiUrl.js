const API_V1_PATH = '/api/v1';

function getBaseUrl() {
  let url = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1';
  if (!url.endsWith(API_V1_PATH) && !url.endsWith(API_V1_PATH + '/')) {
    if (url.endsWith('/')) {
      url = url.slice(0, -1);
    }
    url = url + API_V1_PATH;
  }
  return url;
}

export function getApiUrl() {
  return getBaseUrl();
}

export function getWsUrl() {
  const base = getBaseUrl();
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  return base.replace(/^https?:/, protocol);
}
