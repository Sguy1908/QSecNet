import { useState } from "react";
import type { Project } from "../types/api";
import { api } from "../services/api";

export function NetworkBuilderPage({ projects, onCreated }: { projects: Project[]; onCreated: () => void }) {
  const [projectId, setProjectId] = useState(projects[0]?.id ?? "");
  const [topologyName, setTopologyName] = useState("Metro quantum mesh");
  const [nodeName, setNodeName] = useState("Alice");
  const [topologyId, setTopologyId] = useState("");
  const [message, setMessage] = useState("Create a topology, then add nodes to it.");
  async function createTopology() { try { const topology = await api.createTopology(projectId, topologyName); setTopologyId(topology.id); setMessage(`Topology ${topology.name} created.`); onCreated(); } catch (error) { setMessage(error instanceof Error ? error.message : "Unable to create topology"); } }
  async function addNode() { try { await api.createNode(topologyId, nodeName); setMessage(`Node ${nodeName} added.`); setNodeName(""); } catch (error) { setMessage(error instanceof Error ? error.message : "Unable to add node"); } }
  return <section className="page-stack"><div className="page-title"><div><div className="eyebrow">TOPOLOGY DESIGNER</div><h1>Network builder</h1><p className="subtitle">Compose a persisted quantum network before running security analysis.</p></div></div><div className="builder-grid"><div className="panel form-panel"><h3>Topology configuration</h3><p>Start from a project workspace.</p><label>Project<select value={projectId} onChange={event => setProjectId(event.target.value)}>{projects.map(project => <option value={project.id} key={project.id}>{project.name}</option>)}</select></label><label>Topology name<input value={topologyName} onChange={event => setTopologyName(event.target.value)} /></label><button className="button primary" disabled={!projectId} onClick={() => void createTopology()}>Create topology</button></div><div className="panel form-panel"><h3>Network nodes</h3><p>{topologyId ? `Editing topology ${topologyId.slice(0, 8)}…` : "Create a topology to enable node management."}</p><label>Node name<input value={nodeName} onChange={event => setNodeName(event.target.value)} /></label><button className="button secondary" disabled={!topologyId || !nodeName} onClick={() => void addNode()}>Add node</button><div className="builder-message">{message}</div></div></div></section>;
}
