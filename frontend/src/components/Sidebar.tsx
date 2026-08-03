import { Activity, FileText, Gauge, Info, Network, Radar, Settings2, ShieldCheck } from "lucide-react";

export type Page = "overview" | "builder" | "simulations" | "attacks" | "reports" | "settings" | "about";
const navigation: Array<[Page, typeof Gauge, string]> = [["overview", Gauge, "Overview"], ["builder", Network, "Network builder"], ["simulations", Radar, "Simulations"], ["attacks", ShieldCheck, "Attack analysis"], ["reports", FileText, "Security reports"]];

export function Sidebar({ activePage, onNavigate }: { activePage: Page; onNavigate: (page: Page) => void }) {
  return <aside className="sidebar"><div className="brand"><span className="brand-mark"><Activity size={17} /></span><span>QSecNet</span></div><div className="workspace-label">WORKSPACE</div><nav>{navigation.map(([page, Icon, label]) => <button className={activePage === page ? "nav-item active" : "nav-item"} key={page} onClick={() => onNavigate(page)}><Icon size={17} />{label}</button>)}</nav><div className="sidebar-bottom"><button className={activePage === "settings" ? "nav-item active" : "nav-item"} onClick={() => onNavigate("settings")}><Settings2 size={17} />Settings</button><button className={activePage === "about" ? "nav-item active" : "nav-item"} onClick={() => onNavigate("about")}><Info size={17} />About</button><div className="profile"><span className="avatar">QS</span><span><b>Research lab</b><small>Local workspace</small></span></div></div></aside>;
}
