from django.shortcuts import render
from django.http import JsonResponse

def get_line_chart(request):
    return JsonResponse({'response': 'GET LINE CHART - TURNOVER'})


def get_category_charts(request):
    return JsonResponse({'response': 'GET CATEGORY CHARTS - TURNOVER'})