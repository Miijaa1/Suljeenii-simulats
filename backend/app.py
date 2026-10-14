"""Flask REST API (port 5001). Граф санах ойд хадгалагдаж, өөрчлөлт бүрийн дараа дахин тооцогдоно."""
import math
import re

from flask import Flask, jsonify, request
from flask_cors import CORS

from data import EDGES, NODES
from graph_engine import (build_full_mesh, build_graph, build_mst,
                          make_two_edge_connected, simulate_cut, stats)

app = Flask(__name__)
CORS(app)

# Санах ойн өгөгдөл: зангилаа {id: {...}}, ирмэг {(a, b) эрэмбэлсэн: км}
nodes = {n["id"]: dict(n) for n in NODES}
edges = {tuple(sorted((a, b))): km for a, b, km in EDGES}
# Тооцоолсон үр дүн: graphs (nx.Graph), topologies (JSON), warnings
net = {"graphs": {}, "topologies": {}, "warnings": []}


def edge_list(H):
    """nx.Graph-ийн ирмэгүүдийг JSON хэлбэрт хөрвүүлнэ."""
    return [{"source": u, "target": v, "km": d["weight"]} for u, v, d in H.edges(data=True)]


def rebuild():
    """[FR-1.2] Өөрчлөлт бүрийн дараа MST / 2-Edge / Full Mesh-ийг дахин тооцно."""
    G = build_graph(nodes, edges)
    mst = build_mst(G)
    two, added, warning = make_two_edge_connected(G, mst)
    graphs = {"mst": mst, "two_edge": two, "full_mesh": build_full_mesh(G)}

    topologies = {name: {"edges": edge_list(H), "stats": stats(H)} for name, H in graphs.items()}
    mst_km = topologies["mst"]["stats"]["total_km"]
    two_km = topologies["two_edge"]["stats"]["total_km"]
    topologies["two_edge"]["added_edges"] = [{"source": u, "target": v, "km": km} for u, v, km in added]
    topologies["two_edge"]["extra_percent"] = round((two_km - mst_km) / mst_km * 100, 1) if mst_km else 0

    warnings = []
    if len(G) == 0:
        warnings.append("Зангилаа байхгүй байна.")
    elif not topologies["full_mesh"]["stats"]["connected"]:
        warnings.append("Замын граф салсан байна: зарим хотууд бусадтайгаа холбогдохгүй байна.")
    if warning:
        warnings.append(warning)
    net.update(graphs=graphs, topologies=topologies, warnings=warnings)


def error(message, code=400):
    """Ойлгомжтой алдааны хариу."""
    return jsonify({"error": message}), code


def body():
    """JSON body-г dict болгон авна (буруу бол хоосон dict)."""
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def parse_number(value, low, high):
    """Тоо болгож хөрвүүлээд [low, high] завсарт эсэхийг шалгана, буруу бол None."""
    try:
        x = float(value)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) and low <= x <= high else None


@app.get("/api/network/topologies")
def get_topologies():
    """Бүх топологи, статистик, warning-ийг буцаана."""
    return jsonify({"nodes": list(nodes.values()), "topologies": net["topologies"], "warnings": net["warnings"]})


@app.post("/api/network/simulate-cut")
def post_simulate_cut():
    """[FR-3.1, FR-3.2] Сонгосон топологийн нэг кабелийг таслах симуляц."""
    d = body()
    H = net["graphs"].get(d.get("topology"))
    if H is None:
        return error("topology нь mst, two_edge, full_mesh-ийн нэг байх ёстой.")
    u, v = str(d.get("source")), str(d.get("target"))
    if not H.has_edge(u, v):
        return error("Энэ топологид %s – %s кабель олдсонгүй." % (u, v), 404)
    return jsonify(simulate_cut(H, u, v))


@app.post("/api/nodes")
def save_node():
    """[FR-1.2] Зангилаа нэмэх (id шинэ бол) эсвэл засах (id байгаа бол)."""
    d = body()
    node_id, name = str(d.get("id", "")).strip(), str(d.get("name", "")).strip()
    lat, lon = parse_number(d.get("lat"), -90, 90), parse_number(d.get("lon"), -180, 180)
    if not re.fullmatch(r"[a-z0-9_]+", node_id):
        return error("id нь латин жижиг үсэг, тоо, '_'-аас тогтсон байх ёстой.")
    if not name:
        return error("Хотын нэр хоосон байж болохгүй.")
    if lat is None or lon is None:
        return error("lat [-90, 90], lon [-180, 180] завсарт тоо байх ёстой.")
    created = node_id not in nodes
    nodes[node_id] = {"id": node_id, "name": name, "lat": lat, "lon": lon}
    rebuild()
    return jsonify({"ok": True, "created": created}), 201 if created else 200


@app.delete("/api/nodes/<node_id>")
def delete_node(node_id):
    """[FR-1.2] Зангилаа ба түүнд холбогдсон бүх ирмэгийг устгана."""
    if node_id not in nodes:
        return error("Зангилаа '%s' олдсонгүй." % node_id, 404)
    del nodes[node_id]
    for key in [k for k in edges if node_id in k]:
        del edges[key]
    rebuild()
    return jsonify({"ok": True})


@app.post("/api/edges")
def save_edge():
    """[FR-1.2] Ирмэг (кабелийн трасс) нэмэх эсвэл уртыг нь засах."""
    d = body()
    a, b = str(d.get("source", "")), str(d.get("target", ""))
    km = parse_number(d.get("km"), 0, 100000)
    if a == b:
        return error("Эхлэл ба төгсгөл өөр хот байх ёстой.")
    for n in (a, b):
        if n not in nodes:
            return error("Зангилаа '%s' олдсонгүй." % n, 404)
    if not km:  # None эсвэл 0
        return error("km нь 0-ээс их тоо байх ёстой.")
    key = tuple(sorted((a, b)))
    created = key not in edges
    edges[key] = km
    rebuild()
    return jsonify({"ok": True, "created": created}), 201 if created else 200


@app.delete("/api/edges/<source>/<target>")
def delete_edge(source, target):
    """[FR-1.2] Ирмэг устгана."""
    key = tuple(sorted((source, target)))
    if key not in edges:
        return error("Кабель %s – %s олдсонгүй." % (source, target), 404)
    del edges[key]
    rebuild()
    return jsonify({"ok": True})


def print_summary():
    """Асахад 3 топологийг харьцуулсан хүснэгтийг console-д хэвлэнэ (тайланд зориулав)."""
    names = {"mst": "MST", "two_edge": "2-Edge", "full_mesh": "Full Mesh"}
    print("\n%-10s | %10s | %6s | %5s | %12s" % ("Топологи", "Нийт км", "Ирмэг", "Гүүр", "Max RTT (ms)"))
    print("-" * 56)
    for key, t in net["topologies"].items():
        s = t["stats"]
        print("%-10s | %10.1f | %6d | %5d | %12.2f" %
              (names[key], s["total_km"], s["edge_count"], s["bridge_count"], s["max_rtt_ms"]))
    for w in net["warnings"]:
        print("WARNING:", w)
    print()


rebuild()

if __name__ == "__main__":
    print_summary()
    app.run(host="127.0.0.1", port=5001)
