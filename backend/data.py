"""Өгөгдөл: Монгол улсын 22 зангилаа ба боломжит авто замын трасс [FR-1.1].

Энэ өгөгдөл app.py асахад санах ойд (dict) хуулагдаж, дараа нь API-аар засагдана.
"""

# [FR-1.1] 22 зангилаа: Улаанбаатар + 21 аймгийн төв (бодит координат)
NODES = [
    {"id": "ulaanbaatar",  "name": "Улаанбаатар",         "lat": 47.9184, "lon": 106.9177},
    {"id": "darkhan",      "name": "Дархан",              "lat": 49.4867, "lon": 105.9228},
    {"id": "erdenet",      "name": "Эрдэнэт",             "lat": 49.0278, "lon": 104.0444},
    {"id": "sukhbaatar",   "name": "Сүхбаатар (Сэлэнгэ)", "lat": 50.2333, "lon": 106.2000},
    {"id": "zuunmod",      "name": "Зуунмод",             "lat": 47.7094, "lon": 106.9456},
    {"id": "choir",        "name": "Чойр",                "lat": 46.3667, "lon": 108.3667},
    {"id": "sainshand",    "name": "Сайншанд",            "lat": 44.8914, "lon": 110.1194},
    {"id": "mandalgovi",   "name": "Мандалговь",          "lat": 45.7625, "lon": 106.2708},
    {"id": "dalanzadgad",  "name": "Даланзадгад",         "lat": 43.5708, "lon": 104.4256},
    {"id": "arvaikheer",   "name": "Арвайхээр",           "lat": 46.2639, "lon": 102.7750},
    {"id": "tsetserleg",   "name": "Цэцэрлэг",            "lat": 47.4753, "lon": 101.4544},
    {"id": "bulgan",       "name": "Булган",              "lat": 48.8125, "lon": 103.5347},
    {"id": "moron",        "name": "Мөрөн",               "lat": 49.6358, "lon": 100.1658},
    {"id": "bayankhongor", "name": "Баянхонгор",          "lat": 46.1944, "lon": 100.7181},
    {"id": "altai",        "name": "Алтай",               "lat": 46.3722, "lon": 96.2578},
    {"id": "uliastai",     "name": "Улиастай",            "lat": 47.7417, "lon": 96.8444},
    {"id": "ulaangom",     "name": "Улаангом",            "lat": 49.9811, "lon": 92.0667},
    {"id": "olgii",        "name": "Өлгий",               "lat": 48.9683, "lon": 89.9625},
    {"id": "khovd",        "name": "Ховд",                "lat": 48.0056, "lon": 91.6419},
    {"id": "chinggis",     "name": "Чингис хот",          "lat": 47.3189, "lon": 110.6558},
    {"id": "baruun_urt",   "name": "Баруун-Урт",          "lat": 46.6806, "lon": 113.2792},
    {"id": "choibalsan",   "name": "Чойбалсан",           "lat": 48.0722, "lon": 114.5361},
]

# [FR-1.1] Ирмэг = хөрш хотуудыг холбох авто замын трасс: (эх, төгсгөл, км).
# Урт нь бодит замын зайд ойролцоо. Зангилаа бүр ≥2 ирмэгтэй, граф гүүргүй.
EDGES = [
    # Төв ба хойд
    ("ulaanbaatar", "zuunmod", 43),
    ("ulaanbaatar", "darkhan", 220),
    ("ulaanbaatar", "tsetserleg", 470),
    ("ulaanbaatar", "arvaikheer", 430),
    ("ulaanbaatar", "mandalgovi", 300),
    ("ulaanbaatar", "chinggis", 330),
    ("darkhan", "sukhbaatar", 95),
    ("darkhan", "erdenet", 160),
    ("sukhbaatar", "erdenet", 250),
    ("erdenet", "bulgan", 90),
    ("bulgan", "moron", 280),
    ("bulgan", "tsetserleg", 265),
    ("moron", "tsetserleg", 290),
    # Өмнөд ба зүүн өмнөд
    ("zuunmod", "choir", 215),
    ("zuunmod", "mandalgovi", 270),
    ("mandalgovi", "choir", 220),
    ("mandalgovi", "dalanzadgad", 300),
    ("mandalgovi", "arvaikheer", 340),
    ("choir", "sainshand", 230),
    ("choir", "chinggis", 280),
    # Зүүн
    ("sainshand", "baruun_urt", 380),
    ("baruun_urt", "chinggis", 280),
    ("baruun_urt", "choibalsan", 270),
    ("chinggis", "choibalsan", 340),
    # Хангай ба баруун
    ("arvaikheer", "tsetserleg", 190),
    ("arvaikheer", "bayankhongor", 215),
    ("bayankhongor", "tsetserleg", 240),
    ("dalanzadgad", "bayankhongor", 480),
    ("bayankhongor", "altai", 520),
    ("altai", "uliastai", 280),
    ("uliastai", "tsetserleg", 450),
    ("uliastai", "moron", 520),
    ("altai", "khovd", 450),
    ("uliastai", "ulaangom", 560),
    ("khovd", "olgii", 410),
    ("khovd", "ulaangom", 410),
    ("olgii", "ulaangom", 330),
]
