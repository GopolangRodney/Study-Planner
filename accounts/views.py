from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db.models.functions import Lower
from .models import Task
from .forms import TaskForm 
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from .forms import UserProfileForm
from datetime import datetime
from .models import Reminder
from django.views.decorators.csrf import csrf_exempt
import json
import requests
from django.core.cache import cache
from django.http import JsonResponse

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})



def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    return render(request, 'accounts/dashboard.html')



def home_redirect(request):
    if request.user.is_authenticated:
        return redirect('dashboard')  # Redirect to dashboard if logged in
    return redirect('login')

def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')  # Redirect to a dashboard page after login
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def profile(request):
    # Fetch the current user instance to populate the form with existing data
    user = request.user
    form = UserProfileForm(instance=user)

    if request.method == 'POST':
        # If the form is submitted with POST request
        form = UserProfileForm(request.POST, instance=user, files=request.FILES)

        if form.is_valid():
            # Save the updated user data
            form.save()

            # Optionally, add a success message
            messages.success(request, "Profile updated successfully!")
            
            # Redirect to the profile page after updating
            return redirect('profile')

    # Return the profile page with the form (either with data or empty)
    return render(request, 'profile.html', {'form': form})

@login_required
def update_profile(request):
    user = request.user
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user)

    return render(request, 'profile.html', {'form': form})

def profile_view(request):
    # Logic to get user tasks or profile details
    tasks = Task.objects.filter(user=request.user)  # Example to get tasks for the user
    return render(request, 'profile.html', {'tasks': tasks})

@login_required
def dashboard(request):
    tasks = Task.objects.filter(user=request.user)
    
    # Calculate completion percentage
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(completed=True).count()
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

    return render(request, 'accounts/dashboard.html', {
        'tasks': tasks,
        'completion_rate': round(completion_rate, 2),
    })

@login_required
def add_task(request):
    if request.method == 'POST':
        title = request.POST['title']
        due_date = request.POST['due_date']
        priority = request.POST['priority']
        Task.objects.create(user=request.user, title=title, due_date=due_date, priority=priority)
    return redirect('dashboard')

@csrf_exempt
@login_required
def delete_task(request, task_title):
    if request.method == 'POST':
        try:
            task = Task.objects.get(user=request.user, title=task_title)
            task.delete()
            return redirect('dashboard')  # Change 'dashboard' to your actual URL name
        except Task.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Task not found or already deleted!'})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)
        
def calendar(request):
    # Add any necessary context for the calendar page
    return render(request, 'accounts/calendar.html')

# TEMPORARY: Save in memory (replace with database later)
reminder_data = {}



@login_required
def calendar_view(request):
    return render(request, 'calendar.html')

@login_required
def get_reminders(request):
    user = request.user
    reminders = Reminder.objects.filter(user=user).values('date', 'note')
    reminder_dict = {reminder['date'].strftime('%Y-%m-%d'): reminder['note'] for reminder in reminders}
    return JsonResponse(reminder_dict)

@csrf_exempt
@login_required
def save_reminder(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        date = data['date']
        note = data['note']
        
        reminder, created = Reminder.objects.get_or_create(user=request.user, date=date)
        reminder.note = note
        reminder.save()
        
        return JsonResponse({"message": "Reminder saved successfully"})
    return JsonResponse({"error": "Invalid request"}, status=400)


import requests
from django.shortcuts import render
from django.core.cache import cache

def motivational_quotes(request):
    # Attempt to fetch the quotes from cache
    quotes = cache.get('motivational_quotes')

    if not quotes:
        # Fetch multiple quotes if cache is empty
        api_url = 'https://zenquotes.io/api/quotes'  # Use an endpoint that returns multiple quotes
        response = requests.get(api_url)
        
        if response.status_code == 200:
            quotes_data = response.json()
            quotes = [
                {'text': quote['q'], 'author': quote['a']} for quote in quotes_data
            ]
            cache.set('motivational_quotes', quotes, timeout=86400)  # Cache for 1 day
        else:
            quotes = [{'text': 'Could not retrieve quotes at this time.', 'author': ''}]
    
    # Get the index for the current quote
    current_index = int(request.GET.get('index', 0))

    # Ensure the index is within bounds
    current_index = max(0, min(current_index, len(quotes) - 1))

    # Get the current quote
    current_quote = quotes[current_index]

    # Fetch a random inspirational image URL from Unsplash API
    image_url = get_random_inspirational_image()

    # Render the template with the quote and background image
    return render(request, 'accounts/motivational_quotes.html', {
        'quote': current_quote,
        'quotes': quotes,
        'current_index': current_index,
        'image_url': image_url,
    })

def motivational_quotes(request):
    # Attempt to fetch the quotes from cache
    quotes = cache.get('motivational_quotes')

    if not quotes:
        # Fetch multiple quotes if cache is empty
        api_url = 'https://zenquotes.io/api/quotes'  # Use an endpoint that returns multiple quotes
        response = requests.get(api_url)
        
        if response.status_code == 200:
            quotes_data = response.json()
            quotes = [
                {'text': quote['q'], 'author': quote['a']} for quote in quotes_data
            ]
            cache.set('motivational_quotes', quotes, timeout=86400)  # Cache for 1 day
        else:
            quotes = [{'text': 'Could not retrieve quotes at this time.', 'author': ''}]
    
    # Get the index for the current quote
    current_index = int(request.GET.get('index', 0))

    # Ensure the index is within bounds
    current_index = max(0, min(current_index, len(quotes) - 1))

    # Get the current quote
    current_quote = quotes[current_index]

    # Fetch a random inspirational image URL from Unsplash API
    image_url = get_random_inspirational_image()

    # Render the template with the quote and background image
    return render(request, 'accounts/motivational_quotes.html', {
        'quote': current_quote,
        'quotes': quotes,
        'current_index': current_index,
        'image_url': image_url,
    })

import requests
from django.shortcuts import render
from django.core.cache import cache

def motivational_quotes(request):
    # Attempt to fetch the quotes from cache
    quotes = cache.get('motivational_quotes')

    if not quotes:
        # Fetch multiple quotes if cache is empty
        api_url = 'https://zenquotes.io/api/quotes'  # Use an endpoint that returns multiple quotes
        response = requests.get(api_url)
        
        if response.status_code == 200:
            quotes_data = response.json()
            quotes = [
                {'text': quote['q'], 'author': quote['a']} for quote in quotes_data
            ]
            cache.set('motivational_quotes', quotes, timeout=86400)  # Cache for 1 day
        else:
            quotes = [{'text': 'Could not retrieve quotes at this time.', 'author': ''}]
    
    # Get the index for the current quote
    current_index = int(request.GET.get('index', 0))

    # Ensure the index is within bounds
    current_index = max(0, min(current_index, len(quotes) - 1))

    # Get the current quote
    current_quote = quotes[current_index]

    # Fetch a random inspirational image from Pexels API
    image_url = get_random_inspirational_image()

    return render(request, 'accounts/motivational_quotes.html', {
        'quote': current_quote,
        'quotes': quotes,
        'current_index': current_index,
        'image_url': image_url,  # Pass the image URL to the template
    })

import requests
from django.shortcuts import render
from django.core.cache import cache

def motivational_quotes(request):
    # Attempt to fetch the quotes from cache
    quotes = cache.get('motivational_quotes')

    if not quotes:
        # Fetch multiple quotes if cache is empty
        api_url = 'https://zenquotes.io/api/quotes'  # Use an endpoint that returns multiple quotes
        response = requests.get(api_url)
        
        if response.status_code == 200:
            quotes_data = response.json()
            quotes = [
                {'text': quote['q'], 'author': quote['a']} for quote in quotes_data
            ]
            cache.set('motivational_quotes', quotes, timeout=86400)  # Cache for 1 day
        else:
            quotes = [{'text': 'Could not retrieve quotes at this time.', 'author': ''}]
    
    # Get the index for the current quote
    current_index = int(request.GET.get('index', 0))

    # Ensure the index is within bounds
    current_index = max(0, min(current_index, len(quotes) - 1))

    # Get the current quote
    current_quote = quotes[current_index]

    # Fetch a random inspirational image from Pixabay API
    image_url = get_random_inspirational_image()

    return render(request, 'accounts/motivational_quotes.html', {
        'quote': current_quote,
        'quotes': quotes,
        'current_index': current_index,
        'image_url': image_url,  # Pass the image URL to the template
    })

def get_random_inspirational_image():
    # Pixabay API endpoint to fetch random images
    pixabay_url = 'https://pixabay.com/api/'
    params = {
        'key': '49659185-22eb9807974443879a2968b51',  # Your Pixabay API key
        'q': 'inspiration',  # Search term
        'per_page': 1  # Fetch 1 image per request
    }

    response = requests.get(pixabay_url, params=params)
    if response.status_code == 200:
        image_data = response.json()
        if image_data and image_data.get('hits'):
            return image_data['hits'][0]['largeImageURL']  # Return the large image URL
    return 'https://via.placeholder.com/1200x800.png?text=Inspirational+Image'  # Fallback image if Pixabay fails

@login_required
def settings_view(request):
    return render(request, 'accounts/settings.html')
