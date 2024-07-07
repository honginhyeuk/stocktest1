from django.http import JsonResponse
from django.shortcuts import render
from .utils import get_recommended_stocks

def stock_search(request):
    return render(request, "stockapp/stock_search.html")

def start_analysis(request):
    try:
        recommended_stocks, recent_business_day = get_recommended_stocks()
        if not recommended_stocks:
            return JsonResponse({'status': 'error', 'error': 'No recommended stocks found', 'date': recent_business_day})
        return JsonResponse({'status': 'success', 'recommended_stocks': recommended_stocks, 'date': recent_business_day})
    except Exception as e:
        import traceback
        error_message = traceback.format_exc()
        print(error_message)  # 오류 로그 출력
        return JsonResponse({'status': 'error', 'error': str(e), 'traceback': error_message})
