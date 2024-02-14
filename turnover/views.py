from django.shortcuts import render
from django.http import JsonResponse
from .models import Turnover
from django.db.models import Count, Sum

from django.http import JsonResponse
from datetime import datetime
import calendar

def format_date(date):
    return datetime.strptime(date, '%Y-%m-%d')

def get_month_name(month_number):
    return calendar.month_abbr[month_number]

def calculate_turnover(total_dismissal, active_employees, period):
    print(total_dismissal, active_employees, period)
    
    # requerido pela questão: (soma de fg_demitido_no_mes) / ((contagem de id_matricula onde fg_status = 1) / (quantidade de meses do período selecionado))    
    turnover = (total_dismissal/ (active_employees/period))
    
    return turnover
    
def get_line_chart(request):
    
    # Foi pedido para não alterar o title, porem como sugestão creio que ficaria melhor colocar "Taxa de Turnover por período"
    RESPONSE_TEMPLATE =   {
        "xAxis": {
            "type": "category",
            "data": []
        },
        "yAxis": {
            "type": "value"
        },
        "series": {
            "type": "stacked_line",
            "series": []
        },
        "title": "Taxa de Turnover por Ano (%)",
        "grid": 6,
        "color": [
            "#D4DDE2",
            "#A3B6C2"
        ]
    }
    
    
    init_date = format_date(request.GET.get('init_date'))
    end_date = format_date(request.GET.get('end_date'))
    period = end_date.month - init_date.month + 1
    months = set(range(init_date.month, end_date.month + 1))
    months_names = [get_month_name(month) for month in months]
    

    #Demetidos em um determinado periodo
    dict_dismissal_employees = Turnover.objects.filter(
        fg_dismissal_on_month=1,
        dt_reference_month__gte=init_date,
        dt_reference_month__lte=end_date
    ).aggregate(dismissal_employees=Count('id_employee'))
    
    #Ativos no mesmo período
    dict_actives_employees = Turnover.objects.filter(
        fg_status=1,
        dt_reference_month__gte=init_date,
        dt_reference_month__lte=end_date
    ).aggregate(actives_employees=Count('id_employee'))
    
    
    turnover = calculate_turnover(dict_dismissal_employees["dismissal_employees"],dict_actives_employees["actives_employees"], period)

    RESPONSE_TEMPLATE['xAxis']['data'] = months_names
    RESPONSE_TEMPLATE['series']['series'] = [{
                "name": "Turnover",
                "type": "line",
                "data": [turnover]*len(months),
            }]
    
    
    # Tenho duas sugestões sobre essa questão:
    # 1. Creio que o calculo de turnover seja diferente do descrito no enunciado. A não ser que estamos falando de taxas diferentes, o calculo do turnover é feito do seguinte modo: 
    #    Turnover =  ((número de admissões + número de desligamentos / 2) / número total de funcionários dentro da empresa) x 100
    # Nesse caso, a logica da questão mudaria e a tabela iria precisar ser um pouco diferente do que esta. O que nos leva a segunda sugestão:
    # 2. Vi em populate.py que o preenchimento da tabela foi realizado de forma aleatória. Isso acabou ocasionando uma inconsistência nos dados, pois fez com que o numero de demissões fosse extremamente grande, de modo que ao multiplicarmos por 100 para obter a porcentagem o valor ficasse bem alto. 

    return JsonResponse(RESPONSE_TEMPLATE)

 
def get_category_charts(request):
    return JsonResponse({'response': 'GET CATEGORY CHARTS - TURNOVER'})