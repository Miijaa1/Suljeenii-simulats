import { CircleMarker, MapContainer, Polyline, Popup, TileLayer, Tooltip } from "react-leaflet";
import "leaflet/dist/leaflet.css";

// Ирмэгийг чиглэлгүй түлхүүр болгоно (a|b == b|a)
const edgeKey = (a, b) => [a, b].sort().join("|");

export default function MapView({ nodes, topology, topologyKey, color, cut, onCut }) {
  const byId = Object.fromEntries(nodes.map((n) => [n.id, n]));
  const pos = (id) => [byId[id].lat, byId[id].lon];

  const bridgeSet = new Set(topology.stats.bridges.map((b) => edgeKey(b.source, b.target)));
  const addedSet = new Set((topology.added_edges || []).map((e) => edgeKey(e.source, e.target)));
  const cutKey = cut && edgeKey(cut.source, cut.target);
  const isolated = new Set(cut ? cut.result.isolated : []);
  const reroute = cut && cut.result.reroute ? cut.result.reroute.path : [];

  // [FR-4.1, FR-3.1] Кабелийн өнгө/зузаан: таслагдсан = саарал, гүүр = тасархай, нэмэгдсэн = бүдүүн
  function edgeStyle(e) {
    const key = edgeKey(e.source, e.target);
    if (key === cutKey) return { color: "#9ca3af", weight: 4 };
    return {
      color,
      weight: addedSet.has(key) ? 6 : topologyKey === "full_mesh" ? 2 : 3,
      opacity: topologyKey === "full_mesh" ? 0.45 : 0.9,
      dashArray: bridgeSet.has(key) ? "8 8" : undefined,
    };
  }

  return (
    <MapContainer center={[46.8, 103.0]} zoom={5} className="h-full w-full">
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {/* Кабель: Polyline + Popup (Таслах товч) */}
      {topology.edges.map((e) => (
        <Polyline
          key={`${topologyKey}-${e.source}-${e.target}`}
          positions={[pos(e.source), pos(e.target)]}
          pathOptions={edgeStyle(e)}
        >
          <Popup>
            <div className="text-sm">
              <b>{byId[e.source].name} – {byId[e.target].name}</b>
              <div>{e.km} км</div>
              <button
                className="mt-1 rounded bg-gray-800 px-2 py-1 text-white"
                onClick={() => onCut(e.source, e.target)}
              >
                Таслах
              </button>
            </div>
          </Popup>
        </Polyline>
      ))}

      {/* [FR-3.2] Нөөц зам: улбар шар */}
      {reroute.slice(1).map((id, i) => (
        <Polyline
          key={`reroute-${i}`}
          positions={[pos(reroute[i]), pos(id)]}
          pathOptions={{ color: "#f97316", weight: 6 }}
          interactive={false}
        />
      ))}

      {/* Хот: CircleMarker (салсан хот = нил ягаан). markerPane нь кабелийн дээр зурагдана */}
      {nodes.map((n) => (
        <CircleMarker
          key={n.id}
          center={[n.lat, n.lon]}
          radius={7}
          pane="markerPane"
          pathOptions={{
            color: "#111827",
            weight: 2,
            fillColor: isolated.has(n.id) ? "#7c3aed" : "#ffffff",
            fillOpacity: 1,
          }}
        >
          <Tooltip>{n.name}</Tooltip>
          <Popup>
            <div className="text-sm">
              <b>{n.name}</b>
              <div>lat: {n.lat.toFixed(4)}, lon: {n.lon.toFixed(4)}</div>
            </div>
          </Popup>
        </CircleMarker>
      ))}
    </MapContainer>
  );
}
