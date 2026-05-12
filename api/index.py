"""
API REST - Fase 3 (SQL Dynamic Analytics)
Expone los datos y analytics almacenados en PostgreSQL (Supabase) mediante endpoints HTTP.
"""

import os
import json
import sys

from flask import Flask, jsonify, request
from flask_cors import CORS
import traceback

try:
    from .db_config import get_connection
except ImportError:
    from db_config import get_connection

app = Flask(__name__)
CORS(app)

@app.errorhandler(Exception)
def handle_exception(e):
    """Retorna JSON en lugar de HTML en caso de errores del servidor."""
    # Para ver el log en consola o en Vercel
    traceback.print_exc()
    # Si es una excepcion HTTP de Werkzeug (ej. 404, 405), extraemos su codigo
    code = 500
    if hasattr(e, "code"):
        code = e.code
    return jsonify({"error": str(e), "message": getattr(e, "description", "Internal Server Error")}), code

# ---------------------------------------------------------------------------
# Endpoint principal: /api/datos (datos crudos del warehouse)
# ---------------------------------------------------------------------------

@app.route("/api/datos", methods=["GET"])
def obtener_datos():
    origen = request.args.get("origen")
    limite = request.args.get("limite", 500, type=int)
    offset = request.args.get("offset", 0, type=int)

    conn = get_connection()
    cur = conn.cursor()

    if origen:
        cur.execute(
            "SELECT id, origen, contenido, fecha FROM datos_warehouse "
            "WHERE origen = %s ORDER BY fecha DESC LIMIT %s OFFSET %s",
            (origen.upper(), limite, offset),
        )
    else:
        cur.execute(
            "SELECT id, origen, contenido, fecha FROM datos_warehouse "
            "ORDER BY fecha DESC LIMIT %s OFFSET %s",
            (limite, offset),
        )

    rows = cur.fetchall()
    datos = [{"id": r[0], "origen": r[1], "contenido": r[2], "fecha": r[3].isoformat() if r[3] else None} for r in rows]

    cur.close()
    conn.close()
    return jsonify({"total": len(datos), "datos": datos})


# ---------------------------------------------------------------------------
# Endpoint de resumen/estadisticas generales
# ---------------------------------------------------------------------------

@app.route("/api/datos/resumen", methods=["GET"])
def resumen():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT origen, COUNT(*) FROM datos_warehouse GROUP BY origen")
    por_origen = {r[0]: r[1] for r in cur.fetchall()}

    cur.execute("SELECT COUNT(*) FROM datos_warehouse")
    total = cur.fetchone()[0]

    cur.execute("SELECT MIN(fecha), MAX(fecha) FROM datos_warehouse")
    fecha_min, fecha_max = cur.fetchone()

    cur.execute("""
        SELECT date_trunc('minute', fecha) AS minuto, origen, COUNT(*) AS cantidad
        FROM datos_warehouse GROUP BY minuto, origen ORDER BY minuto
    """)
    timeline = [{"timestamp": r[0].isoformat() if r[0] else None, "origen": r[1], "cantidad": r[2]} for r in cur.fetchall()]

    cur.close()
    conn.close()

    return jsonify({
        "total": total, "por_origen": por_origen,
        "fecha_inicio": fecha_min.isoformat() if fecha_min else None,
        "fecha_fin": fecha_max.isoformat() if fecha_max else None,
        "timeline": timeline,
    })


# ---------------------------------------------------------------------------
# Endpoint: Sensores UDP
# ---------------------------------------------------------------------------

@app.route("/api/datos/sensores", methods=["GET"])
def obtener_sensores():
    limite = request.args.get("limite", 200, type=int)
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT contenido, fecha FROM datos_warehouse WHERE origen = 'UDP' ORDER BY fecha LIMIT %s", (limite,))

    sensores = []
    for row in cur.fetchall():
        try:
            data = json.loads(row[0])
            data["fecha_insercion"] = row[1].isoformat() if row[1] else None
            sensores.append(data)
        except json.JSONDecodeError:
            continue

    cur.close()
    conn.close()
    return jsonify({"total": len(sensores), "sensores": sensores})
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM olist_order_items")
    total_items = cur.fetchone()[0]

    cur.execute("SELECT SUM(price), SUM(freight_value), AVG(price), AVG(freight_value), MAX(price), MAX(freight_value) FROM olist_order_items")
    stats = cur.fetchone()
    ingreso_total = round(float(stats[0] or 0), 2)
    envio_total = round(float(stats[1] or 0), 2)
    precio_promedio = round(float(stats[2] or 0), 2)
    envio_promedio = round(float(stats[3] or 0), 2)
    precio_max = float(stats[4] or 0)
    envio_max = float(stats[5] or 0)

    cur.execute("""
        SELECT 
            SUM(CASE WHEN price <= 25 THEN 1 ELSE 0 END) as "$0-25",
            SUM(CASE WHEN price > 25 AND price <= 50 THEN 1 ELSE 0 END) as "$25-50",
            SUM(CASE WHEN price > 50 AND price <= 100 THEN 1 ELSE 0 END) as "$50-100",
            SUM(CASE WHEN price > 100 AND price <= 200 THEN 1 ELSE 0 END) as "$100-200",
            SUM(CASE WHEN price > 200 AND price <= 500 THEN 1 ELSE 0 END) as "$200-500",
            SUM(CASE WHEN price > 500 THEN 1 ELSE 0 END) as "$500+"
        FROM olist_order_items
    """)
    p_row = cur.fetchone()
    if p_row:
        rangos_precio = {
            "$0-25": p_row[0] or 0, "$25-50": p_row[1] or 0, "$50-100": p_row[2] or 0,
            "$100-200": p_row[3] or 0, "$200-500": p_row[4] or 0, "$500+": p_row[5] or 0
        }
    else:
        rangos_precio = {"$0-25":0, "$25-50":0, "$50-100":0, "$100-200":0, "$200-500":0, "$500+":0}

    cur.execute("""
        SELECT 
            SUM(CASE WHEN freight_value <= 10 THEN 1 ELSE 0 END) as "$0-10",
            SUM(CASE WHEN freight_value > 10 AND freight_value <= 20 THEN 1 ELSE 0 END) as "$10-20",
            SUM(CASE WHEN freight_value > 20 AND freight_value <= 30 THEN 1 ELSE 0 END) as "$20-30",
            SUM(CASE WHEN freight_value > 30 AND freight_value <= 50 THEN 1 ELSE 0 END) as "$30-50",
            SUM(CASE WHEN freight_value > 50 AND freight_value <= 100 THEN 1 ELSE 0 END) as "$50-100",
            SUM(CASE WHEN freight_value > 100 THEN 1 ELSE 0 END) as "$100+"
        FROM olist_order_items
    """)
    f_row = cur.fetchone()
    if f_row:
        rangos_envio = {
            "$0-10": f_row[0] or 0, "$10-20": f_row[1] or 0, "$20-30": f_row[2] or 0,
            "$30-50": f_row[3] or 0, "$50-100": f_row[4] or 0, "$100+": f_row[5] or 0
        }
    else:
        rangos_envio = {"$0-10":0, "$10-20":0, "$20-30":0, "$30-50":0, "$50-100":0, "$100+":0}

    cur.execute("""
        SELECT 
            SUM(CASE WHEN r <= 10 THEN 1 ELSE 0 END) as "0-10%",
            SUM(CASE WHEN r > 10 AND r <= 20 THEN 1 ELSE 0 END) as "10-20%",
            SUM(CASE WHEN r > 20 AND r <= 30 THEN 1 ELSE 0 END) as "20-30%",
            SUM(CASE WHEN r > 30 AND r <= 50 THEN 1 ELSE 0 END) as "30-50%",
            SUM(CASE WHEN r > 50 AND r <= 100 THEN 1 ELSE 0 END) as "50-100%",
            SUM(CASE WHEN r > 100 THEN 1 ELSE 0 END) as "100%+"
        FROM (
            SELECT (freight_value / price * 100) as r
            FROM olist_order_items WHERE price > 0
        ) t
    """)
    r_row = cur.fetchone()
    if r_row:
        rangos_ratio = {
            "0-10%": r_row[0] or 0, "10-20%": r_row[1] or 0, "20-30%": r_row[2] or 0,
            "30-50%": r_row[3] or 0, "50-100%": r_row[4] or 0, "100%+": r_row[5] or 0
        }
    else:
        rangos_ratio = {"0-10%":0, "10-20%":0, "20-30%":0, "30-50%":0, "50-100%":0, "100%+":0}

    cur.execute("SELECT price, freight_value FROM olist_order_items TABLESAMPLE SYSTEM(1) LIMIT 150")
    scatter_sample = [{"precio": float(r[0]), "envio": float(r[1])} for r in cur.fetchall()]

    cur.close()
    conn.close()

    return jsonify({
        "total_items": total_items, "ingreso_total": ingreso_total, "envio_total": envio_total,
        "precio_promedio": precio_promedio, "envio_promedio": envio_promedio,
        "precio_max": precio_max, "envio_max": envio_max,
        "rangos_precio": rangos_precio, "rangos_envio": rangos_envio,
        "rangos_ratio_envio": rangos_ratio, "scatter_precio_envio": scatter_sample,
    })


# ---------------------------------------------------------------------------
# Endpoint: Analisis de Geolocalizacion (SQL Dinamico)
# ---------------------------------------------------------------------------

@app.route("/api/analytics/geo", methods=["GET"])
def analytics_geo():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM olist_customers")
    total_registros = cur.fetchone()[0]

    cur.execute("SELECT COUNT(DISTINCT customer_state) FROM olist_customers WHERE customer_state IS NOT NULL")
    total_estados = cur.fetchone()[0]

    cur.execute("SELECT COUNT(DISTINCT customer_city) FROM olist_customers WHERE customer_city IS NOT NULL")
    total_ciudades = cur.fetchone()[0]

    cur.execute("""
        SELECT customer_state, COUNT(*) as c 
        FROM olist_customers 
        WHERE customer_state IS NOT NULL 
        GROUP BY customer_state ORDER BY c DESC LIMIT 15
    """)
    top_estados = [{"state": r[0], "count": r[1]} for r in cur.fetchall()]

    cur.execute("""
        SELECT customer_city, COUNT(*) as c 
        FROM olist_customers 
        WHERE customer_city IS NOT NULL 
        GROUP BY customer_city ORDER BY c DESC LIMIT 20
    """)
    top_ciudades = [{"city": r[0], "count": r[1]} for r in cur.fetchall()]

    cur.execute("""
        WITH top_cities AS (
            SELECT customer_city, COUNT(*) as c 
            FROM olist_customers 
            WHERE customer_city IS NOT NULL 
            GROUP BY customer_city ORDER BY c DESC LIMIT 100
        )
        SELECT tc.customer_city, tc.c,
               (SELECT geolocation_lat FROM olist_geolocation WHERE geolocation_city = tc.customer_city LIMIT 1) as lat,
               (SELECT geolocation_lng FROM olist_geolocation WHERE geolocation_city = tc.customer_city LIMIT 1) as lng
        FROM top_cities tc
    """)
    ciudades_mapa = []
    for r in cur.fetchall():
        if r[2] is not None and r[3] is not None:
            ciudades_mapa.append({"city": r[0], "count": r[1], "lat": float(r[2]), "lng": float(r[3])})

    cur.execute("""
        SELECT geolocation_state, AVG(geolocation_lat), AVG(geolocation_lng), COUNT(*) as c
        FROM olist_geolocation
        WHERE geolocation_state IS NOT NULL AND geolocation_lat IS NOT NULL AND geolocation_lng IS NOT NULL
        GROUP BY geolocation_state ORDER BY c DESC
    """)
    estados_mapa = [{"state": r[0], "lat": round(float(r[1]), 4), "lng": round(float(r[2]), 4), "count": r[3]} for r in cur.fetchall()]

    cur.close()
    conn.close()

    return jsonify({
        "total_registros": total_registros, "total_estados": total_estados, "total_ciudades": total_ciudades,
        "top_estados": top_estados, "top_ciudades": top_ciudades, "ciudades_mapa": ciudades_mapa, "estados_mapa": estados_mapa,
    })


if __name__ == "__main__":
    print("=" * 55)
    print("  API REST - Data Warehouse Simulation (SQL Dynamic)")
    print("=" * 55)
    app.run(host="0.0.0.0", port=5000, debug=True)
