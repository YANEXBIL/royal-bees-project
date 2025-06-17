from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User # For teacher/admin 'recorded_by' or 'created_by' fields
from django.utils.text import slugify # For auto-generating slugs if needed

# --- Academic Structure Models ---

class AcademicSession(models.Model):
    year = models.CharField(max_length=10, unique=True, help_text="e.g., 2024/2025")
    is_current = models.BooleanField(default=False, help_text="Mark if this is the current academic session.")
    # Consider adding start_date and end_date if needed for more granular control

    class Meta:
        ordering = ['-year']

    def __str__(self):
        return f"{self.year}{' (Current)' if self.is_current else ''}"

    def save(self, *args, **kwargs):
        # Ensure only one session can be current
        if self.is_current:
            AcademicSession.objects.filter(is_current=True).update(is_current=False)
        super().save(*args, **kwargs)


class Term(models.Model):
    name = models.CharField(max_length=20, unique=True, help_text="e.g., First Term, Second Term")
    order = models.PositiveIntegerField(unique=True, help_text="e.g., 1 for First Term, 2 for Second Term")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name


class ClassLevel(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="e.g., Primary 1A, JSS 2B, SSS 3 Science")
    # section = models.CharField(max_length=20, blank=True, null=True, help_text="e.g., A, B, Science, Arts")
    # level_group = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., Primary, Junior Secondary, Senior Secondary")

    class Meta:
        ordering = ['name'] # Or more complex ordering if needed

    def __str__(self):
        return self.name


# --- People & Subject Models ---

class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True, help_text="Unique ID for the student, e.g., RBS00123")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    other_names = models.CharField(max_length=100, blank=True, null=True)
    current_class = models.ForeignKey(ClassLevel, on_delete=models.SET_NULL, null=True, blank=True, related_name="students")
    date_of_birth = models.DateField(null=True, blank=True) # Made optional as per some use cases
    pin = models.CharField(max_length=10, blank=True, null=True, help_text="System-generated PIN for result checking (store securely if student-settable, otherwise can be plain if system-managed)") # Store securely if it's sensitive
    photo = models.ImageField(upload_to='student_photos/', blank=True, null=True)
    active = models.BooleanField(default=True, help_text="Is the student currently enrolled?")
    date_admitted = models.DateField(default=timezone.now)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.last_name}, {self.first_name} ({self.student_id})"

    def get_full_name(self):
        if self.other_names:
            return f"{self.last_name}, {self.first_name} {self.other_names}"
        return f"{self.last_name}, {self.first_name}"


class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)
    subject_code = models.CharField(max_length=20, blank=True, null=True, unique=True)
    # class_levels = models.ManyToManyField(ClassLevel, related_name="subjects_offered", blank=True) # If subjects are tied to specific classes

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


# --- Result Model ---

class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="results")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="results")
    academic_session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, related_name="results")
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="results")
    class_level_at_time_of_result = models.ForeignKey(ClassLevel, on_delete=models.SET_NULL, null=True, related_name="results_for_class")
    
    test_score_1 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="e.g., CA 1 score")
    test_score_2 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="e.g., CA 2 score")
    # Add more CA scores if needed: test_score_3, project_score, etc.
    exam_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    total_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Calculated or entered")
    grade = models.CharField(max_length=5, blank=True, null=True, help_text="e.g., A1, B2, C4 or A, B, C") # Store calculated grade
    remarks = models.TextField(blank=True, null=True)
    
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="results_recorded", help_text="Teacher or admin who entered/updated the result")
    date_recorded = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['student', 'subject', 'academic_session', 'term']] # A student should only have one entry per subject per term per session
        ordering = ['academic_session__year', 'term__order', 'subject__name']

    def __str__(self):
        return f"Result for {self.student} - {self.subject} ({self.academic_session}, {self.term})"

    def calculate_total_score(self):
        # Implement your school's logic for calculating total score
        # Example:
        total = 0
        if self.test_score_1 is not None:
            total += self.test_score_1
        if self.test_score_2 is not None:
            total += self.test_score_2
        if self.exam_score is not None:
            total += self.exam_score
        return total if total > 0 or self.test_score_1 is not None or self.exam_score is not None else None # Return None if no scores entered

    def calculate_grade(self):
        # Implement your school's grading scheme
        # Example:
        if self.total_score is None:
            return None
        if self.total_score >= 75: return 'A1'
        if self.total_score >= 70: return 'B2'
        if self.total_score >= 65: return 'B3'
        if self.total_score >= 60: return 'C4'
        if self.total_score >= 55: return 'C5'
        if self.total_score >= 50: return 'C6'
        if self.total_score >= 45: return 'D7'
        if self.total_score >= 40: return 'E8'
        return 'F9'

    def save(self, *args, **kwargs):
        self.total_score = self.calculate_total_score()
        if self.total_score is not None : # Only calculate grade if total score exists
            self.grade = self.calculate_grade()
        super().save(*args, **kwargs)