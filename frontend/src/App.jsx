import { useEffect, useState } from "react";
import MapView from "./components/MapView";
import SidePanel from "./components/SidePanel";

const API = "http://127.0.0.1:5001";

// [FR-4.1] Топологи бүрийн нэр ба өнгө
const TOPOS = {
  mst: { label: "MST", color: "#dc2626" },
  two_edge: { label: "2-Edge", color: "#2563eb" },
  full_mesh: { label: "Full Mesh", color: "#16a34a" },
};

// Backend руу хүсэлт илгээнэ. Алдаа гарвал backend-ийн мессежтэй Error шидэнэ.
async function api(path, method = "GET", body) {
  const res = await fetch(API + path, {
    method,
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || `Алдаа ${res.status}`);
  return data;
}

export default function App() {
  const [data, setData] = useState(null); // { nodes, topologies, warnings }
  const [topology, setTopology] = useState("mst");
  const [cut, setCut] = useState(null); // { source, target, result }
  const [error, setError] = useState("");

  // Топологиудыг backend-ээс татна (засвар хийсний дараа дахин дуудна) [FR-1.2]
  function load() {
    return api("/api/network/topologies")
      .then((d) => {
        setData(d);
        setCut(null);
        setError("");
      })
      .catch((e) => setError(`Backend-тэй холбогдож чадсангүй (${API}): ${e.message}`));
  }

  // Эхний удаа ачаалахад (setState-ийг callback дотор дуудахын тулд .then ашиглав)
  useEffect(() => {
    api("/api/network/topologies")
      .then(setData)
      .catch((e) => setError(`Backend-тэй холбогдож чадсангүй (${API}): ${e.message}`));
  }, []);

  // [FR-3.1, FR-3.2] Кабелийг таслах симуляци
  async function cutEdge(source, target) {
    try {
      const result = await api("/api/network/simulate-cut", "POST", { topology, source, target });
      setCut({ source, target, result });
    } catch (e) {
      setError(e.message);
    }
  }

  // [FR-4.1] Топологи солих үед таслалтыг цэвэрлэнэ
  function selectTopology(key) {
    setTopology(key);
    setCut(null);
  }

  return (
    <div className="flex h-full">
      <SidePanel
        data={data}
        topos={TOPOS}
        topology={topology}
        onSelect={selectTopology}
        cut={cut}
        onRestore={() => setCut(null)}
        error={error}
        api={api}
        reload={load}
      />
      <div className="flex-1">
        {data && (
          <MapView
            nodes={data.nodes}
            topology={data.topologies[topology]}
            topologyKey={topology}
            color={TOPOS[topology].color}
            cut={cut}
            onCut={cutEdge}
          />
        )}
      </div>
    </div>
  );
}
