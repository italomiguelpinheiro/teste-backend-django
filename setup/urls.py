from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('headcount/', include('headcount.urls')),
    path('turnover/', include('turnover.urls'))
]
