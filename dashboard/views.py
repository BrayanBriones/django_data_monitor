from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from collections import defaultdict
import json


@login_required
def index(request):
    TZ = ZoneInfo("America/Guayaquil")

    def parse_ts_es(s, tz=TZ):
        if not s:
            return None
        # Normaliza “a. m.” / “p. m.” a AM/PM
        s = s.replace("a. m.", "AM").replace("p. m.", "PM")
        # Formato: dd/mm/YYYY, hh:mm:ss AM/PM
        try:
            dt = datetime.strptime(s, "%d/%m/%Y, %I:%M:%S %p")
            return dt.replace(tzinfo=tz)
        except ValueError:
            return None

    def visitor_key(e):
        return e.get("correo") or e.get("usuario") or e.get("nombre") or e.get("_id")

    # llamada de API
    response = requests.get(settings.API_URL)  # URL de la API
    posts = response.json()  # Convertir la respuesta a JSON
    # Normalizamos datos
    if isinstance(posts, dict):
        entries = [{**v, "_id": k} for k, v in posts.items()]
    elif isinstance(posts, list):
        entries = [{**item, "_id": str(i)} for i, item in enumerate(posts)]
    else:
        entries = []

    hoy = datetime.now(TZ).date()
    # Número total de visitantes
    total_visitantes = len(posts)
    # Numero de personas que rellenaron el formulario
    completados = sum(1 for e in entries if e.get("relleno_formulario") is True)
    # Tasa de conversion
    tasa = (completados / total_visitantes) if total_visitantes else 0.0
    # Numero de respuestas hoy
    respuestahoy = sum(
        1
        for e in entries
        if e.get("relleno_formulario") is True
        and (ts := parse_ts_es(e.get("timestamp"))) is not None
        and ts.date() == hoy
    )
    # Datos para la tabla
    # Filtra solo quienes llenaron el formulario
    entries_ok = [e for e in entries if e.get("relleno_formulario") is True]

    # Ordénalos por timestamp (más recientes primero)
    def clave_orden(e):
        ts = parse_ts_es(e.get("timestamp"))
        return ts or datetime.min.replace(tzinfo=TZ)

    entries_ok.sort(key=clave_orden, reverse=True)

    # Construye pares (col1, col2) ya emparejados
    filas = [
        (
            e.get("nombre") or e.get("correo") or e.get("usuario"),
            e.get("timestamp"),
        )
        for e in entries_ok
    ]

    # Crear diccionarios para contar por día
    visitantes_por_dia = defaultdict(int)
    respuestas_por_dia = defaultdict(int)

    # Obtener los últimos 7 días
    ultimos_7_dias = []
    for i in range(6, -1, -1):  # De 6 a 0 (últimos 7 días)
        fecha = hoy - timedelta(days=i)
        ultimos_7_dias.append(fecha)
        visitantes_por_dia[fecha] = 0  # Inicializar en 0
        respuestas_por_dia[fecha] = 0  # Inicializar en 0

    # Contar visitantes por día (todos los entries)
    for e in entries:
        ts = parse_ts_es(e.get("timestamp"))
        if ts:
            fecha_visita = ts.date()
            if fecha_visita in visitantes_por_dia:
                visitantes_por_dia[fecha_visita] += 1

    # Contar respuestas por día (solo los que completaron formulario)
    for e in entries_ok:
        ts = parse_ts_es(e.get("timestamp"))
        if ts:
            fecha_respuesta = ts.date()
            if fecha_respuesta in respuestas_por_dia:
                respuestas_por_dia[fecha_respuesta] += 1

    # Preparar datos para Chart.js
    chart_labels = []
    chart_visitantes = []
    chart_respuestas = []

    for fecha in ultimos_7_dias:
        # Formato de etiqueta para el gráfico (ej: "Lun 12")
        nombre_dia = fecha.strftime("%a %d")
        chart_labels.append(nombre_dia)
        chart_visitantes.append(visitantes_por_dia[fecha])
        chart_respuestas.append(respuestas_por_dia[fecha])

    # Datos a enviar
    data = {
        "title": "Landing Page Dashboard",
        "total_visitantes": total_visitantes,
        "total_respuestas": completados,
        "respuestas_de_hoy": respuestahoy,
        "tasa_conversion": round(tasa, 3),
        "filas": filas,  # ← lista de tuplas (col1, col2)
        "chart_labels": json.dumps(chart_labels, ensure_ascii=False),
        "chart_visitantes": json.dumps(chart_visitantes),
        "chart_respuestas": json.dumps(chart_respuestas),
    }

    # return HttpResponse("¡Bienvenido a la aplicación Django!")
    return render(request, "dashboard/index.html", data)
