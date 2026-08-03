import { Activity, FileText, Gauge, Network, Radar, Settings2, ShieldCheck } from "lucide-react";

const navigation = [
  [Gauge, "Overview"],
  [Network, "Network builder"],
  [Radar, "Simulations"],
  [ShieldCheck, "Attack analysis"],
  [FileText, "Security reports"],
] as const;

export function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="brand"><span className="brand-mark"><Activity size={17} /></span><span>QSecNet</span></div>
      <div className="workspace-label">WORKSPACE</div>
      <nav>{navigation.map(([Icon, label], index) => <button className={index === 0 ? "nav-item active" : "nav-item"} key={label}><Icon size={17} />{label}</button>)}</nav>
      <div className="sidebar-bottom"><button className="nav-item"><Settings2 size={17} />Settings</button><div className="profile"><span className="avatar">QS</span><span><b>Research lab</b><small>Local workspace</small></span></div></div>
    </aside>
  );
}
