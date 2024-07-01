from django.http import JsonResponse
from django.shortcuts import render
from .utils import get_recommended_stocks

def stock_search(request):
    return render(request, "stockapp/stock_search.html")

def start_analysis(request):
    try:
        recommended_stocks = get_recommended_stocks()
        return JsonResponse({'status': 'success', 'recommended_stocks': recommended_stocks})
    except Exception as e:
        return JsonResponse({'status': 'error', 'error': str(e)})
