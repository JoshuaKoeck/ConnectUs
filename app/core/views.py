from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

def index(request):
    context = {
        "total": 42,
    }
    return render(request, "index.html", context)