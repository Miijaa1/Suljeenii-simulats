import { useState } from "react";

const inputCls = "w-full rounded border border-gray-300 px-2 py-1 text-sm";
const btnCls = "rounded px-3 py-1 text-sm font-medium text-white disabled:opacity-50";

// Статистикийн нэг мөр
function Row({ label, value }) {
  return (
    <div className="flex justify-between border-b border-gray-100 py-1 text-sm">
      <span className="text-gray-600">{label}</span>
      <span className="font-medium">{value}</span>
    </div>
  );
}

export default function SidePanel({ data, topos, topology, onSelect, cut, onRestore, error, api, reload }) {
  const [node, setNode] = useState({ id: "", name: "", lat: "", lon: "" });
  const [edge, setEdge] = useState({ source: "", target: "", km: "" });
  const [msg, setMsg] = useState("");

  const nodes = data ? data.nodes : [];
  const nameOf = (id) => (nodes.find((n) => n.id === id) || { name: id }).name;
  const t = data && data.topologies[topology];

  // [FR-1.2] Засварын хүсэлт илгээж, амжилттай бол топологиудыг дахин татна
  async function edit(path, method, body) {
    try {
      await api(path, method, body);
      setMsg("✅ Амжилттай");
      await reload();
    } catch (e) {
      setMsg("❌ " + e.message);
    }
  }

  // [FR-3.1, FR-3.2] Таслалтын үр дүнгийн мессеж
  function cutMessage() {
    const { result } = cut;
    const lines = [];
    if (result.connected) lines.push("✅ Сүлжээ холбоотой хэвээр байна.");
    else lines.push("❌ Сүлжээ салсан. Тусгаарлагдсан хотууд: " + result.isolated.map(nameOf).join(", "));
    if (result.reroute) {
      const r = result.reroute;
      lines.push(`Нөөц зам: ${r.path.map(nameOf).join(" → ")}`);
      lines.push(`${r.km} км, RTT ${r.rtt_ms} ms`);
    }
    return lines;
  }

  return (
    <aside className="h-full w-96 shrink-0 space-y-4 overflow-y-auto border-r border-gray-300 bg-white p-4">
      <h1 className="text-lg font-bold">Монгол улсын шилэн кабелийн сүлжээ</h1>

      {error && <div className="rounded bg-red-100 p-2 text-sm text-red-800">{error}</div>}
      {data && data.warnings.map((w) => (
        <div key={w} className="rounded bg-yellow-100 p-2 text-sm text-yellow-800">⚠️ {w}</div>
      ))}

      {/* [FR-4.1] Топологи солих товчнууд */}
      <div className="flex gap-2">
        {Object.entries(topos).map(([key, { label, color }]) => (
          <button
            key={key}
            className={btnCls + " flex-1 " + (key === topology ? "ring-2 ring-offset-2" : "opacity-70")}
            style={{ backgroundColor: color, "--tw-ring-color": color }}
            onClick={() => onSelect(key)}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Статистик */}
      {t && (
        <section>
          <h2 className="mb-1 font-semibold">Статистик</h2>
          <Row label="Нийт урт" value={`${t.stats.total_km.toLocaleString()} км`} />
          <Row label="Ирмэгийн тоо" value={t.stats.edge_count} />
          <Row label="Гүүрийн тоо" value={t.stats.bridge_count} />
          <Row label="1-Fault Tolerant" value={t.stats.fault_tolerant ? "✅" : "❌"} />
          {t.stats.farthest && (
            <Row
              label={`Хамгийн их RTT (${nameOf(t.stats.farthest.source)} – ${nameOf(t.stats.farthest.target)})`}
              value={`${t.stats.max_rtt_ms} ms ${t.stats.rtt_ok ? "✅ < 50" : "❌ ≥ 50"}`}
            />
          )}
          {t.extra_percent !== undefined && <Row label="MST-ээс нэмэлт кабель" value={`+${t.extra_percent}%`} />}
        </section>
      )}

      {/* Таслалтын үр дүн */}
      <section>
        <h2 className="mb-1 font-semibold">Кабель таслах симуляци</h2>
        {cut ? (
          <div className="space-y-1 rounded bg-gray-100 p-2 text-sm">
            <div className="font-medium">Тасарсан: {nameOf(cut.source)} – {nameOf(cut.target)}</div>
            {cutMessage().map((line) => <div key={line}>{line}</div>)}
            <button className={btnCls + " mt-1 bg-gray-800"} onClick={onRestore}>Сэргээх</button>
          </div>
        ) : (
          <p className="text-sm text-gray-500">Газрын зураг дээр кабель дээр дарж «Таслах» товчийг ашиглана уу.</p>
        )}
      </section>

      {/* [FR-1.2] Засварын form */}
      <section className="space-y-2">
        <h2 className="font-semibold">Засвар</h2>
        {msg && <div className="text-sm">{msg}</div>}

        <div className="space-y-1 rounded border border-gray-200 p-2">
          <div className="text-sm font-medium">Зангилаа</div>
          <input className={inputCls} placeholder="id (латин, жишээ: test_city)" value={node.id}
            onChange={(e) => setNode({ ...node, id: e.target.value })} />
          <input className={inputCls} placeholder="Нэр" value={node.name}
            onChange={(e) => setNode({ ...node, name: e.target.value })} />
          <div className="flex gap-2">
            <input className={inputCls} placeholder="lat" value={node.lat}
              onChange={(e) => setNode({ ...node, lat: e.target.value })} />
            <input className={inputCls} placeholder="lon" value={node.lon}
              onChange={(e) => setNode({ ...node, lon: e.target.value })} />
          </div>
          <div className="flex gap-2">
            <button className={btnCls + " bg-blue-600"} onClick={() => edit("/api/nodes", "POST", node)}>
              Нэмэх / засах
            </button>
            <button className={btnCls + " bg-red-600"} onClick={() => edit(`/api/nodes/${node.id}`, "DELETE")}>
              Устгах
            </button>
          </div>
        </div>

        <div className="space-y-1 rounded border border-gray-200 p-2">
          <div className="text-sm font-medium">Кабель (ирмэг)</div>
          {["source", "target"].map((field) => (
            <select key={field} className={inputCls} value={edge[field]}
              onChange={(e) => setEdge({ ...edge, [field]: e.target.value })}>
              <option value="">{field === "source" ? "Эхлэх хот" : "Төгсөх хот"}</option>
              {nodes.map((n) => <option key={n.id} value={n.id}>{n.name}</option>)}
            </select>
          ))}
          <input className={inputCls} placeholder="Урт (км)" value={edge.km}
            onChange={(e) => setEdge({ ...edge, km: e.target.value })} />
          <div className="flex gap-2">
            <button className={btnCls + " bg-blue-600"} onClick={() => edit("/api/edges", "POST", edge)}>
              Нэмэх / засах
            </button>
            <button className={btnCls + " bg-red-600"}
              onClick={() => edit(`/api/edges/${edge.source}/${edge.target}`, "DELETE")}>
              Устгах
            </button>
          </div>
        </div>
      </section>
    </aside>
  );
}
