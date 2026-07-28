import { useState } from "react";
import { Sidebar, type Page } from "./components/Sidebar";
import { SimulationPage } from "./pages/SimulationPage";
import { StaticPage } from "./pages/StaticPage";
export default function App() { const [page, setPage] = useState<Page>("Home"); return <main><Sidebar active={page} onSelect={setPage}/><div className="content">{page === "Simulation" ? <SimulationPage/> : <StaticPage title={page}/>}</div></main>; }
