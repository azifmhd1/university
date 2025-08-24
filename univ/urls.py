from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('admin/', admin.site.urls),  # ✅ add this line
    path('', views.home, name='home'),
    path('whatsnew/', views.whatsnew, name='whatsnew'),
    path('announcements/', views.announcements, name='announcements'),
    path('notifications/', views.notifications, name='notifications'),
    path('examfees/', views.examfees, name='examfees'),
    path('timetable/', views.timetable, name='timetable'),
    path('pressrelease/', views.pressrelease, name='pressrelease'),
    path('readmore/', views.readmore, name='readmore'),
    path('student/login/', views.student_login, name='student_login'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('logout/', views.logout_view, name='logout'),
    path('feedback/', views.feedback, name='feedback'),
    path('testimonials/', views.testimonials, name='testimonials'),
    path('mycourses/', views.my_courses, name='my_courses'),
    path('upcoming-events/', views.upcoming_events, name='upcoming_events'),
    path("dashboard/", views.dashboard, name="dashboard"),
    path('student/register/', views.register, name='register'),
    path("examfees/", views.examfees, name="exam_fees"),
    path('download-timetable/', views.download_timetable, name='download_timetable'),
    path('download-admit-card/', views.download_admit_card, name='download_admit_card'),
    path("pay-exam-fee/", views.pay_exam_fee, name="pay_exam_fee"),
    path("payment-success/", views.payment_success, name="payment_success"),
    path("test-alert/", views.test_alert, name="test_alert"),
    path("send-whatsapp/", views.send_whatsapp, name="send_whatsapp"),]

if settings.DEBUG:  
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)