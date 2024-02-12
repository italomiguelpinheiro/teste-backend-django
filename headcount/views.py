from django.shortcuts import render
from django.http import HttpResponse

def get_line_chart(request):
    return HttpResponse('GET LINE CHART')


def get_category_charts(request):
    return HttpResponse('GET CATEGORIES CHARTS')
