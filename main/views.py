from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import connection
from datetime import timedelta
from django.utils import timezone
import logging
from .models import Review


logger = logging.getLogger(__name__)

# Create your views here.

# OWASP A03 Injection

def index(request):
    search = request.GET.get("search", "")

    if search:
        query = f"""SELECT * FROM main_review
                    WHERE title LIKE '%{search}%'"""

        # Search is inserted directly into SQL allowing malicious input to be execute as commands
        # Search becomes part of the SQL itself

        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [column[0] for column in cursor.description]
            reviews = [dict(zip(columns, row)) for row in cursor.fetchall()]
    else:
        reviews = Review.objects.all()

    return render(request, "index.html", {"reviews": reviews, "search": search,})

# Fixed version for A03 using Django ORM:

# def index(request):
#     search = request.GET.get("search", "")

#     if search:
#         reviews = Review.objects.filter(title__icontains=search)

#         with connection.cursor() as cursor:
#             cursor.execute(query)
#             columns = [column[0] for column in cursor.description]
#             reviews = [dict(zip(columns, row)) for row in cursor.fetchall()]
#     else:
#         reviews = Review.objects.all()

#     return render(request, "index.html", {"reviews": reviews, "search": search,})


# OWASP A02: Cryptographic Failures

def signup(request):
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        password_confirm = request.POST.get("password_confirm", "")

        if len(username) > 20:
            return render(request, "signup.html", {"error": "Username must be 20 characters or fewer."})

        if len(password) < 4 or len(password) > 25:
            return render(request, "signup.html", {"error": "Password must be between 8 and 120 characters."})

        if password != password_confirm:
            return render(request, "signup.html", {"error": "Passwords do not match"})

        if User.objects.filter(username=username).exists():
            return render(request, "signup.html", {"error": "Username is already taken"})

        # OWASP A02: The problem
        user = User(username=username, password=password)
        user.save()

        return redirect("login")
    
    return render(request, "signup.html")

# Fixed version for A02:

# def signup(request):
#     if request.method == "POST":
#         username = request.POST.get("username", "")
#         password = request.POST.get("password", "")
#         password_confirm = request.POST.get("password_confirm", "")

#         if len(username) > 20:
#            return render(request, "signup.html", {"error": "Username must be 20 characters or fewer."})

#         if len(password) < 4 or len(password) > 25:
#            return render(request, "signup.html", {"error": "Password must be between 8 and 120 characters."})


#         if password != password_confirm:
#             return render(request, "signup.html", {"error": "Passwords do not match"})

#         if User.objects.filter(username=username).exists():
#             return render(request, "signup.html", {"error": "Username is already taken"})

#         User.objects.create_user(username=username, password=password)

#         return redirect("login")
    
#     return render(request, "signup.html")


# OWASP A07: Identification and Authetication failures
# Unlimited log in tries, nothing punishing attackers for repeated failures or any delay between attempts.
# Vulnerable to brute-force attacks

# OWASP A09: Security Logging and Monitoring Failures:
# Security-related events are not being logged or monitored

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

# Fixed version for both A07 and A09:

# max_attempts = 5
# lockedmins = 2

# def login_page(request):
#     locked_text = request.session.get("locked_until")

#     if locked_text:
#         locked_until = timezone.datetime.fromisoformat(locked_text)

#         if timezone.now() < locked_until:
#             return render(request, "login.html", {"error": "Too many failed attempts. Try again later.", "locked": True, })

#     if request.method == "POST":
#         username = request.POST.get("username", "")
#         password = request.POST.get("password", "")

#         user = authenticate(request, username=username, password=password)

#         if len(username) > 20:
#             return render(request, "signup.html", {"error": "Invalid username or password."})

#         if len(password) < 4 or len(password) > 25:
#             return render(request, "signup.html", {"error": "Invalid username or password."})

#         if user is not None:
#             request.session["failed_attempts"] = 0
#             request.session.pop("locked_until", None)

#             logger.info(f"User {username} logged in succesfully")
#             login(request, user)
#             return redirect("index")
        
#         else:
#             attempts = request.session.get("failed_attempts", 0) + 1
#             request.session["failed_attempts"] = attempts

#             logger.warning(f"Failed login attempt for user {username}. Attempt number: {attempts}")

#         if attempts >= max_attempts:
#             locked_until = timezone.now() + timedelta(minutes=lockedmins)
#             request.session["locked_until"] = locked_until.isoformat()
#             logger.warning(f"Login locked for user {username}")

#             return render(request, "login.html", {"error": "Too many failed attempts. " "Login is locked for 3 minutes."})

#         return render(request, "login.html", {"error": "Invalid username or password."})

#     return render(request, "login.html")

    

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

    if request.method == "POST":
        review.delete()

    return redirect("index")

# Fixed version for A01:

# def delete_review(request, review_id):
#     review = get_object_or_404(Review, id=review_id, user=request.user)
#     # User is included, preventing other users from deleting your post

#     if request.method == "POST":
#         review.delete()

#     return redirect("index")