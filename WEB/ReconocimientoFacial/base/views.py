from django.shortcuts import render
from django.http import request, HttpResponse

# Create your views here.
def base(request):
    return render(request, "base/base.html")


def home(request):
    return render(request, "base/home.html")

