import { useCallback, useEffect, useState } from "react";
import type { Project, Recommendation, SecurityReport, Simulation } from "../types/api";
import { api } from "../services/api";

export function useDashboard() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [simulation, setSimulation] = useState<Simulation>();
  const [report, setReport] = useState<SecurityReport>();
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      setProjects(await api.projects());
      setError(undefined);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to reach QSecNet API");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => void refresh(), [refresh]);

  const runAssessment = useCallback(async (projectId: string) => {
    setLoading(true);
    try {
      const nextSimulation = await api.simulations(projectId);
      const nextReport = await api.report(nextSimulation.id);
      const nextRecommendations = await api.recommendations(nextReport.id);
      setSimulation(nextSimulation);
      setReport(nextReport);
      setRecommendations(nextRecommendations);
      setError(undefined);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Assessment failed");
    } finally {
      setLoading(false);
    }
  }, []);

  return { projects, simulation, report, recommendations, loading, error, refresh, runAssessment };
}
