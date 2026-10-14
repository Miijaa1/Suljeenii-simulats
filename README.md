# Монгол улсын шилэн кабелийн сүлжээний симуляци

Их сургуулийн лабораторийн ажил. Улаанбаатар + 21 аймгийн төвийн (22 зангилаа) шилэн кабелийн сүлжээг
графаар загварчилж, 3 топологийг (MST, 2-Edge-Connected, Full Mesh) харьцуулан, кабель таслах симуляци хийнэ.
Өгөгдөл санах ойд хадгалагдана (өгөгдлийн сан, auth байхгүй).

## Ажиллуулах

Backend (Python 3.9+, port 5001):

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Асахад MST / 2-Edge / Full Mesh-ийн нийт км, гүүрийн тоо, max RTT-ийг харьцуулсан хүснэгтийг console-д хэвлэнэ.

Frontend (Node.js 20.19+ эсвэл 22+), өөр terminal дээр:

```bash
cd frontend
npm install
npm run dev
```

Дараа нь http://localhost:5173 хаягийг нээнэ. Газрын зургийн дэвсгэр (OpenStreetMap) интернэт шаардана.
Backend-ийн хаяг `frontend/src/App.jsx` дахь `API` тогтмолд байна.

## Бүтэц

```
backend/
  data.py          22 зангилаа, замын ирмэгүүд (боломжит трасс)        [FR-1.1]
  graph_engine.py  MST, Tarjan гүүр, 2-edge-connected, Full Mesh, статистик, таслалт
  app.py           Flask REST API
frontend/src/
  App.jsx                  төлөв, backend-тэй харилцах
  components/MapView.jsx   Leaflet газрын зураг
  components/SidePanel.jsx товчлуур, статистик, засварын form
```

## Алгоритм

| Шаардлага | Тайлбар | Хаана |
|-----------|---------|-------|
| FR-2.1 | MST – Prim (`nx.minimum_spanning_tree`) | `build_mst` |
| FR-2.2 | Гүүр олох – Tarjan (DFS, `disc`/`low`), өөрөө бичсэн | `find_bridges` |
| FR-2.3 | MST-д (арилсан гүүр / км) харьцаа хамгийн их ирмэгийг давтан нэмж гүүргүй болгоно | `make_two_edge_connected` |
| FR-3.1, 3.2 | Кабель таслаад холбоотой эсэх, салсан хотууд, нөөц зам, RTT | `simulate_cut` |
| – | Full Mesh: бүх хос хот, жин = хамгийн богино замын зай (зөвхөн зардлын харьцуулалт) | `build_full_mesh` |

RTT (ms) = 2 × зам_км / 200 (гэрэл шилэн кабельд ≈ 200 км/мс). Зорилт: < 50 ms.

## REST API (http://127.0.0.1:5001)

| Метод | Зам | Тайлбар |
|-------|-----|---------|
| GET | `/api/network/topologies` | `{ nodes, topologies: { mst, two_edge, full_mesh }, warnings }` |
| POST | `/api/network/simulate-cut` | `{topology, source, target}` → `{connected, isolated, reroute}` |
| POST | `/api/nodes` | зангилаа нэмэх/засах `{id, name, lat, lon}` [FR-1.2] |
| DELETE | `/api/nodes/<id>` | зангилаа (болон түүний ирмэгүүд) устгах |
| POST | `/api/edges` | ирмэг нэмэх/засах `{source, target, km}` |
| DELETE | `/api/edges/<source>/<target>` | ирмэг устгах |

Буруу оролтод 400 / 404 ба `{ "error": "..." }` буцна. Засвар хийсний дараа граф салсан эсвэл 2-Edge болохгүй
бол сервер унахгүй, `warnings` жагсаалтад мэдэгдэл орно.

## Хэрэглээ

- Дээд талын 3 товчоор топологи солино: MST (улаан), 2-Edge (цэнхэр), Full Mesh (ногоон).
  Гүүр тасархай, 2-Edge-ийн нэмэгдсэн ирмэг бүдүүн зурагдана.
- Кабель дээр дарж «Таслах» товчийг дарна: тасарсан кабель саарал, салсан хотууд нил ягаан,
  нөөц зам улбар шар болно. «Сэргээх» товч хэвийн байдалд буцаана.
- «Засвар» хэсгээс хот болон кабелийг нэмэх / засах / устгана.

## Анхаарах зүйл

Замын урт нь бодит замын зайд ойролцоо тооцоолсон утга бөгөөд албан ёсны хэмжилт биш.
