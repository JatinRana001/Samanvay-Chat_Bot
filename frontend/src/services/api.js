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

let healthCheckPromise;

async function requestJson(path, options = {}) {
  const url = `${API_BASE_URL}${path}`;
  let response;
  try {
    response = await fetch(url, options);
  } catch (cause) {
    const error = new Error(
      `Could not reach the Samanvay API at ${url}. Check the backend address, CORS settings, and HTTPS configuration.`,
      { cause },
    );
    error.name = 'ApiConnectionError';
    throw error;
  }

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `Samanvay API returned HTTP ${response.status} at ${url}`);
  }

  try {
    return await response.json();
  } catch (cause) {
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
  if (!healthCheckPromise) {
    healthCheckPromise = requestJson('/api/health').catch((error) => {
      healthCheckPromise = undefined;
      throw error;
    });
  }
  return healthCheckPromise;
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

export function getIndustries() {
  return requestJson('/api/industries');
}

export function getDepartments() {
  return requestJson('/api/departments');
}

export function queryRAG(query) {
  return postJson('/api/rag/query', { query, top_k: 3 });
}
