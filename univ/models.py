from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Subject(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    course = models.CharField(max_length=100, blank=True, null=True)
    duration = models.CharField(max_length=50, blank=True, null=True)   # 👈 Course duration
    register_no = models.CharField(max_length=20, unique=True, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to="student_photos/", blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.register_no})"




class Mark(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    mark = models.IntegerField()

    def __str__(self):
        return f"{self.student.user.username} - {self.subject.name}: {self.mark}"
    
class Feedback(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    rating = models.IntegerField(default=0)  # ⭐ New star rating field
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} - {self.created_at.strftime('%Y-%m-%d')}"
    
# models.py
class Assessment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    subject = models.CharField(max_length=100)
    date = models.DateField()
    time = models.TimeField()
    venue = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.subject} - {self.student}"

class Exam(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    exam_name = models.CharField(max_length=200)
    date = models.DateField()
    center = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.exam_name} - {self.student}"

class Notice(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    created_at = models.DateTimeField(default=timezone.now)  # instead of auto_now_add

class ExamFee(models.Model):
    student = models.OneToOneField(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2, default=1000.00)  # exam fee default ₹1000
    paid = models.BooleanField(default=False)
    payment_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.username} - {'Paid' if self.paid else 'Pending'}"



