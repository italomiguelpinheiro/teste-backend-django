from django.urls import path
from . import views

urlpatterns = [
    path('line_chart/', views.get_line_chart),
    path('category_charts/', views.get_category_charts)
]
    