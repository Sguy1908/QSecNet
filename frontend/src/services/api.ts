import type { Project, Recommendation, SecurityReport, Simulation } from "../types/api";

const API_BASE = import.meta.env.VITE_API_BASE ?? "";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });
  if (!response.ok) {
    const detail = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(detail.detail ?? "Request failed");
  }
  return response.json() as Promise<T>;
}

export const api = {
  projects: () => request<Project[]>("/api/v1/projects"),
  createProject: (name: string) =>
    request<Project>("/api/v1/projects", {
      method: "POST",
      body: JSON.stringify({ name }),
    }),
  createTopology: (projectId: string, name: string) =>
    request<{ id: string; name: string; project_id: string }>(
      `/api/v1/projects/${projectId}/topologies`,
      { method: "POST", body: JSON.stringify({ name }) },
    ),
  createNode: (topologyId: string, name: string, nodeType = "repeater") =>
    request<{ id: string; name: string }>(`/api/v1/topologies/${topologyId}/nodes`, {
      method: "POST",
      body: JSON.stringify({ name, node_type: nodeType }),
    }),
  simulations: (projectId: string, bits = 256) =>
    request<Simulation>(`/api/v1/projects/${projectId}/simulations`, {
      method: "POST",
      body: JSON.stringify({ requested_bits: bits, execution_mode: "analytic" }),
    }),
  report: (simulationId: string) =>
    request<SecurityReport>(`/api/v1/simulations/${simulationId}/security-reports`, {
      method: "POST",
    }),
  recommendations: (reportId: string) =>
    request<Recommendation[]>(`/api/v1/security-reports/${reportId}/recommendations`, {
      method: "POST",
    }),
};
