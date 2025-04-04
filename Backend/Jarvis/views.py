from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# Create your views here.
def home(request):
    return render(request, "base.html")

@csrf_exempt
def get_model_info(request):
    if request.method == 'POST':
        # Parse JSON data from request body
        try:
            data = json.loads(request.body)
            print(data)

            # Do something with the message
            reply = "Hello, this is a response from the server"

            return HttpResponse(reply, content_type='text/plain')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return JsonResponse({'error': 'Only POST method allowed'}, status=405)
