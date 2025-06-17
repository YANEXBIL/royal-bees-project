from django.contrib import admin
from .models import AcademicSession, Term, ClassLevel, Student, Subject, Result

@admin.register(AcademicSession)
class AcademicSessionAdmin(admin.ModelAdmin):
    list_display = ('year', 'is_current')
    list_editable = ('is_current',) # Allows editing 'is_current' directly in the list view
    list_filter = ('is_current',)

@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    ordering = ('order',)

@admin.register(ClassLevel)
class ClassLevelAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'student_id', 'current_class', 'active', 'pin') # Added pin for visibility
    list_filter = ('current_class', 'active')
    search_fields = ('first_name', 'last_name', 'student_id', 'other_names')
    list_editable = ('active', 'current_class', 'pin') # Be cautious with pin editable here if it's sensitive
    readonly_fields = ('date_admitted',)
    fieldsets = (
        ('Personal Information', {
            'fields': ('student_id', 'first_name', 'last_name', 'other_names', 'date_of_birth', 'photo')
        }),
        ('Academic Information', {
            'fields': ('current_class', 'pin', 'active', 'date_admitted')
        }),
    )
    ordering = ('last_name', 'first_name')

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject_code')
    search_fields = ('name', 'subject_code')
    ordering = ('name',)

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'academic_session', 'term', 'total_score', 'grade', 'class_level_at_time_of_result', 'recorded_by')
    list_filter = ('academic_session', 'term', 'subject__name', 'grade', 'class_level_at_time_of_result__name', 'recorded_by')
    search_fields = ('student__first_name', 'student__last_name', 'student__student_id', 'subject__name')
    readonly_fields = ('total_score', 'grade', 'date_recorded', 'date_updated') # These are auto-calculated or auto-set
    fieldsets = (
        (None, {
            'fields': ('student', 'subject', 'academic_session', 'term', 'class_level_at_time_of_result')
        }),
        ('Scores', {
            'fields': (('test_score_1', 'test_score_2'), 'exam_score') # Grouping scores
        }),
        ('Calculated & Audit', {
            'classes': ('collapse',),
            'fields': ('total_score', 'grade', 'remarks', 'recorded_by', 'date_recorded', 'date_updated')
        }),
    )
    # For large numbers of students/subjects, raw_id_fields can improve performance:
    # raw_id_fields = ('student', 'subject', 'recorded_by', 'academic_session', 'term', 'class_level_at_time_of_result')
    autocomplete_fields = ['student', 'subject'] # More user-friendly than raw_id_fields if search_fields are set on Student/Subject admin

    def get_queryset(self, request):
        # Optimize queries by prefetching related objects
        return super().get_queryset(request).select_related(
            'student', 'subject', 'academic_session', 'term', 'class_level_at_time_of_result', 'recorded_by'
        )