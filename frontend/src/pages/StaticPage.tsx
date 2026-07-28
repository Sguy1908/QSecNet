export function StaticPage({ title }: { title: string }) {
  const content: Record<string, string> = {
    Home: "Model, attack, and harden quantum communication networks from a single security workspace.",
    "Network Builder": "Create a connected topology using endpoint, repeater, and trusted-relay nodes. Persist it through the Topologies API.",
    "Attack Analysis": "Run intercept-resend, noise, loss, node-failure, and link-failure scenarios against BB84 transmission.",
    "Security Report": "Calculate QBER, fidelity, key-rate, reliability, connectivity, and prioritized remediations.",
    Settings: "Configure the API address and IBM Quantum Runtime credentials through deployment environment variables.",
    About: "QSecNet is an open-source research platform for quantum-network threat assessment."
  };
  return <section><header><p className="eyebrow">QSECNET</p><h2>{title}</h2><p>{content[title]}</p></header><div className="empty">Use the sidebar to explore the QSecNet security workflow.</div></section>;
}
