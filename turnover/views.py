from django.shortcuts import render
from django.http import JsonResponse
from .models import Turnover
from django.db.models import Count

from django.http import JsonResponse
from datetime import datetime
import calendar
    
def get_line_chart(request):
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
    
    #A questão sugere que o calculo do Turnover seja: dividindo o número de funcionários que deixaram a empresa durante um PERÍODO específico pelo número médio total de funcionários durante o MESMO PERÍODO.
    #soma de demitidos no perído / média de ativos do período

    #Demetidos em um determinado periodo
    dict_dismissal_employees = get_dismissal_employees_by_period(init_date, end_date)
    
    #Ativos no mesmo período
    dict_actives_employees = get_actives_employees_by_period(init_date, end_date)
    
    turnover = calculate_turnover(dict_dismissal_employees["dismissal_employees"],dict_actives_employees["actives_employees"], period)

    RESPONSE_TEMPLATE['xAxis']['data'] = months_names
    RESPONSE_TEMPLATE['series']['series'] = [{
                "name": "Turnover",
                "type": "line",
                "data": [turnover]*len(months),
            }]
    
    # OBS: Vi em populate.py que o preenchimento da tabela foi realizado de forma aleatória. Isso acabou ocasionando uma inconsistência nos dados, pois fez com que o numero de demissões fosse extremamente grande, de modo que ao multiplicarmos por 100 para obter a porcentagem o valor ficasse bem alto. 
    return JsonResponse(RESPONSE_TEMPLATE)

 
def get_category_charts(request):
    RESPONSE_TEMPLATE = {
        "xAxis": {
            "type": "value",
            "show": True,
            "max": {}
        },
        "yAxis": {
            "type": "category",
            "data": []
        },
        "series": {
            "type": "horizontal_stacked",
            "series": []
        },
        "title": "Empresa",
        "grid": 6,
        "color": [
            "#2896DC"
        ],
        "is%": False
    }
    
    init_date = format_date(request.GET.get('init_date'))
    end_date = format_date(request.GET.get('end_date'))
    category = request.GET.get('category')
    period = end_date.month - init_date.month + 1
    
    #Demitidos em um determinado periodo por empresa da categoria
    dict_dismissal_employees = get_dismissal_employees_by_category_and_period(init_date, end_date, category)

    #Ativos no mesmo período por empresa da categoria
    dict_actives_employees = get_actives_employees_by_category_and_period(init_date, end_date, category)
    
    agruped_data= agrupe_queries(dict_dismissal_employees, dict_actives_employees)
    
    turnover_by_company = []
    for company in agruped_data:
        result = {}
        result['company'] = company['company']
        result['turnover'] = calculate_turnover(company['dismissals'], company['actives'], period)
        turnover_by_company.append(result)
               
    companies, turnovers = get_companies_and_turnovers(turnover_by_company)
    
    RESPONSE_TEMPLATE['yAxis']['data'] = companies
    RESPONSE_TEMPLATE['series']['series'] = [
            {
                "name": "Turnoveres",
                "data": turnovers,
                "type": "bar"
            }
        ]
        
    return JsonResponse(RESPONSE_TEMPLATE)


def format_date(date):
    return datetime.strptime(date, '%Y-%m-%d')

def get_month_name(month_number):
    return calendar.month_abbr[month_number]

def calculate_turnover(total_dismissal, active_employees, period):
    # requerido pela questão: (soma de fg_dismissal_on_month) / ((contagem de id_employee onde fg_status = 1) / (quantidade de meses do período selecionado))    
    turnover = (total_dismissal/ (active_employees/period))
    return turnover

def get_dismissal_employees_by_period(init_date, end_date):
    return Turnover.objects.filter(
           fg_dismissal_on_month=1,
           dt_reference_month__gte=init_date,
           dt_reference_month__lte=end_date
           ).aggregate(dismissal_employees=Count('id_employee'))

def get_actives_employees_by_period(init_date, end_date):
    return Turnover.objects.filter(
           fg_status=1,
           dt_reference_month__gte=init_date,
           dt_reference_month__lte=end_date
           ).aggregate(actives_employees=Count('id_employee'))

#Obs: Estou considerando que o nome da empresa é representado pela coluna ds_category_1, e o nome da "categoria da base" é representado pela coluna ds_category_5
def get_dismissal_employees_by_category_and_period(init_date, end_date, category):
    return  Turnover.objects.filter(
            fg_dismissal_on_month=1,
            ds_category_5 = category,
            dt_reference_month__gte=init_date,
            dt_reference_month__lte=end_date
            ).values('ds_category_1').annotate(dismissal_employees=Count('id_employee'))

#Obs: Estou considerando que o nome da empresa é representado pela coluna ds_category_1, e o nome da "categoria da base" é representado pela coluna ds_category_5
def get_actives_employees_by_category_and_period(init_date, end_date, category):
    return Turnover.objects.filter(
        fg_status=1,
        ds_category_5=category,
        dt_reference_month__gte=init_date,
        dt_reference_month__lte=end_date
    ).values('ds_category_1').annotate(actives_employees=Count('id_employee'))
    
def agrupe_queries(dismissals, actives):
    agruped_data=[]
    for dismissal, active in zip(dismissals, actives):
        agruped = {}
        agruped['company'] = dismissal['ds_category_1']
        agruped['dismissals'] = dismissal['dismissal_employees']
        agruped['actives'] = active['actives_employees']
        agruped_data.append(agruped)
    return agruped_data

def get_companies_and_turnovers(turnover_by_company):
    return zip(*[(i['company'], i['turnover']) for i in turnover_by_company])
    