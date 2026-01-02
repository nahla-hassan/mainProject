from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .forms import TeacherRegistrationForm, StudentRegistrationForm,StudentForm,TeacherForm,AssignDivisionForm,SubjectForm,StudyMaterialForm
from .models import UserRole, Teacher, Student,ClassDivision,Notification,Subject,TimeTableEntry,StudyMaterial,Marks,Attendance
import csv
import io
from django.db.models import Avg
from django.http import FileResponse
from datetime import date, timedelta
from django.utils import timezone
from django.db.models import Q


def home(request):
    return render(request, 'home.html')


def teacher_register(request):
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST)
        if form.is_valid():
            # Create user
            user = form.save(commit=False)
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()
            
            # Create UserRole
            UserRole.objects.create(user=user, role='teacher')
            
            # Create Teacher profile
            Teacher.objects.create(
                user=user,
                phone=form.cleaned_data['phone'],
                qualification=form.cleaned_data['qualification'],
                address=form.cleaned_data['address'],
                class_to_handle=form.cleaned_data.get('class_to_handle', '')
            )
            
            messages.success(request, 'Teacher registration successful! Please login.')
            return redirect('manage_teachers')
    else:
        form = TeacherRegistrationForm()
    
    return render(request, 'register_teacher.html', {'form': form})


def student_register(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            # Create user
            user = form.save(commit=False)
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            
            # Create UserRole
            UserRole.objects.create(user=user, role='student')
            
            # Create Student profile
            Student.objects.create(
                user=user,
                roll_number=form.cleaned_data['roll_number'],
                student_class=form.cleaned_data['student_class'],
                division=form.cleaned_data['division'],
                date_of_birth=form.cleaned_data['date_of_birth'],
                gender=form.cleaned_data['gender'],
                parent_contact=form.cleaned_data['parent_contact'],
                address=form.cleaned_data['address']
            )
            
            messages.success(request, 'Student registration successful! Please login.')
            return redirect('manage_students')
    else:
        form = StudentRegistrationForm()
    
    return render(request, 'register_student.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Get user role and redirect accordingly
            try:
                user_role = UserRole.objects.get(user=user)
                
                if user_role.role == 'admin':
                    return redirect('admin_dashboard')
                elif user_role.role == 'teacher':
                    return redirect('teacher_dashboard')
                elif user_role.role == 'student':
                    return redirect('student_dashboard')
                else:
                    messages.error(request, 'Invalid user role.')
                    logout(request)
                    return redirect('login')
            except UserRole.DoesNotExist:
                messages.error(request, 'User role not found.')
                logout(request)
                return redirect('login')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'login.html')


@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('login')


# Dashboard views (placeholder - customize as needed)
@login_required
def admin_dashboard(request):
    # Access control: only admin
    if not hasattr(request.user, 'user_role') or request.user.user_role.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('login')
    
    # Summary data for cards
    total_students = Student.objects.count()
    total_teachers = Teacher.objects.count()
    total_classes = ClassDivision.objects.values('class_name').distinct().count()
    
    # List of teachers for the table
    teachers = Teacher.objects.all()
    
    context = {
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_classes': total_classes,
        'teachers': teachers,
    }
    
    return render(request, 'admin_dashboard.html', context)



@login_required
def teacher_dashboard(request):
    if not hasattr(request.user, 'user_role') or request.user.user_role.role != 'teacher':
        messages.error(request, 'Access denied.')
        return redirect('login')
    teacher = request.user.teacher_profile

    return render(request, 'teacher_dashboard.html', {
        "teacher": teacher,
        "total_students": 142,
        "subjects_assigned": teacher.subjects.count(),
        "today_classes": 6,
        "today_class_count": 3,
    })

@login_required
def user_logout(request):
    logout(request)
    return redirect('login')


@login_required
def student_dashboard(request):
    if not hasattr(request.user, 'user_role') or request.user.user_role.role != 'student':
        messages.error(request, 'Access denied.')
        return redirect('login')
    student = request.user.student_profile
    return render(request, 'student_dashboard.html', {'student': student})


def manage_students(request):
    return render(request, 'student_management.html')


@login_required
def student_view(request):
    students = Student.objects.none()

    class_filter = request.GET.get('class')
    division_filter = request.GET.get('division')

    if class_filter and division_filter:
        students = Student.objects.filter(
            student_class=class_filter,
            division=division_filter
        )

    return render(request, 'student_view.html', {
        'students': students,
        'selected_class': class_filter,
        'selected_division': division_filter
    })


@login_required
def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, f'Student {student.user.get_full_name()} updated successfully!')
            return redirect('student_view')
    else:
        form = StudentForm(instance=student)

    return render(request, 'edit_student.html', {'form': form, 'student': student})

@login_required
def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    if request.method == 'POST':
        full_name = f"{student.user.first_name} {student.user.last_name}"
        student.delete()
        messages.success(request, f'Student {full_name} deleted successfully!')
        return redirect('student_view')

    return render(request, 'delete_student.html', {'student': student})




def manage_teachers(request):
    return render(request, 'teacher_management.html')

@login_required
def teacher_view(request):
    teachers = Teacher.objects.all()

    class_filter = request.GET.get('class_to_handle')

    # Apply filters only if values are provided
    if class_filter:
        teachers = teachers.filter(class_to_handle=class_filter)


    return render(request, 'view_teacher.html', {
        'teachers': teachers,
        'selected_class': class_filter
    })


@login_required
def edit_teacher(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)

    if request.method == 'POST':
        form = TeacherForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, f'Teacher {teacher.user.get_full_name()} updated successfully!')
            return redirect('teacher_view')
    else:
        form = TeacherForm(instance=teacher)
        form.fields['join_date'].disabled = True

    return render(request, 'edit_teacher.html', {'form': form, 'teacher': teacher})

@login_required
def delete_teacher(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)

    if request.method == 'POST':
        full_name = f"{teacher.user.first_name} {teacher.user.last_name}"
        teacher.delete()
        messages.success(request, f'Teacher {full_name} deleted successfully!')
        return redirect('teacher_view')

    return render(request, 'delete_teacher.html', {'teacher': teacher})



@login_required
def teacher_list(request):
    if not hasattr(request.user, 'user_role') or request.user.user_role.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('login')

    teachers = Teacher.objects.all()
    return render(request, 'teacher_list.html', {'teachers': teachers})

@login_required
def assign_divisions(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)

    if request.method == 'POST':
        form = AssignDivisionForm(request.POST, instance=teacher)
        if form.is_valid():
            # Save assigned divisions
            teacher.assigned_divisions.set(form.cleaned_data['assigned_divisions'])
            teacher.save()  # save first for M2M relations
            # Save multiple subjects
            teacher.subjects.set(form.cleaned_data['subjects'])

            messages.success(request, 'Divisions and subjects assigned successfully.')
            return redirect('teacher_list')
    else:
        form = AssignDivisionForm(instance=teacher)

    return render(request, 'assign_divisions.html', {
        'teacher': teacher,
        'form': form
    })


@login_required
def create_notification(request):
    if not hasattr(request.user, 'user_role') or request.user.user_role.role != 'admin':
        messages.error(request, "Access denied.")
        return redirect('login')

    if request.method == 'POST':
        message_text = request.POST.get('message')
        recipient_type = request.POST.get('recipient_type')
        attachment = request.FILES.get('attachment')  # get the uploaded PDF

        if message_text and recipient_type:
            notif = Notification.objects.create(
                message=message_text,
                recipient_type=recipient_type,
                attachment=attachment  # Save attachment if uploaded
            )
            messages.success(request, "Notification sent successfully!")
            return redirect('create_notification')

    return render(request, 'create_notification.html')



def subject_list(request):
    class_filter = request.GET.get('class_name')
    if class_filter:
        subjects = Subject.objects.filter(class_name=class_filter).order_by('name')
    else:
        subjects = Subject.objects.all().order_by('class_name', 'name')
    
    class_choices = [str(i) for i in range(1, 11)]  # 1-10 as strings
    return render(request, 'subject_list.html', {
        'subjects': subjects,
        'class_filter': class_filter,
        'class_choices': class_choices
    })


def subject_create(request):
    form = SubjectForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Subject added successfully!")
        return redirect('subject-list')
    return render(request, 'subject_form.html', {'form': form, 'title': 'Add Subject'})

def subject_update(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    form = SubjectForm(request.POST or None, instance=subject)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Subject updated successfully!")
        return redirect('subject-list')
    return render(request, 'subject_form.html', {'form': form, 'title': 'Edit Subject'})

def subject_delete(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        subject.delete()
        messages.success(request, "Subject deleted successfully!")
        return redirect('subject-list')
    return render(request, 'subject_confirm_delete.html', {'subject': subject})



@login_required
def upload_common_timetable(request):
    if request.method == "POST":
        file = request.FILES.get('csv_file')
        if not file.name.endswith('.csv'):
            messages.error(request, "Only CSV files allowed!")
            return render(request, 'upload_common_timetable.html')

        # Read CSV
        decoded_file = file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)

        # Clear old timetable (optional)
        TimeTableEntry.objects.all().delete()

        # Save each row into the database
        for row in reader:
            TimeTableEntry.objects.create(
                class_name=row['class'],
                division=row['division'],
                day=row['day'],
                period=row['period'],
                subject=row['subject'] or '-',
                teacher=row['teacher']
            )

        messages.success(request, "Timetable uploaded successfully!")
        return redirect('admin_dashboard')

    return render(request, 'upload_common_timetable.html')



from django.shortcuts import render
from .models import Student, Attendance, ClassDivision
from django.db.models import Count

@login_required
def admin_attendance_report(request):
    # Get filters from GET request
    selected_class = request.GET.get("class")
    selected_division = request.GET.get("division")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    # Get all classes/divisions for dropdowns
    classes = ClassDivision.objects.values_list("class_name", flat=True).distinct()
    divisions = ClassDivision.objects.values_list("division", flat=True).distinct()

    # Base queryset for students
    students_qs = Student.objects.all()
    if selected_class:
        students_qs = students_qs.filter(student_class=selected_class)
    if selected_division:
        students_qs = students_qs.filter(division=selected_division)

    # Prepare summary
    attendance_summary = []

    for student_class in students_qs.values_list('student_class', flat=True).distinct():
        for division in students_qs.filter(student_class=student_class).values_list('division', flat=True).distinct():
            class_students = students_qs.filter(student_class=student_class, division=division)
            total_students = class_students.count()

            # Attendance in date range
            attendance_qs = Attendance.objects.filter(
                student__in=class_students
            )
            if start_date and end_date:
                attendance_qs = attendance_qs.filter(date__range=[start_date, end_date])

            present_count = attendance_qs.filter(status="Present").count()
            absent_count = attendance_qs.filter(status="Absent").count()

            # Avoid division by zero
            if total_students > 0:
                divisor = total_students if attendance_qs.count() == 0 else attendance_qs.count() / total_students
                present_percent = round((present_count / (total_students * divisor)) * 100, 2)
                absent_percent = round(100 - present_percent, 2)
            else:
                present_percent = 0.00
                absent_percent = 0.00

            attendance_summary.append({
                "class_name": f"{student_class}{division}",
                "total_students": total_students,
                "present_percent": present_percent,
                "absent_percent": absent_percent
            })

    context = {
        "classes": classes,
        "divisions": divisions,
        "selected_class": selected_class,
        "selected_division": selected_division,
        "start_date": start_date,
        "end_date": end_date,
        "attendance_summary": attendance_summary
    }

    return render(request, "attendance_report.html", context)






def admin_exam_report(request):
    # Get all classes
    classes = Student.objects.values_list('student_class', flat=True).distinct().order_by('student_class')
    
    selected_class = request.GET.get('class_name', '')

    # Base queryset
    marks_qs = Marks.objects.all()

    # Filter by class
    if selected_class:
        students_in_class = Student.objects.filter(student_class=selected_class)
        marks_qs = marks_qs.filter(student__in=students_in_class)
    
    # Compute average per class
    summary = []
    class_list = [selected_class] if selected_class else classes

    for cls in class_list:
        students_in_cls = Student.objects.filter(student_class=cls)
        total_students = students_in_cls.count()
        if total_students == 0:
            continue

        avg_marks = marks_qs.filter(student__student_class=cls).aggregate(avg=Avg('marks'))['avg']
        avg_marks = round(avg_marks or 0, 2)
        
        summary.append({
            'class_name': cls,
            'total_students': total_students,
            'average_marks': avg_marks
        })

    context = {
        'classes': classes,
        'marks_summary': summary,
        'selected_class': selected_class
    }
    return render(request, 'admin_exam_report.html', context)



@login_required
def view_teacher_timetable(request):
    teacher = request.user.teacher_profile
    teacher_name = teacher.user.get_full_name().strip()

    # Get all rows for this teacher
    teacher_rows = list(TimeTableEntry.objects.filter(teacher=teacher_name))

    if teacher_rows:
        DAY_ORDER = {
            "Monday": 1,
            "Tuesday": 2,
            "Wednesday": 3,
            "Thursday": 4,
            "Friday": 5
        }

        # Sort by day order and period (convert period to int if needed)
        teacher_rows = sorted(
            teacher_rows,
            key=lambda row: (DAY_ORDER.get(row.day, 99), int(row.period))
        )

    # Now teacher_rows is always defined (even if empty)
    return render(request, "teacher_timetable.html", {
        "timetable": teacher_rows,
        "teacher_name": teacher_name
    })


@login_required
def teacher_notifications(request):
    # Fetch notifications for teachers or all users
    notifications = Notification.objects.filter(
        recipient_type__in=['teachers', 'all']
    ).order_by('-created_at')  # newest first

    return render(request, 'teacher_notifications.html', {
        'notifications': notifications
    })


def upload_study_material(request):
    teacher = getattr(request.user, 'teacher_profile', None)  # logged-in teacher

    if request.method == "POST":
        form = StudyMaterialForm(request.POST, request.FILES, teacher=teacher)
        if form.is_valid():
            material = form.save(commit=False)
            material.uploaded_by = teacher
            material.save()
            messages.success(request, "Study material uploaded successfully!")
            return redirect('teacher_dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = StudyMaterialForm(teacher=teacher)

    return render(request, 'upload_study_material.html', {'form': form})




@login_required
def mark_attendance(request):
    teacher = request.user.teacher_profile
    teacher_divs = teacher.assigned_divisions.all()
    
    students = Student.objects.filter(
        student_class__in=[d.class_name for d in teacher_divs],
        division__in=[d.division for d in teacher_divs]
    )

    if request.method == "POST":
        date = request.POST.get("date")
        for student in students:
            status = request.POST.get(f"status_{student.id}")
            if status:
                Attendance.objects.update_or_create(
                    student=student,
                    date=date,
                    defaults={'status': status}
                )
        messages.success(request, f"Attendance saved for {date}!")
        return redirect('teacher_dashboard')

    return render(request, "mark_attendance.html", {"students": students})



@login_required
def enter_marks(request):
    teacher = request.user.teacher_profile
    teacher_divs = teacher.assigned_divisions.all()
    
    students = Student.objects.filter(
        student_class__in=[d.class_name for d in teacher_divs],
        division__in=[d.division for d in teacher_divs]
    )

    subjects = teacher.subjects.all()

    if request.method == "POST":
        subject_id = request.POST.get("subject")
        subject = Subject.objects.get(id=subject_id)
        
        for student in students:
            marks_value = request.POST.get(f"marks_{student.id}")
            if marks_value:
                Marks.objects.update_or_create(
                    student=student,
                    subject=subject,
                    defaults={'marks': marks_value}
                )
        messages.success(request, "Marks saved successfully!")
        return redirect('teacher_dashboard')

    return render(request, "enter_marks.html", {"students": students, "subjects": subjects})


def study_material_list(request):
    student = request.user.student_profile  # logged-in student

    # Filter by class and division of the student
    materials = StudyMaterial.objects.filter(
        class_name=student.student_class,
        division=student.division
    )

    return render(request, 'study_materials.html', {'materials': materials})


def study_material_download(request, pk):
    material = get_object_or_404(StudyMaterial, pk=pk)
    return FileResponse(material.file.open(), as_attachment=True)



@login_required
def student_notifications(request):
    student = request.user

    notifications = Notification.objects.filter(
        recipient_type__in=['students', 'all']
    ).order_by('-created_at')

    last_login = student.last_login  

    return render(request, "student_notifications.html", {
        "notifications": notifications,
        "last_login": last_login
    })



@login_required
def student_timetable(request):
    student = get_object_or_404(Student, user=request.user)

    # Fetch all timetable entries
    entries = TimeTableEntry.objects.filter(
        class_name=student.student_class,
        division=student.division
    )

    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

    # Get all unique periods and sort them
    period_order = sorted(
        entries.values_list('period', flat=True).distinct(),
        key=lambda x: int(''.join(filter(str.isdigit, str(x)))) if any(c.isdigit() for c in str(x)) else 999
    )

    # Build a list of rows for the template
    timetable_grid = []
    for day in days_order:
        row = {'day': day, 'periods': []}
        for period in period_order:
            entry = entries.filter(day=day, period=period).first()
            row['periods'].append(entry)
        timetable_grid.append(row)

    return render(request, "student_timetable.html", {
        "student": student,
        "period_order": period_order,
        "timetable_grid": timetable_grid,
    })



@login_required
def student_marks_view(request):
    student = request.user.student_profile  # logged-in student

    # Fetch subjects only for the student's class
    subjects = Subject.objects.filter(class_name=student.student_class)

    marks_list = []
    for subject in subjects:
        try:
            mark_obj = Marks.objects.get(student=student, subject=subject)
            mark_value = mark_obj.marks
            status = "Pass" if mark_value >= 35 else "Fail"
        except Marks.DoesNotExist:
            mark_value = None
            status = "No mark assigned"

        marks_list.append({
            "subject": subject.name,
            "marks": mark_value,
            "status": status
        })

    return render(request, "student_marks.html", {"marks_list": marks_list})


@login_required
def student_attendance_view(request):
    student = request.user.student_profile  # logged-in student
    view_type = request.GET.get('view', 'daily')  # default to daily
    today = date.today()
    
    if view_type == 'daily':
        attendances = Attendance.objects.filter(student=student, date=today)
    elif view_type == 'weekly':
        start_week = today - timedelta(days=today.weekday())  # Monday
        end_week = start_week + timedelta(days=6)  # Sunday
        attendances = Attendance.objects.filter(student=student, date__range=[start_week, end_week])
    elif view_type == 'monthly':
        start_month = today.replace(day=1)
        end_month = today.replace(day=28) + timedelta(days=4)  # get next month safely
        end_month = end_month - timedelta(days=end_month.day)  # last day of current month
        attendances = Attendance.objects.filter(student=student, date__range=[start_month, end_month])
    else:
        attendances = Attendance.objects.filter(student=student)

    return render(request, "student_attendance.html", {
        "attendances": attendances,
        "view_type": view_type
    })