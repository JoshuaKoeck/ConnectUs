from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

def index(request):
    context = {
        "total": 42,
    }
    return render(request, "index.html", context)


def faq(request):
    """Render the FAQ page (trilingual)."""
    
    return render(request, "faq.html")