const API = import.meta.env.VITE_API_URL;

if (!API) {
  // Keep this loud in production builds to surface bad deploy config quickly.
  console.warn("Missing VITE_API_URL. Frontend API calls will fail.");
}

async function request(path, options = {}) {
  if (!API) {
    throw new Error("Missing VITE_API_URL in frontend environment.");
  }

  const response = await fetch(`${API}${path}`, options);
  let payload = {};

  try {
    payload = await response.json();
  } catch {
    payload = {};
  }

  if (!response.ok) {
    const detail =
      (payload && (payload.detail || payload.message)) ||
      `Request failed with status ${response.status}`;
    throw new Error(String(detail));
  }

  return payload;
}

export async function getAgents() {
  return request("/agents");
}

export async function getHistory(userId, limit = 25) {
  const params = new URLSearchParams({
    user_id: String(userId),
    limit: String(limit),
  });
  return request(`/history?${params.toString()}`);
}

export async function analyzePrompt(body) {
  return request("/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

