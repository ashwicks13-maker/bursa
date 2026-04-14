from flask import Flask, request, Response
import sqlite3
import json
import os

app = Flask(__name__)

# 🔥 Render uyumlu DB path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "bursa.db")

# ------------------------
# DB QUERY SAFE
# ------------------------
def query_db(sql, params=()):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.text_factory = str  # UTF-8 fix

    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()

    return [dict(r) for r in rows]

# ------------------------
# HOME
# ------------------------
@app.route("/")
def home():
    return Response(
        json.dumps(
            {"status": "ok", "api": "bursa-sicil"},
            ensure_ascii=False
        ),
        content_type="application/json; charset=utf-8"
    )

# ------------------------
# MAIN SEARCH
# ------------------------
@app.route("/bursasicil")
def bursasicil():

    tc = request.args.get("tc", "").strip()
    ad = request.args.get("ad", "").strip()
    soyad = request.args.get("soyad", "").strip()
    city = request.args.get("city", "").strip()

    sql = "SELECT * FROM data WHERE 1=1"
    params = []

    # 🔥 TC
    if tc:
        sql += " AND AVUKAT_TC_KIMLIK_NO LIKE ?"
        params.append(f"%{tc}%")

    # 🔥 AD
    if ad:
        sql += " AND KISI_ADI LIKE ?"
        params.append(f"%{ad}%")

    # 🔥 SOYAD
    if soyad:
        sql += " AND KISI_SOYAD LIKE ?"
        params.append(f"%{soyad}%")

    # 🔥 CITY / KURUM
    if city:
        sql += " AND KURUM_ADI LIKE ?"
        params.append(f"%{city}%")

    sql += " LIMIT 100"

    result = query_db(sql, params)

    return Response(
        json.dumps(
            {"status": "success", "count": len(result), "data": result},
            ensure_ascii=False
        ),
        content_type="application/json; charset=utf-8"
    )

# ------------------------
# RUN (RENDER SAFE)
# ------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
