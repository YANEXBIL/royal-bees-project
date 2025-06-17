# results/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import AcademicSession, Term, Student, Result, Subject
from django.db.models import Q
from django.forms import formset_factory
from .forms import ScoreEntryForm
from django.contrib import messages
def check_result_view(request):
    error_message = None
    student_id_input = '' 

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        pin = request.POST.get('pin')

        print(f"\n--- DEBUG: POST Request Received ---")
        print(f"Entered Student ID: '{student_id}'")
        print(f"Entered PIN: '{pin}'")
        print(f"-----------------------------------\n")

        student_id_input = student_id 

        try:
            student_found = Student.objects.get(student_id=student_id) 

            print(f"\n--- DEBUG: Student Found ---")
            print(f"DB Student ID: '{student_found.student_id}'")
            print(f"DB PIN: '{student_found.pin}'")
            print(f"Comparing Entered PIN ('{pin}') with DB PIN ('{student_found.pin}')")
            print(f"Result of comparison: {student_found.pin == pin}")
            print(f"----------------------------\n")
            
            if student_found.pin == pin:
                results = student_found.results.all().select_related('subject', 'academic_session', 'term')
                
                current_session = None
                current_term = None
                if results.exists():
                    latest_result = results.latest('academic_session__year', 'term__order')
                    current_session = latest_result.academic_session
                    current_term = latest_result.term

                print(f"\n--- DEBUG: Credentials Valid! Rendering display_results.html ---")
                return render(request, 'results/display_results.html', {
                    'student': student_found,
                    'results': results,
                    'academic_session': current_session,
                    'current_term': current_term,
                })
            else:
                error_message = "Invalid Student ID or PIN."
                print(f"\n--- DEBUG: PIN Mismatch. Error: {error_message} ---")
        except Student.DoesNotExist:
            error_message = "Invalid Student ID or PIN."
            print(f"\n--- DEBUG: Student ID Not Found. Error: {error_message} ---")
        # --- TEMPORARILY REMOVE THIS GENERIC EXCEPTION BLOCK TO SEE FULL TRACEBACK ---
        # except Exception as e:
        #     error_message = f"An unexpected error occurred: {e}"
        #     print(f"\n--- DEBUG: Caught unexpected exception: {e} ---")
        # -----------------------------------------------------------------------------
    
    print(f"\n--- DEBUG: Rendering check_result_form.html (GET or POST Failed) ---")
    return render(request, 'results/check_result_form.html', {
        'error_message': error_message,
        'student_id_input': request.POST.get('student_id', '')
    })

def teacher_search_student_view(request):
    students_found = None
    search_query = "" 

    if request.method == 'POST': 
        search_query = request.POST.get('search_query', '').strip()
        if search_query:
            students_found = Student.objects.filter(
                Q(student_id__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(other_names__icontains=search_query)
            ).filter(active=True).select_related('current_class')
            
            if not students_found.exists():
                messages.info(request, f"No students found matching your search query: '{search_query}'.")
        else: 
             messages.info(request, "Please enter a search term.") # Message if POSTed with empty query
    
    context = {
        'page_title': 'Result Entry - Search Student',
        'students_found': students_found,
        'search_query': search_query,
    }
    return render(request, 'results/teacher_student_search.html', context)


# @login_required
# @permission_required('results.add_result', raise_exception=True) 
def teacher_select_session_term_view(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    
    sessions_list = AcademicSession.objects.all().order_by('-year')
    terms_list = Term.objects.all().order_by('order')
    current_session_obj = AcademicSession.objects.filter(is_current=True).first()

    ScoreEntryFormSet = formset_factory(ScoreEntryForm, extra=0)

    if request.method == 'POST':
        if 'save_scores' in request.POST:
            # --- This block handles the SUBMISSION of the score formset ---
            posted_session_id = request.POST.get('posted_academic_session_id')
            posted_term_id = request.POST.get('posted_term_id')

            if not posted_session_id or not posted_term_id:
                messages.error(request, "Session or Term ID was missing during score saving. Please try selecting again.")
                return redirect('results:teacher_select_session_term', student_id=student.id)

            selected_session = get_object_or_404(AcademicSession, pk=posted_session_id)
            selected_term = get_object_or_404(Term, pk=posted_term_id)
            
            score_formset_submitted = ScoreEntryFormSet(request.POST, prefix='scores')

            if score_formset_submitted.is_valid():
                all_saved_successfully = True
                for form in score_formset_submitted: 
                    if form.has_changed(): # Process only forms that have data or were changed
                        cleaned_data = form.cleaned_data
                        subject_id = cleaned_data.get('subject_id')
                        if not subject_id: 
                            messages.warning(request, "A score entry was skipped (missing subject ID).")
                            all_saved_successfully = False # Mark as not fully successful
                            continue
                            
                        subject = get_object_or_404(Subject, pk=subject_id)
                        
                        defaults = {
                            'class_level_at_time_of_result': student.current_class, 
                            'test_score_1': cleaned_data.get('test_score_1'),
                            'test_score_2': cleaned_data.get('test_score_2'),
                            'exam_score': cleaned_data.get('exam_score'),
                            'remarks': cleaned_data.get('remarks', ''),
                            'recorded_by': request.user if request.user.is_authenticated else None
                        }
                        # Filter out None values for score fields that cannot be null in the model,
                        # but allow remarks to be empty string.
                        # This assumes score fields in model can be null or you handle None->0 conversion.
                        defaults_filtered = {k: v for k, v in defaults.items() if v is not None or k == 'remarks'}

                        try:
                            Result.objects.update_or_create(
                                student=student, subject=subject,
                                academic_session=selected_session, term=selected_term,
                                defaults=defaults_filtered
                            )
                        except Exception as e:
                            messages.error(request, f"Error saving scores for {subject.name}: {e}")
                            all_saved_successfully = False
                
                if all_saved_successfully:
                    messages.success(request, f"Scores for {student.get_full_name()} ({selected_session.year} - {selected_term.name}) processed.")
                else:
                    messages.warning(request, f"Some scores for {student.get_full_name()} may not have saved or updated correctly. Please review.")
                
                return redirect('results:teacher_search_student') 
            else:
                # Formset is not valid, re-render the page with the formset containing errors
                messages.error(request, "There were errors in the scores submitted. Please correct them and resubmit.")
                # Pass back the invalid formset and other necessary context to re-render the page
                context = {
                    'page_title': f'Enter Scores for {student.get_full_name()} (Errors)',
                    'student': student,
                    'selected_session': selected_session, 
                    'selected_term': selected_term,       
                    'score_formset': score_formset_submitted, # The formset with errors
                }
                return render(request, 'results/teacher_score_entry_form.html', context)
        else: 
            # --- This POST is from selecting session/term to DISPLAY formset ---
            session_id = request.POST.get('academic_session')
            term_id = request.POST.get('term')

            if session_id and term_id: 
                selected_session = get_object_or_404(AcademicSession, pk=session_id)
                selected_term = get_object_or_404(Term, pk=term_id)

                # TODO: Refine subject fetching (e.g., subjects for student.current_class)
                subjects_for_formset = Subject.objects.all().order_by('name') 
                
                initial_formset_data = []
                for sub in subjects_for_formset:
                    existing_result = Result.objects.filter(
                        student=student, subject=sub,
                        academic_session=selected_session, term=selected_term
                    ).first()
                    data_row = {'subject_id': sub.id, 'subject_name_display': sub.name}
                    if existing_result:
                        data_row.update({
                            'test_score_1': existing_result.test_score_1,
                            'test_score_2': existing_result.test_score_2,
                            'exam_score': existing_result.exam_score,
                            'remarks': existing_result.remarks,
                        })
                    initial_formset_data.append(data_row)
                
                score_formset_instance = ScoreEntryFormSet(initial=initial_formset_data, prefix='scores')

                context = {
                    'page_title': f'Enter Scores for {student.get_full_name()}',
                    'student': student,
                    'selected_session': selected_session,
                    'selected_term': selected_term,
                    'score_formset': score_formset_instance,
                }
                return render(request, 'results/teacher_score_entry_form.html', context)
            else: 
                # Error in session/term selection form submission (session_id or term_id missing)
                context = {
                    'page_title': f'Select Session/Term for {student.get_full_name()}',
                    'student': student,
                    'sessions': sessions_list, 
                    'terms': terms_list,         
                    'current_session': current_session_obj,
                    'error_message': 'Please select both Academic Session and Term to proceed.'
                }
                return render(request, 'results/teacher_select_session_term.html', context)
    else: # request.method == 'GET' (for teacher_select_session_term_view)
        context = {
            'page_title': f'Select Session/Term for {student.get_full_name()}',
            'student': student,
            'sessions': sessions_list,
            'terms': terms_list,
            'current_session': current_session_obj,
        }
        return render(request, 'results/teacher_select_session_term.html', context)