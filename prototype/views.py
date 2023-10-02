from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpRequest
from django.views.decorators.http import require_http_methods


@login_required()
@require_http_methods(['GET'])
def index(request: HttpRequest):
    # Process the events and metadata and put it into db
    return HttpResponse(f'Welcome to the world of workflows: {request.user}')
