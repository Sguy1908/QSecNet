import { useState } from "react";
import { MetricCard } from "../components/MetricCard";
import { runBb84 } from "../services/api";
import type { AttackKind, SimulationResponse } from "../types/api";

export function SimulationPage() {
  const [result, setResult] = useState<SimulationResponse>(); const [error, setError] = useState("");
  async function run(attack?: AttackKind) { try { setError(""); setResult(await runBb84(2048, attack)); } catch (e) { setError(e instanceof Error ? e.message : "Unknown error"); } }
  return <section><header><p className="eyebrow">PROTOCOL LAB</p><h2>BB84 simulation</h2><p>Measure sifted key generation and attack-induced error rates.</p></header>
    <div className="actions"><button className="primary" onClick={() => run()}>Run ideal channel</button><button onClick={() => run("intercept_resend")}>Simulate intercept &amp; resend</button></div>
    {error && <p className="error">{error}</p>}
    {result && <div className="metrics"><MetricCard label="QBER" value={`${(result.qber * 100).toFixed(2)}%`} detail="Matched-basis error rate" /><MetricCard label="Shared key" value={`${result.key_length} bits`} detail={`Delivery ${(result.delivery_probability * 100).toFixed(1)}%`} /><MetricCard label="Success" value={`${(result.success_probability * 100).toFixed(1)}%`} detail="Sifting efficiency" /></div>}
  </section>;
}
