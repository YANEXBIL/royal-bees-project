# results/urls.py
from django.urls import path
from . import views # We'll create views in the next step

app_name = 'results' # Namespacing the URLs

urlpatterns = [
    path('check/', views.check_result_view, name='check_results'), # <--- ADD COMMA HERE!
    path('teacher/entry/search-student/', views.teacher_search_student_view, name='teacher_search_student'),
    path('teacher/entry/select-session-term/<int:student_id>/', views.teacher_select_session_term_view, name='teacher_select_session_term'),
] # Also, best practice is to have a trailing comma after the last item in a list, but the missing one in the middle was the critical error.