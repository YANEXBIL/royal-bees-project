# royal_bees_project/core/views.py

from django.shortcuts import render, get_object_or_404
from .models import NewsItem, Event # Make sure Event and NewsItem are imported
from django.utils import timezone # For filtering upcoming events

# --- Existing Views ---
def home_view(request):
    # Fetch recent news items (e.g., top 3 latest news)
    # Order by '-published_date' to get the newest first
    latest_news = NewsItem.objects.all().order_by('-published_date')[:3]

    # Fetch upcoming events (e.g., top 3 upcoming events)
    # Filter for events starting from now or in the future
    upcoming_events = Event.objects.filter(start_datetime__gte=timezone.now()).order_by('start_datetime')[:3]

    context = {
        'latest_news': latest_news,
        'upcoming_events': upcoming_events,
        'page_title': 'Home' # You can set a specific title for your home page
    }
    return render(request, 'core/index.html', context) # Pass the context here

def about_view(request):
    return render(request, 'core/about.html')

def contact_us_view(request): # This name is now consistent with urls.py
    return render(request, 'core/contact.html', {'page_title': 'Contact Us'})
    #                                  ^^^^^^^^^
    #                              Changed to contact.html

# --- News Views ---
def news_list_view(request):
    news_items = NewsItem.objects.all().order_by('-published_date') # Order by date for consistency
    context = {
        'news_items': news_items,
        'page_title': 'News & Announcements'
    }
    return render(request, 'core/news_list.html', context)

def news_detail_view(request, year, month, day, slug):
    news_item = get_object_or_404(NewsItem,
                                   slug=slug,
                                   published_date__year=year,
                                   published_date__month=month,
                                   published_date__day=day)
    context = {
        'news_item': news_item,
        'page_title': news_item.title # Set page title dynamically
    }
    return render(request, 'core/news_detail.html', context)

# --- Event Views ---
def event_list_view(request):
    upcoming_events = Event.objects.filter(start_datetime__gte=timezone.now()).order_by('start_datetime')
    past_events = Event.objects.filter(start_datetime__lt=timezone.now()).order_by('-start_datetime')

    context = {
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        'page_title': 'School Events'
    }
    return render(request, 'core/event_list.html', context)

def event_detail_view(request, year, month, day, slug):
    event = get_object_or_404(Event,
                               slug=slug,
                               start_datetime__year=year,
                               start_datetime__month=month,
                               start_datetime__day=day)
    context = {
        'event': event,
        'page_title': event.title # Set page title dynamically
    }
    return render(request, 'core/event_detail.html', context)

# --- Academics Views ---
def academics_overview_view(request):
    context = {
        'page_title': 'Academics Overview'
    }
    return render(request, 'core/academics_overview.html', context)

def curriculum_view(request):
    context = {
        'page_title': 'Our Curriculum'
    }
    return render(request, 'core/curriculum.html', context)

def departments_view(request):
    departments_list = [
        {'name': 'Science Department', 'head': 'Dr. B. Adebayo', 'description': 'Focusing on Physics, Chemistry, Biology and Integrated Science.'},
        {'name': 'Mathematics Department', 'head': 'Mrs. C. Eze', 'description': 'Covering all aspects of Mathematics from Basic to Advanced.'},
        {'name': 'Languages Department', 'head': 'Mr. A. Okoro', 'description': 'English, Yoruba, Igbo, Hausa, French and Literature.'},
        {'name': 'Humanities & Social Sciences', 'head': 'Ms. F. Bello', 'description': 'History, Government, Economics, Geography, Social Studies.'},
    ]
    context = {
        'page_title': 'Academic Departments',
        'departments': departments_list
    }
    return render(request, 'core/departments.html', context)

def admissions_view(request):
    context = {
        'page_title': 'Admissions Information'
    }
    return render(request, 'core/admissions.html', context)

def gallery_view(request):
    context = {
        'page_title': 'School Gallery',
    }
    return render(request, 'core/gallery.html', context)

def academic_calendar_view(request):
    context = {
        'page_title': 'Academic Calendar'
    }
    return render(request, 'core/academic_calendar.html', context)