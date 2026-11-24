const API_BASE = '/api';

/**
 * Sends farmer query to the Multilingual AI Advisory endpoint.
 */
export async function sendChatMessage({ query, language = 'en', location = 'Pune', soil_type, soil_ph, commodity }) {
  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query,
      language,
      location,
      soil_type,
      soil_ph: soil_ph ? parseFloat(soil_ph) : null,
      commodity,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Server responded with status ${response.status}`);
  }

  return response.json();
}

/**
 * Fetches real-time weather observations and agricultural spray/irrigation advisories.
 */
export async function getWeather(location = 'Pune') {
  const response = await fetch(`${API_BASE}/weather?location=${encodeURIComponent(location)}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch weather for ${location}`);
  }
  return response.json();
}

/**
 * Fetches official APMC Mandi prices with market comparisons.
 */
export async function getMandiPrices(commodity = '', state = '') {
  const params = new URLSearchParams();
  if (commodity) params.append('commodity', commodity);
  if (state) params.append('state', state);

  const response = await fetch(`${API_BASE}/mandi?${params.toString()}`);
  if (!response.ok) {
    throw new Error('Failed to fetch Mandi price feed');
  }
  return response.json();
}

/**
 * Evaluates soil profile and generates crop suitability recommendations.
 */
export async function getSoilAdvisory(soilData) {
  const response = await fetch(`${API_BASE}/soil/advisory`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(soilData),
  });

  if (!response.ok) {
    throw new Error('Failed to generate soil advisory');
  }
  return response.json();
}

/**
 * Fetches RAG knowledge base operational status.
 */
export async function getRagStatus() {
  const response = await fetch(`${API_BASE}/rag/status`);
  if (!response.ok) {
    throw new Error('Failed to fetch RAG status');
  }
  return response.json();
}

/**
 * Checks backend health status.
 */
export async function checkBackendHealth() {
  const response = await fetch(`${API_BASE}/health`);
  if (!response.ok) {
    throw new Error('Backend offline');
  }
  return response.json();
}
