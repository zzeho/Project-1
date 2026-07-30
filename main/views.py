from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import connection
from .models import Review

# Create your views here.

# A03 Injection

def index(request):
    search = request.GET.get("search", "")

    if search:
        query = f"""SELECT * FROM main_review
                    WHERE title LIKE '%{search}%'"""

        # Search is inserted directly into SQL allowing malicious input to be execute as commands
        # Search becomes part of the SQL itself

        # Fixed version using Django ORM:
        # reviews = Review.objects.filter(title__icontains=search)

        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [column[0] for column in cursor.description]
            reviews = [dict(zip(columns, row)) for row in cursor.fetchall()]
    else:
        reviews = Review.objects.all()

    return render(request, "index.html", {"reviews": reviews, "search": search,})

def signup(request):
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        password_confirm = request.POST.get("password_confirm", "")

        if password != password_confirm:
            return render(request, "signup.html", {"error": "Passwords do not match"})

        if User.objects.filter(username=username).exists():
            return render(request, "signup.html", {"error": "Username is already taken"})

        # OWASP A02: Cryptographic Failures
        user = User(username=username, password=password)
        user.save()


        # Fixed version:
        # User.objects.create_user(username=username, password=password)

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
    # Fixed version:

    # OWASP A09: Security Logging and Monitoring Failures:

    # Security-related events are not being logged or monitored
    

def logout_page(request):
    logout(request)
    return redirect("login")

def create_review(request):
    if request.method == "POST":
        title = request.POST.get("title", "")
        content = request.POST.get("content", "")

        if not title or not content:
            return render(request, "create_review.html", {
                "error": "Title and review content are required.",
                "title": title,
                "content": content,
            })

        Review.objects.create(title=title, content=content, user=request.user)

        return redirect("index")

    return render(request, "create_review.html")


# OWASP A01: Broken Access Control

def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id) 
    # Only checks the review ID, no user
    # Any logged in user is able to delete another user's reviews using developer tools (F12/Inspect on browser)

    # Fixed version: 
    # review = get_object_or_404(Review, id=review_id, user=request.user)
    # User is included, preventing other users from deleting your post

    if request.method == "POST":
        review.delete()

    return redirect("index")
