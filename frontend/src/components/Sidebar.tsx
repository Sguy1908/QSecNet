export type Page = "Home" | "Network Builder" | "Simulation" | "Attack Analysis" | "Security Report" | "Settings" | "About";
const pages: Page[] = ["Home", "Network Builder", "Simulation", "Attack Analysis", "Security Report", "Settings", "About"];
export function Sidebar({ active, onSelect }: { active: Page; onSelect: (page: Page) => void }) {
  return <aside><h1>QSec<span>Net</span></h1><p className="eyebrow">QUANTUM SECURITY</p><nav>{pages.map(page => <button className={page === active ? "active" : ""} key={page} onClick={() => onSelect(page)}>{page}</button>)}</nav></aside>;
}
