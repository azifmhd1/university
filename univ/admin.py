from django.contrib import admin
from .models import Subject, Student, Mark, Feedback, Assessment, Exam,ExamFee,Notice

admin.site.register(Subject)
admin.site.register(Student)
admin.site.register(Mark)
admin.site.register(Feedback)
admin.site.register(Assessment)
admin.site.register(Exam)
admin.site.register(ExamFee)
admin.site.register(Notice)

