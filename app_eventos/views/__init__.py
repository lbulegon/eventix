from django.shortcuts import render
from ..models import Evento

def home(request):
    return render(request, "home.html")

def evento_list(request):
    eventos = Evento.objects.all()
    return render(request, "evento_list.html", {"eventos": eventos})
