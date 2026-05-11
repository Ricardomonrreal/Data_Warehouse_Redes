"""
API REST - Fase 3 (SQL Dynamic Analytics)
Expone los datos y analytics almacenados en PostgreSQL (Supabase) mediante endpoints HTTP.
"""

import os
import json
import sys

from flask import Flask, jsonify, request
from flask_cors import CORS
from .db_config import get_connection

app = Flask(__name__)
CORS(app)

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


# ---------------------------------------------------------------------------
# Endpoint: Analisis de Ordenes (SQL Dinamico)
# ---------------------------------------------------------------------------

@app.route("/api/analytics/ordenes", methods=["GET"])
def analytics_ordenes():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM olist_orders")
    total_ordenes = cur.fetchone()[0]

    cur.execute("SELECT order_status, COUNT(*) FROM olist_orders GROUP BY order_status")
    estados = dict(cur.fetchall())

    cur.execute("""
        SELECT to_char(order_purchase_timestamp, 'YYYY-MM') as mes, COUNT(*) 
        FROM olist_orders 
        WHERE order_purchase_timestamp IS NOT NULL
        GROUP BY mes ORDER BY mes
    """)
    ordenes_por_mes = dict(cur.fetchall())

    cur.execute("""
        SELECT AVG(extract(epoch from (order_delivered_customer_date - order_purchase_timestamp))/86400) 
        FROM olist_orders 
        WHERE order_delivered_customer_date IS NOT NULL AND order_purchase_timestamp IS NOT NULL 
        AND extract(epoch from (order_delivered_customer_date - order_purchase_timestamp))/86400 BETWEEN 0 AND 120
    """)
    avg_row = cur.fetchone()
    promedio_entrega_dias = round(float(avg_row[0]), 1) if avg_row and avg_row[0] else 0

    cur.execute("""
        SELECT 
            SUM(CASE WHEN dias <= 5 THEN 1 ELSE 0 END) as "0-5",
            SUM(CASE WHEN dias > 5 AND dias <= 10 THEN 1 ELSE 0 END) as "6-10",
            SUM(CASE WHEN dias > 10 AND dias <= 15 THEN 1 ELSE 0 END) as "11-15",
            SUM(CASE WHEN dias > 15 AND dias <= 20 THEN 1 ELSE 0 END) as "16-20",
            SUM(CASE WHEN dias > 20 AND dias <= 30 THEN 1 ELSE 0 END) as "21-30",
            SUM(CASE WHEN dias > 30 AND dias <= 60 THEN 1 ELSE 0 END) as "31-60",
            SUM(CASE WHEN dias > 60 THEN 1 ELSE 0 END) as "60+"
        FROM (
            SELECT extract(epoch from (order_delivered_customer_date - order_purchase_timestamp))/86400 as dias
            FROM olist_orders 
            WHERE order_delivered_customer_date IS NOT NULL AND order_purchase_timestamp IS NOT NULL
        ) t WHERE dias BETWEEN 0 AND 120
    """)
    hist_row = cur.fetchone()
    if hist_row:
        rangos = {
            "0-5": hist_row[0] or 0, "6-10": hist_row[1] or 0, "11-15": hist_row[2] or 0,
            "16-20": hist_row[3] or 0, "21-30": hist_row[4] or 0, "31-60": hist_row[5] or 0,
            "60+": hist_row[6] or 0
        }
    else:
        rangos = {"0-5": 0, "6-10": 0, "11-15": 0, "16-20": 0, "21-30": 0, "31-60": 0, "60+": 0}

    cur.execute("""
        SELECT 
            SUM(CASE WHEN order_delivered_customer_date <= order_estimated_delivery_date THEN 1 ELSE 0 END),
            SUM(CASE WHEN order_delivered_customer_date > order_estimated_delivery_date THEN 1 ELSE 0 END)
        FROM olist_orders
        WHERE order_delivered_customer_date IS NOT NULL AND order_estimated_delivery_date IS NOT NULL
    """)
    tiempo_row = cur.fetchone()
    entregas_a_tiempo = tiempo_row[0] or 0 if tiempo_row else 0
    entregas_tarde = tiempo_row[1] or 0 if tiempo_row else 0

    cur.close()
    conn.close()

    return jsonify({
        "total_ordenes": total_ordenes, "estados": estados, "ordenes_por_mes": ordenes_por_mes,
        "promedio_entrega_dias": promedio_entrega_dias, "histograma_entrega": rangos,
        "entregas_a_tiempo": entregas_a_tiempo, "entregas_tarde": entregas_tarde,
    })


# ---------------------------------------------------------------------------
# Endpoint: Analisis de Productos (SQL Dinamico)
# ---------------------------------------------------------------------------

@app.route("/api/analytics/productos", methods=["GET"])
def analytics_productos():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM olist_products")
    total_productos = cur.fetchone()[0]

    cur.execute("SELECT COUNT(DISTINCT product_category_name) FROM olist_products WHERE product_category_name IS NOT NULL")
    total_categorias = cur.fetchone()[0]

    cur.execute("""
        SELECT product_category_name, COUNT(*) as c 
        FROM olist_products 
        WHERE product_category_name IS NOT NULL 
        GROUP BY product_category_name 
        ORDER BY c DESC LIMIT 15
    """)
    top_categorias = dict(cur.fetchall())

    cur.execute("SELECT product_category_name, product_category_name_english FROM product_category_translation")
    traducciones = dict(cur.fetchall())

    cur.execute("""
        SELECT 
            SUM(CASE WHEN product_weight_g <= 500 THEN 1 ELSE 0 END) as "0-500g",
            SUM(CASE WHEN product_weight_g > 500 AND product_weight_g <= 1000 THEN 1 ELSE 0 END) as "500g-1kg",
            SUM(CASE WHEN product_weight_g > 1000 AND product_weight_g <= 2000 THEN 1 ELSE 0 END) as "1-2kg",
            SUM(CASE WHEN product_weight_g > 2000 AND product_weight_g <= 5000 THEN 1 ELSE 0 END) as "2-5kg",
            SUM(CASE WHEN product_weight_g > 5000 AND product_weight_g <= 10000 THEN 1 ELSE 0 END) as "5-10kg",
            SUM(CASE WHEN product_weight_g > 10000 THEN 1 ELSE 0 END) as "10kg+"
        FROM olist_products
        WHERE product_weight_g IS NOT NULL
    """)
    w_row = cur.fetchone()
    if w_row:
        rangos_peso = {
            "0-500g": w_row[0] or 0, "500g-1kg": w_row[1] or 0, "1-2kg": w_row[2] or 0,
            "2-5kg": w_row[3] or 0, "5-10kg": w_row[4] or 0, "10kg+": w_row[5] or 0
        }
    else:
        rangos_peso = {"0-500g":0, "500g-1kg":0, "1-2kg":0, "2-5kg":0, "5-10kg":0, "10kg+":0}

    cur.execute("SELECT AVG(product_weight_g) FROM olist_products WHERE product_weight_g IS NOT NULL")
    avg_w = cur.fetchone()[0]
    peso_promedio = int(avg_w) if avg_w else 0

    cur.execute("SELECT AVG(product_photos_qty) FROM olist_products WHERE product_photos_qty IS NOT NULL")
    avg_ph = cur.fetchone()[0]
    promedio_fotos = round(float(avg_ph), 1) if avg_ph else 0

    cur.execute("SELECT product_photos_qty, COUNT(*) FROM olist_products WHERE product_photos_qty IS NOT NULL GROUP BY product_photos_qty ORDER BY product_photos_qty")
    distribucion_fotos = {str(int(k)): v for k, v in cur.fetchall()}

    cur.execute("SELECT AVG(product_description_lenght) FROM olist_products WHERE product_description_lenght IS NOT NULL")
    avg_desc = cur.fetchone()[0]
    promedio_largo_descripcion = int(avg_desc) if avg_desc else 0

    cur.close()
    conn.close()

    return jsonify({
        "total_productos": total_productos, "total_categorias": total_categorias, "top_categorias": top_categorias,
        "traducciones": traducciones, "rangos_peso": rangos_peso, "peso_promedio_g": peso_promedio,
        "promedio_fotos": promedio_fotos, "distribucion_fotos": distribucion_fotos,
        "promedio_largo_descripcion": promedio_largo_descripcion,
    })


# ---------------------------------------------------------------------------
# Endpoint: Analisis de Items (SQL Dinamico)
# ---------------------------------------------------------------------------

@app.route("/api/analytics/items", methods=["GET"])
def analytics_items():
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

    cur.execute("SELECT COUNT(*) FROM olist_geolocation")
    total_registros = cur.fetchone()[0]

    cur.execute("SELECT COUNT(DISTINCT geolocation_state) FROM olist_geolocation WHERE geolocation_state IS NOT NULL")
    total_estados = cur.fetchone()[0]

    cur.execute("SELECT COUNT(DISTINCT geolocation_city) FROM olist_geolocation WHERE geolocation_city IS NOT NULL")
    total_ciudades = cur.fetchone()[0]

    cur.execute("""
        SELECT geolocation_state, COUNT(*) as c 
        FROM olist_geolocation 
        WHERE geolocation_state IS NOT NULL 
        GROUP BY geolocation_state ORDER BY c DESC LIMIT 15
    """)
    top_estados = dict(cur.fetchall())

    cur.execute("""
        SELECT geolocation_city, COUNT(*) as c 
        FROM olist_geolocation 
        WHERE geolocation_city IS NOT NULL 
        GROUP BY geolocation_city ORDER BY c DESC LIMIT 20
    """)
    top_ciudades = dict(cur.fetchall())

    cur.execute("""
        SELECT geolocation_lat, geolocation_lng, geolocation_city, geolocation_state
        FROM olist_geolocation
        TABLESAMPLE SYSTEM(1)
        LIMIT 200
    """)
    puntos_mapa = [{"lat": float(r[0]), "lng": float(r[1]), "city": r[2], "state": r[3]} for r in cur.fetchall()]

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
        "top_estados": top_estados, "top_ciudades": top_ciudades, "puntos_mapa": puntos_mapa, "estados_mapa": estados_mapa,
    })


if __name__ == "__main__":
    print("=" * 55)
    print("  API REST - Data Warehouse Simulation (SQL Dynamic)")
    print("=" * 55)
    app.run(host="0.0.0.0", port=5000, debug=True)
