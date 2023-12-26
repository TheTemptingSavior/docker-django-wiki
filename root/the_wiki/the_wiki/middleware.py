from django.http import HttpResponse
from django.shortcuts import redirect


class HealthCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == "/health":
            return HttpResponse("ok")
        return self.get_response(request)


class AuthEverywhereMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Bypass authenticated for the login route
        if request.path == "/_accounts/login/" or request.path == "/admin/login/":
            return self.get_response(request)

        # user is not authenticated, redirect to the login page
        if not request.user.is_authenticated:
            return redirect("/_accounts/login/")

        return self.get_response(request)
