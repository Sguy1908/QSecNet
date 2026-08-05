export interface Project {
  id: string;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface Simulation {
  id: string;
  project_id: string;
  topology_id?: string;
  protocol: string;
  status: "pending" | "running" | "completed" | "failed";
  requested_bits: number;
  configuration: Record<string, unknown>;
  result?: {
    qber: number;
    key_length: number;
    estimated_key_rate: number;
    success_probability: number;
    execution_mode: string;
  };
  error_message?: string;
}

export interface SecurityReport {
  id: string;
  simulation_id: string;
  security_score: number;
  risk_level: "low" | "medium" | "high" | "critical";
  metrics: {
    qber: number;
    average_fidelity: number;
    reliability: number;
    connectivity: number;
    weakest_link_id?: string;
    weakest_node_id?: string;
    estimated_key_rate: number;
  };
}

export interface Recommendation {
  id: string;
  report_id: string;
  title: string;
  description: string;
  priority: "low" | "medium" | "high" | "critical";
  category: string;
}
