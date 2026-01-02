from django.urls import path
from . import views

# app_name = "ClassCrest"

urlpatterns = [
    # Home and Authentication
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    
    # Registration
    path('register/student/', views.student_register, name='student_register'),

    path('register/teacher/', views.teacher_register, name='teacher_register'),

    # ADMIN
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/students/', views.manage_students, name='manage_students'),
    path('students/', views.student_view, name='student_view'),
    path('students/edit/<int:student_id>/', views.edit_student, name='edit_student'),
    path('students/delete/<int:student_id>/', views.delete_student, name='delete_student'),
    path('upload/timetable/', views.upload_common_timetable, name='upload_common_timetable'),
    path('admin/exam-marks-report/', views.admin_exam_report, name='admin_exam_report'),
    

    path('admin/teachers/', views.manage_teachers, name='manage_teachers'),
    path('teachers/', views.teacher_view, name='teacher_view'),
    path('teachers/edit/<int:teacher_id>/', views.edit_teacher, name='edit_teacher'),
    path('teachers/delete/<int:teacher_id>/', views.delete_teacher, name='delete_teacher'),
    path('teachers/list/', views.teacher_list, name='teacher_list'),

    path('teacher/<int:teacher_id>/assign-divisions/', views.assign_divisions, name='assign_divisions'),
    
    path('admin/notifications/create/', views.create_notification, name='create_notification'),
    
    path('subjects/', views.subject_list, name='subject-list'),
    path('subjects/add/', views.subject_create, name='subject-add'),
    path('subjects/<int:pk>/edit/', views.subject_update, name='subject-edit'),
    path('subjects/<int:pk>/delete/', views.subject_delete, name='subject-delete'),
    path('admin/attendance-report/', views.admin_attendance_report, name='admin_attendance_report'),

    # TEACHER
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/timetable/', views.view_teacher_timetable, name='teacher_timetable'),
    path('teacher/dashboard/teacher_notifications/', views.teacher_notifications, name='teacher_notifications'),
    path('teacher/upload-study-material/', views.upload_study_material, name='upload_study_material'),
    path('teacher/mark-attendance/', views.mark_attendance, name='mark_attendance'),
    path('teacher/enter-marks/', views.enter_marks, name='enter_marks'),

    # STUDENT
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('materials/', views.study_material_list, name='study_material_list'),
    path('materials/download/<int:pk>/', views.study_material_download, name='study_material_download'),
    path('notifications/', views.student_notifications, name='student_notifications'),
    path("student/timetable/", views.student_timetable, name="student_timetable"),
    path('student/marks/',views.student_marks_view, name='student-marks'),
    path('student/attendance/',views.student_attendance_view, name='student-attendance'),

]