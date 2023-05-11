from django.http import HttpResponse
from django.shortcuts import render

def map(request):
    return render(request,'yumymap/map.html')
