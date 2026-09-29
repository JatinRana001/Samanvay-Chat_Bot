const configuredApiBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim();
export const API_BASE_URL = (configuredApiBaseUrl || (
  import.meta.env.DEV ? 'http://127.0.0.1:8000' : window.location.origin
)).replace(/\/+$/, '');

if (import.meta.env.PROD && !configuredApiBaseUrl) {
  console.error(
    '[Samanvay] VITE_API_BASE_URL is unset in this production build. '
    + `Requests are using the frontend origin (${API_BASE_URL}); configure the HTTPS FastAPI origin and rebuild.`
  );
}

async function requestJson(path, options = {}) {
  const url = `${API_BASE_URL}${path}`;
  let response;
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 30000);
  try {
    response = await fetch(url, { ...options, signal: controller.signal });
  } catch (cause) {
    clearTimeout(timeout);
    const error = new Error(
      cause.name === 'AbortError'
        ? 'The Samanvay API request timed out after 30 seconds.'
        : `Network or CORS error while reaching the Samanvay API at ${url}. Check the backend address and allowed origins.`,
      { cause },
    );
    error.name = 'ApiConnectionError';
    throw error;
  }
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    const detail = typeof body.detail === 'string'
      ? body.detail
      : (body.detail ? JSON.stringify(body.detail) : (body.database === 'error' ? 'Backend database unreachable' : JSON.stringify(body)));
    const error = new Error(`HTTP ${response.status}: ${detail || `Request failed at ${url}`}`);
    error.status = response.status;
    clearTimeout(timeout);
    throw error;
  }

  try {
    const result = await response.json();
    clearTimeout(timeout);
    return result;
  } catch (cause) {
    clearTimeout(timeout);
    if (cause.name === 'AbortError') {
      throw new Error('The Samanvay API request timed out after 30 seconds.', { cause });
    }
    throw new Error(`Samanvay API returned an invalid JSON response at ${url}`, { cause });
  }
}

function postJson(path, body) {
  return requestJson(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
}

export function checkApiHealth() {
  return requestJson('/api/health');
}

export function sendChatMessage(sessionId, message) {
  return postJson('/api/chat', { session_id: sessionId, message });
}

export function sendWebsiteHelp(message) {
  return postJson('/api/website-help', { message });
}

export function recommendApprovals(profile) {
  return postJson('/api/recommend-approvals', profile);
}

export function recommendApprovalsBySession(sessionId) {
  return requestJson(`/api/recommend-approvals/by-session/${encodeURIComponent(sessionId)}`);
}

export function getIndustries() {
  return requestJson('/api/industries');
}

export function getDepartments() {
  return requestJson('/api/departments');
}

export function queryRAG(query) {
  return postJson('/api/rag/query', { query, top_k: 3 });
}
