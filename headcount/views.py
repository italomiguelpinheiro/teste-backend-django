from django.shortcuts import render
from django.http import JsonResponse
from .models import Headcount
from django.db.models import Count

from django.http import JsonResponse
from datetime import datetime
import calendar

def get_line_chart(request):
    RESPONSE_TEMPLATE =  {
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
        "title": "Headcount por Ano",
        "grid": 6,
        "color": [
            "#D4DDE2",
            "#A3B6C2"
        ]
    }

    init_date = format_date(request.GET.get('init_date'))
    end_date = format_date(request.GET.get('end_date'))

    filtered_data = get_actives_employees_by_period(init_date, end_date)
    
    agruped_data = {}
    for result in filtered_data:
        month = result['dt_reference_month__month']
        year = result['dt_reference_month__year']
        active_employees = result['active_employees']
    
        RESPONSE_TEMPLATE['xAxis']['data'].append(get_month_name(month))
        
        if year not in agruped_data:
            agruped_data[year] = []
        agruped_data[year].append(active_employees)


    for year, values in agruped_data.items():
        RESPONSE_TEMPLATE['series']['series'].append({
            "name": str(year),
            "type": "line",
            "data": values
        })

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
            "series": [
                {
                    "name": "Colaboradores",
                    "data": [],
                    "type": "bar"
                }
            ]
        },
        "title": "Empresa",
        "grid": 6,
        "color": [
            "#2896DC"
        ],
        "is%": False
    }
    
    end_date = format_date(request.GET.get('end_date'))
    category = request.GET.get('category')

    #Filtrando os dados referentes aos empresários ativos que fazem parte da categoria selecionado dentro do mês determinado no end_date
    # A questão não diz nada sobre pegar os empresários ativos até o end_Date, mas sim, pegar todos os funcionarios ativos dentro do mês do end_date.
    filtered_data = get_companies_and_actives_employees_on_month_by_category(end_date, category)

    for result in filtered_data:
        RESPONSE_TEMPLATE['yAxis']['data'].append(result['ds_category_1'])
        RESPONSE_TEMPLATE['series']['series'][0]['data'].append(result['active_employees'])
        
    return JsonResponse(RESPONSE_TEMPLATE)

def format_date(date):
    return datetime.strptime(date, '%Y-%m-%d')

def get_month_name(month_number):
    return calendar.month_abbr[month_number]

#Retorna os funcionarios ativos por mês, o mês e o ano do periodo inidicado
def get_actives_employees_by_period(init_date, end_date):
    return Headcount.objects.filter(
            fg_status=1,
            dt_reference_month__gte=init_date,
            dt_reference_month__lte=end_date
        ).values('dt_reference_month__month', 'dt_reference_month__year').annotate(
            active_employees=Count('id_employee')
        )   
        
#Retorna as empresas da categoria passada e a quantidade de funcionarios ativos no mes passado no end_date
def get_companies_and_actives_employees_on_month_by_category(end_date, category):
    # Obs: Eu entendi que a ds_category_5 é a "categoria da base" e o ds_category_1 é o nome da empresa
    return Headcount.objects.filter(
            fg_status=1,
            ds_category_5 = category,
            dt_reference_month__month=end_date.month
        ).values('ds_category_1').annotate(
            active_employees=Count('id_employee')
        ) 
    