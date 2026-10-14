"""Графын алгоритмууд: MST, гүүр (Tarjan), 2-edge-connected, Full Mesh, статистик, таслалт."""
from itertools import combinations

import networkx as nx

LIGHT_KM_PER_MS = 200  # гэрэл шилэн кабельд ≈ 200 км/мс
RTT_LIMIT_MS = 50      # зөвшөөрөгдөх дээд RTT


def rtt_ms(km):
    """RTT(ms) = 2 × зам_км / 200."""
    return round(2 * km / LIGHT_KM_PER_MS, 2)


def build_graph(nodes, edges):
    """[FR-1.1] Боломжит бүх трасс G: чиглэлгүй, жигнэсэн (weight = км).

    nodes: {id: {...}}, edges: {(эх, төгсгөл): км}
    """
    G = nx.Graph()
    G.add_nodes_from(nodes)
    for (a, b), km in edges.items():
        G.add_edge(a, b, weight=km)
    return G


def build_mst(G):
    """[FR-2.1] Prim-ийн алгоритмаар хамгийн бага жинтэй өргөн мод (салсан бол ойн мод)."""
    return nx.minimum_spanning_tree(G, algorithm="prim", weight="weight")


def find_bridges(H):
    """[FR-2.2] Tarjan-ий алгоритм: DFS-ээр disc/low тооцоод low[v] > disc[u] бол (u,v) гүүр."""
    disc, low, bridges = {}, {}, []
    timer = [0]

    def dfs(u, parent):
        timer[0] += 1
        disc[u] = low[u] = timer[0]
        for v in H[u]:
            if v == parent:          # ирмэг давхардахгүй тул эцэг рүү буцахыг алгасна
                continue
            if v in disc:            # буцах ирмэг (back edge)
                low[u] = min(low[u], disc[v])
            else:
                dfs(v, u)
                low[u] = min(low[u], low[v])
                if low[v] > disc[u]:  # v-ийн дэд мод u-аас дээш гарч чадахгүй → гүүр
                    bridges.append((u, v))

    for start in H.nodes:            # салсан граф байж болох тул бүх хэсгийг гүйнэ
        if start not in disc:
            dfs(start, None)
    return bridges


def make_two_edge_connected(G, mst):
    """[FR-2.3] MST-д G-ийн ирмэг нэмж гүүрийг арилгана (greedy).

    Нэмэх ирмэг бүрийг түр нэмээд (арилсан гүүр / км) харьцааг тооцож, хамгийн ихийг нь авна.
    Буцаах: (2-edge граф, нэмсэн ирмэгүүд [(u, v, км)], warning эсвэл None)
    """
    H = mst.copy()
    added, warning = [], None
    while True:
        bridges = find_bridges(H)
        if not bridges:
            break
        best, best_ratio = None, 0
        for u, v, data in G.edges(data=True):
            if H.has_edge(u, v):
                continue
            H.add_edge(u, v, weight=data["weight"])           # түр нэмнэ
            removed = len(bridges) - len(find_bridges(H))
            H.remove_edge(u, v)                                # буцааж хасна
            ratio = removed / data["weight"]
            if ratio > best_ratio:
                best, best_ratio = (u, v, data["weight"]), ratio
        if best is None:  # аль ч ирмэг гүүр арилгахгүй → зогсоно
            warning = "2-Edge топологи бүрэн болсонгүй: %d гүүр үлдсэн (нөөц зам нэмэх боломжгүй)." % len(bridges)
            break
        H.add_edge(best[0], best[1], weight=best[2])
        added.append(best)
    return H, added, warning


def build_full_mesh(G):
    """Full Mesh: бүх хос хотыг шууд холбоно, жин = хамгийн богино замын зай (зөвхөн зардлын харьцуулалтад)."""
    dist = dict(nx.all_pairs_dijkstra_path_length(G, weight="weight"))
    M = nx.Graph()
    M.add_nodes_from(G.nodes)
    for u, v in combinations(G.nodes, 2):
        if v in dist[u]:             # замаар холбогдоогүй хос алгасагдана
            M.add_edge(u, v, weight=dist[u][v])
    return M


def stats(H):
    """Топологийн статистик: нийт км, ирмэг, гүүр, fault-tolerant, хамгийн алс 2 хот ба RTT."""
    bridges = find_bridges(H)
    connected = len(H) > 0 and nx.is_connected(H)

    farthest = None  # хамгийн алслагдсан хос (замын жингээр)
    for u, dists in nx.all_pairs_dijkstra_path_length(H, weight="weight"):
        for v, d in dists.items():
            if u != v and (farthest is None or d > farthest["km"]):
                farthest = {"source": u, "target": v, "km": round(d, 1)}
    max_rtt = rtt_ms(farthest["km"]) if farthest else 0

    return {
        "total_km": round(sum(d["weight"] for _, _, d in H.edges(data=True)), 1),
        "edge_count": H.number_of_edges(),
        "bridges": [{"source": u, "target": v} for u, v in bridges],
        "bridge_count": len(bridges),
        "connected": connected,
        "fault_tolerant": connected and not bridges,
        "farthest": farthest,
        "max_rtt_ms": max_rtt,
        "rtt_ok": max_rtt < RTT_LIMIT_MS,
    }


def simulate_cut(H, u, v):
    """[FR-3.1, FR-3.2] (u,v) кабелийг таслаад сүлжээ холбоотой эсэхийг шалгана.

    Салсан бол хамгийн том хэсгээс тусгаарлагдсан хотуудыг, холбоотой бол u→v нөөц замыг буцаана.
    """
    C = H.copy()
    C.remove_edge(u, v)
    connected = nx.is_connected(C)

    isolated = []
    if not connected:  # хамгийн том холбоот хэсгээс бусад хотууд
        parts = sorted(nx.connected_components(C), key=len, reverse=True)
        isolated = [n for part in parts[1:] for n in part]

    reroute = None
    if nx.has_path(C, u, v):  # u→v нөөц зам байвал (хамгийн богино)
        path = nx.shortest_path(C, u, v, weight="weight")
        km = nx.path_weight(C, path, "weight")
        reroute = {"path": path, "km": round(km, 1), "rtt_ms": rtt_ms(km)}
    return {"connected": connected, "isolated": isolated, "reroute": reroute}
