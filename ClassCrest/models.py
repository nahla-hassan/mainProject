from django.db import models
from django.contrib.auth.models import User



class ClassDivision(models.Model):
    CLASS_CHOICES = [(i, str(i)) for i in range(1, 11)]  # (stored_value, display_value)
    DIVISION_CHOICES = [(c, c) for c in ['A', 'B', 'C', 'D']]

    class_name = models.IntegerField(choices=CLASS_CHOICES)
    division = models.CharField(max_length=1, choices=DIVISION_CHOICES)

    def __str__(self):
        return f"{self.class_name}{self.division}"

    

class Subject(models.Model):
    CLASS_CHOICES = [(str(i), f"Class {i}") for i in range(1, 11)]

    name = models.CharField(max_length=100)
    class_name = models.CharField(max_length=2, choices=CLASS_CHOICES)

    def __str__(self):
        return f"{self.name} ({self.class_name})"



class UserRole(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_role')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    phone = models.CharField(max_length=15)
    qualification = models.CharField(max_length=100)
    address = models.TextField()
    class_to_handle = models.CharField(max_length=50, blank=True, null=True)
    join_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    assigned_divisions = models.ManyToManyField(ClassDivision, blank=True)
    subjects = models.ManyToManyField(Subject, blank=True)


    def __str__(self):
        return f"{self.user.get_full_name()} - Teacher"


class Student(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    DIVISION_CHOICES=(
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    roll_number = models.CharField(max_length=20)
    student_class = models.CharField(max_length=20)
    division=models.CharField(max_length=1, choices=DIVISION_CHOICES, default='A')
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    parent_contact = models.CharField(max_length=15)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.roll_number}"
    

class Notification(models.Model):
    MESSAGE_CHOICES = [
        ('all', 'All Users'),
        ('teachers', 'Teachers Only'),
        ('students', 'Students Only'),
    ]
    message = models.TextField()
    recipient_type = models.CharField(max_length=20, choices=MESSAGE_CHOICES)
    attachment = models.FileField(upload_to='notifications/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.recipient_type}: {self.message[:30]}..."


class TimeTableEntry(models.Model):
    class_name = models.CharField(max_length=50)
    division = models.CharField(max_length=10)
    day = models.CharField(max_length=15)
    period = models.CharField(max_length=10)
    subject = models.CharField(max_length=50)
    teacher = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.class_name}-{self.division} | {self.day} | {self.period} | {self.subject} | {self.teacher}"
    


class StudyMaterial(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    # Assign to class and division
    class_name = models.CharField(max_length=50)
    division = models.CharField(max_length=10)
    file = models.FileField(upload_to='study_materials/')
    uploaded_by = models.ForeignKey('Teacher', on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.class_name}{self.division}"
    

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10) 

class Marks(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    marks = models.FloatField()
