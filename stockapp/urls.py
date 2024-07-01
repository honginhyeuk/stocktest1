from django.urls import path
from .views import stock_search, start_analysis

urlpatterns = [
    path('', stock_search, name='stock_search'),
    path('start-analysis/', start_analysis, name='start_analysis'),
]
