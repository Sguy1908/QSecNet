import type { AttackKind, SimulationResponse } from "../types/api";

const baseUrl = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";

export async function runBb84(rounds: number, attack?: AttackKind): Promise<SimulationResponse> {
  const attacks = attack ? [{ kind: attack }] : [];
  const response = await fetch(`${baseUrl}/simulations/bb84`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ rounds, seed: 42, attacks })
  });
  if (!response.ok) throw new Error(`Simulation failed: ${await response.text()}`);
  return response.json() as Promise<SimulationResponse>;
}
