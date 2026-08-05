import { AlertTriangle } from "lucide-react";
import { useState } from "react";
import { Sidebar, type Page } from "./components/Sidebar";
import { useDashboard } from "./hooks/useDashboard";
import { HomePage } from "./pages/HomePage";
import { NetworkBuilderPage } from "./pages/NetworkBuilderPage";
import { ReportsPage } from "./pages/ReportsPage";
import { SimulationPage } from "./pages/SimulationPage";
import { StaticPage } from "./pages/StaticPage";
import { api } from "./services/api";

function App() {
  const dashboard = useDashboard();
  const [activePage, setActivePage] = useState<Page>("overview");
  async function createWorkspace() {
    try {
      const project = await api.createProject(`Network study ${new Date().toLocaleDateString()}`);
      await dashboard.refresh();
      await dashboard.runAssessment(project.id);
    } catch {
      // Hook owns and displays request errors.
    }
  }
  const content = activePage === "overview" ? <HomePage {...dashboard} onCreate={() => void createWorkspace()} onAssess={(id) => void dashboard.runAssessment(id)} onRefresh={() => void dashboard.refresh()} /> : activePage === "builder" ? <NetworkBuilderPage projects={dashboard.projects} onCreated={() => void dashboard.refresh()} /> : activePage === "simulations" ? <SimulationPage projects={dashboard.projects} simulation={dashboard.simulation} report={dashboard.report} onAssess={(id) => void dashboard.runAssessment(id)} /> : activePage === "reports" ? <ReportsPage report={dashboard.report} recommendations={dashboard.recommendations} /> : <StaticPage kind={activePage === "settings" ? "settings" : activePage === "attacks" ? "attacks" : "about"} />;
  return <div className="app-shell"><Sidebar activePage={activePage} onNavigate={setActivePage} /><main className="main-content">{dashboard.error && <div className="error-banner"><AlertTriangle size={17} />{dashboard.error}<button onClick={() => void dashboard.refresh()}>Retry</button></div>}{content}</main></div>;
}

export default App;
