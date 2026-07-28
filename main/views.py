from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .models import Review

# Create your views here.

def index(request):
    reviews = Review.objects.all()
    return render(request, "index.html", {"reviews": reviews})

def signup(request):
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        password_confirm = request.POST.get("password_confirm", "")

        if password != password_confirm:
            return render(request, "signup.html", {"error": "Passwords do not match"})

        if User.objects.filter(username=username).exists():
            return render(request, "signup.html", {"error": "Username is already taken"})

        User.objects.create_user(username=username, password=password)

        return redirect("login")
    
    return render(request, "signup.html")

def login_page(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("index")

        return render(request, "login.html", {"error": "Invalid username or password"})

    return render(request, "login.html",)

    # OWASP A07: Identification and Authetication failures

    # Unlimited log in tries, nothing punishing attackers for repeated failures or any delay between attempts.
    # Vulnerable to brute-force attacks
    # Fixed version: SCREENSHOT FIRST!