from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
import requests
from django.conf import settings
def index(request):
    response = requests.get(settings.API_URL)  # URL de la API
    posts = response.json()  # Convertir la respuesta a JSON

    # Número total de respuestas
    total_responses = len(posts)
    data = {
        'title': "Landing Page' Dashboard",
        'total_responses': total_responses,
    }
    #Agregar interesados en Renovar Baño,Mejora de Cocina, 
    #Instalación de Azulejos en indicador 2, 3 y 4
    #En columnas 1 nombre completo y 2 email
    #El grafico de Respuesta vs Tiempo y 

        # return HttpResponse("¡Bienvenido a la aplicación Django!")
    return render(request, 'dashboard/index.html',data)