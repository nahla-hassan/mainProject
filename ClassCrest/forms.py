from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Teacher, Student,ClassDivision,Subject,StudyMaterial


class TeacherRegistrationForm(UserCreationForm):
    QUALIFICATION_CHOICES = [
        ("B.Ed", "B.Ed"),
        ("M.Ed", "M.Ed"),
        ("M.Sc", "M.Sc"),
        ("B.Sc", "B.Sc"),
        ("PhD", "PhD"),
        ("M.A", "M.A"),
        ("B.A", "B.A"),
        ("M.Com", "M.Com"),
        ("B.Com", "B.Com"),
    ]

    first_name = forms.CharField(
        max_length=30, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=30, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    phone = forms.CharField(
        max_length=15, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'})
    )
    qualification = forms.ChoiceField(
        choices=QUALIFICATION_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Address', 'rows': 3}),
        required=True
    )
    class_to_handle = forms.CharField(
        max_length=50, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Class to Handle'})
    )
    join_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=False
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})


class TeacherForm(forms.ModelForm):
    QUALIFICATION_CHOICES = [
        ("B.Ed", "B.Ed"),
        ("M.Ed", "M.Ed"),
        ("M.Sc", "M.Sc"),
        ("B.Sc", "B.Sc"),
        ("PhD", "PhD"),
        ("M.A", "M.A"),
        ("B.A", "B.A"),
        ("M.Com", "M.Com"),
        ("B.Com", "B.Com"),
    ]

    qualification = forms.ChoiceField(
        choices=QUALIFICATION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Teacher
        fields = [
            'phone',
            'qualification',
            'address',
            'class_to_handle',
            'join_date'
        ]

        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number'
            }),

            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Address',
                'rows': 3,
            }),

            'class_to_handle': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Class to Handle'
            }),
            'join_date': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'readonly': 'readonly'
            }),
        }


class AssignDivisionForm(forms.ModelForm):
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.none(),
        required=True,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})  # Change this
    )

    class Meta:
        model = Teacher
        fields = ['subjects', 'assigned_divisions']
        widgets = {
            'subjects': forms.CheckboxSelectMultiple(),
            'assigned_divisions': forms.CheckboxSelectMultiple
        }

    def __init__(self, *args, **kwargs):
        teacher = kwargs.get('instance')
        super().__init__(*args, **kwargs)

        if teacher and teacher.class_to_handle:
            self.fields['assigned_divisions'].queryset = ClassDivision.objects.filter(
                class_name=teacher.class_to_handle
            )
        else:
            self.fields['assigned_divisions'].queryset = ClassDivision.objects.none()

        if teacher and teacher.class_to_handle:
            self.fields['subjects'].queryset = Subject.objects.filter(
                class_name=teacher.class_to_handle
            )
        else:
            self.fields['subjects'].queryset = Subject.objects.none()

        if teacher and teacher.pk:
            self.fields['subjects'].initial = teacher.subjects.all()


class StudyMaterialForm(forms.ModelForm):
    class Meta:
        model = StudyMaterial
        fields = ['title', 'description', 'class_name', 'division', 'file']

    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher', None)  # logged-in teacher
        super().__init__(*args, **kwargs)

        if teacher:
            # Get assigned divisions
            assigned_divs = teacher.assigned_divisions.all()  # QuerySet of ClassDivision

            # Extract classes and divisions
            class_choices = sorted(set([(d.class_name, d.class_name) for d in assigned_divs]))
            division_choices = sorted(set([(d.division, d.division) for d in assigned_divs]))

            self.fields['class_name'] = forms.ChoiceField(
                choices=class_choices,
                label="Class"
            )
            self.fields['division'] = forms.ChoiceField(
                choices=division_choices,
                label="Division"
            )


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['class_name', 'name']
        widgets = {
            'class_name': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject Name'}),
        }

class StudentRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    roll_number = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Roll Number'}))
    student_class = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Class'}))
    division = forms.ChoiceField(choices=Student.DIVISION_CHOICES,widget=forms.Select(attrs={'class': 'form-control'}))
    date_of_birth = forms.DateField(required=True, widget=forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Date of Birth', 'type': 'date'}))
    gender = forms.ChoiceField(choices=Student.GENDER_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    parent_contact = forms.CharField(max_length=15, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Parent Contact'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Address', 'rows': 3}), required=True)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})
    
    def clean_roll_number(self):
        roll_number = self.cleaned_data.get('roll_number')
        if Student.objects.filter(roll_number=roll_number).exists():
            raise forms.ValidationError("This roll number is already registered.")
        return roll_number
    
    
class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'student_class', 'division', 'roll_number', 
            'date_of_birth', 'gender', 'parent_contact', 'address'
        ]

        widgets = {
            'student_class': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Class'}),
            'division': forms.Select(attrs={'class': 'form-control'}),
            'roll_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Roll Number'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'parent_contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Parent Contact'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Address'}),
        }