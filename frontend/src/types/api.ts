export type AttackKind = "intercept_resend" | "channel_noise" | "photon_loss" | "node_failure" | "link_failure";

export interface SimulationResponse {
  shared_key: string; key_length: number; qber: number; success_probability: number;
  sifted_bits: number; delivery_probability: number; attacks: AttackKind[];
  affected_nodes: string[]; affected_links: [string, string][];
}
