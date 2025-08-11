from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from datetime import datetime
from zoneinfo import ZoneInfo
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
    #llamada de API
    response = requests.get(settings.API_URL)  # URL de la API
    posts = response.json()  # Convertir la respuesta a JSON
        #Normalizamos datos
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
    #Tasa de conversion
    tasa = (completados / total_visitantes) if total_visitantes else 0.0
    #Numero de respuestas hoy
    respuestahoy = sum(
        1
        for e in entries
        if e.get("relleno_formulario") is True
        and (ts := parse_ts_es(e.get("timestamp"))) is not None
        and ts.date() == hoy
    )
    #Datos para la tabla 
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

    #Datos a enviar
    data = {
        'title': "Landing Page Dashboard",
        'total_visitantes': total_visitantes,
        "total_respuestas": completados,
        "respuestas_de_hoy": respuestahoy,
        "tasa_conversion": tasa,
        "filas": filas,  # ← lista de tuplas (col1, col2)
    }

        # return HttpResponse("¡Bienvenido a la aplicación Django!")
    return render(request, 'dashboard/index.html',data)