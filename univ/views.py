from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
from twilio.rest import Client


from datetime import datetime
import io
import razorpay
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import inch

from .models import Student, Assessment, Notice, Exam, ExamFee, Feedback
from .forms import FeedbackForm
from .utils import send_whatsapp_message


# ---------------------- Public Pages ----------------------
def home(request):
    return render(request, "home.html")

def whatsnew(request):
    return render(request, "whatsnew.html")

def announcements(request):
    return render(request, "announcements.html")

def notifications(request):
    return render(request, "notifications.html")

def timetable(request):
    return render(request, "timetable.html")

def pressrelease(request):
    return render(request, "pressrelease.html")

def readmore(request):
    return render(request, "readmore.html")

def contact(request):
    return render(request, "contact.html")


# ---------------------- Authentication ----------------------
def student_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # WhatsApp alert
            try:
                student = Student.objects.get(user=user)
                if student.phone:
                    send_whatsapp_message(
                        student.phone,
                        f"Hi {user.username}, you logged in successfully! 🎉"
                    )
            except Student.DoesNotExist:
                pass

            return redirect("dashboard")
        else:
            return render(request, "student_login.html", {"error": "Invalid username or password"})
    return render(request, "student_login.html")


@login_required(login_url="student_login")
def logout_view(request):
    logout(request)
    return redirect("student_login")


# ---------------------- Student Pages ----------------------
def about(request):
    return render(request, "about.html")

@login_required(login_url="student_login")
def my_courses(request):
    return render(request, "mycourses.html")

@login_required(login_url="student_login")
def upcoming_events(request):
    return render(request, "upcomingevents.html")


# ---------------------- Feedback ----------------------
def feedback(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you for your feedback!")
            return redirect("feedback")
    else:
        form = FeedbackForm()

    feedback_list = Feedback.objects.order_by("-created_at")
    return render(request, "feedback.html", {"form": form, "feedback_list": feedback_list})

def testimonials(request):
    return render(request, "testimonials.html")


# ---------------------- Registration ----------------------
def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        course = request.POST.get("course")
        phone = request.POST.get("phone")
        address = request.POST.get("address")

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("register")
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect("register")
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("register")

        user = User.objects.create_user(username=username, email=email, password=password1)
        Student.objects.create(user=user, course=course, phone=phone, address=address)

        messages.success(request, "Registration successful! Please login.")
        return redirect("student_login")

    return render(request, "register.html")


# ---------------------- Exam Fees (Display Only) ----------------------
def examfees(request):
    fees = [
        {"course": "BCom Semester 3", "fee": 1200, "late": 200, "last_date": "2025-09-15"},
        {"course": "BBA Semester 5", "fee": 1500, "late": 250, "last_date": "2025-09-18"},
        {"course": "BSc Computer Science Semester 1", "fee": 1100, "late": 150, "last_date": "2025-09-20"},
    ]
    return render(request, "examfees.html", {"fees": fees})


# ---------------------- Challan PDF ----------------------
def download_challan(request):
    course = request.GET.get("course", "B.Com")
    amount = request.GET.get("amount", "600")
    last_date = request.GET.get("last_date", "10-Aug-2025")

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="challan_{course}.pdf"'

    p = canvas.Canvas(response)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(60, 800, "Skillera University - Exam Fee Challan")
    p.setFont("Helvetica", 12)
    p.drawString(60, 760, f"Course: {course}")
    p.drawString(60, 740, f"Amount (₹): {amount}")
    p.drawString(60, 720, f"Last Date: {last_date}")
    p.drawString(60, 700, "Please pay at your nearest bank branch.")
    p.showPage()
    p.save()
    return response


def download_timetable(request):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=timetable.pdf"

    p = canvas.Canvas(response)

    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    p.drawString(100, 780, "Exam Timetable")
    p.drawString(100, 760, f"Generated on: {now}")
    p.drawString(100, 730, "Date: 20-08-2025 | Subject: Mathematics")
    p.drawString(100, 710, "Date: 22-08-2025 | Subject: Physics")

    p.showPage()
    p.save()
    return response


# ---------------------- Dashboard ----------------------
# Dashboard
@login_required(login_url="student_login")
def dashboard(request):
    student = Student.objects.get(user=request.user)

    exam_fee, created = ExamFee.objects.get_or_create(student=student)

    # Now Notice expects Student, not User
    notices = Notice.objects.filter(student=student).order_by("-created_at")[:5]

    context = {
        "student": student,
        "next_exam": Exam.objects.filter(student=student).order_by("date").first(),
        "assessments": Assessment.objects.filter(student=student),
        "notices": notices,
        "notices_count": notices.count(),
        "exam_fee": exam_fee,
        "razorpay_key": settings.RAZORPAY_KEY_ID,
    }
    return render(request, "dashboard.html", context)

# ---------------------- Exam Fee Payment ----------------------
@login_required
def pay_exam_fee(request):
    student = Student.objects.get(user=request.user)
    exam_fee = ExamFee.objects.get(student=student)

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    payment = client.order.create({
        "amount": int(exam_fee.amount * 100),
        "currency": "INR",
        "payment_capture": 1,
    })

    exam_fee.order_id = payment["id"]
    exam_fee.save()

    context = {
        "exam_fee": exam_fee,
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "order_id": payment["id"],
        "amount": exam_fee.amount,
    }
    return render(request, "pay_exam_fee.html", context)


@login_required
def payment_success(request):
    student = Student.objects.get(user=request.user)
    exam_fee = ExamFee.objects.get(student=student)

    exam_fee.paid = True
    exam_fee.payment_date = timezone.now()
    exam_fee.save()

    return redirect("dashboard")


# ---------------------- Admit Card PDF ----------------------
@login_required(login_url="student_login")
def download_admit_card(request):
    student = Student.objects.get(user=request.user)

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    width, height = A4

    # Title Banner
    p.setFont("Helvetica-Bold", 20)
    p.setFillColorRGB(0.2, 0.4, 0.8)
    p.rect(0, height - 80, width, 60, fill=1)
    p.setFillColorRGB(1, 1, 1)
    p.drawCentredString(width / 2, height - 55, "UNIVERSITY ADMIT CARD")

    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    p.setFont("Helvetica", 9)
    p.setFillColorRGB(0, 0, 0)
    p.drawRightString(width - 40, height - 90, f"Generated on: {now}")

    # Outer border
    p.setLineWidth(2)
    p.rect(30, 100, width - 60, height - 160)

    # Student Photo
    if student.photo and student.photo.path:
        try:
            p.drawImage(student.photo.path, width - 170, height - 300,
                        width=120, height=140, preserveAspectRatio=True, mask="auto")
        except:
            p.rect(width - 170, height - 300, 120, 140)
            p.drawString(width - 160, height - 230, "Photo N/A")
    else:
        p.rect(width - 170, height - 300, 120, 140)
        p.drawString(width - 160, height - 230, "Photo N/A")

    # Student Details
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, height - 140, "Student Details")

    p.setFont("Helvetica", 12)
    y = height - 160
    line_gap = 22
    details = [
        ("Name", student.user.get_full_name() or student.user.username),
        ("Register No", student.register_no or "N/A"),
        ("Course", student.course or "N/A"),
        ("Duration", student.duration or "N/A"),
        ("Phone", student.phone or "N/A"),
        ("Address", student.address or "N/A"),
    ]
    for label, value in details:
        p.drawString(60, y, f"{label}:")
        p.drawString(180, y, str(value))
        y -= line_gap

    # Exam Details
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y - 10, "Exam Details")

    p.setFont("Helvetica", 12)
    exam_details = [
        ("Exam Date", "15th September 2025"),
        ("Exam Center", "University Main Hall"),
    ]
    y -= 30
    for label, value in exam_details:
        p.drawString(60, y, f"{label}:")
        p.drawString(180, y, str(value))
        y -= line_gap

    # Signature
    p.rect(width - 250, 120, 180, 60)
    p.setFont("Helvetica", 12)
    p.drawCentredString(width - 160, 140, "Controller of Exams")
    p.setFont("Helvetica", 9)
    p.drawCentredString(width - 160, 125, "(Authorized Signatory)")

    # Finalize
    p.showPage()
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="admit_card.pdf")

from django.shortcuts import HttpResponse
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from .utils import send_whatsapp_message
from .models import Student

def test_alert(request):
    user = request.user
    if not user.is_authenticated:
        return HttpResponse("❌ Please login first to test alert.")

    ts = timezone.localtime().strftime("%Y-%m-%d %H:%M:%S")
    subject = "Test Alert - University Portal"
    message = f"Hi {user.username}, this is a test alert at {ts}."
    recipient = [user.email]

    # Send Email
    try:
        send_mail(subject, message, settings.EMAIL_HOST_USER, recipient)
    except Exception as e:
        return HttpResponse(f"❌ Email failed: {e}")

    # Send WhatsApp if phone exists
    student = Student.objects.filter(user=user).first()
    if student and student.phone:
        try:
            send_whatsapp_message(f"+91{student.phone}", message)
        except Exception as e:
            return HttpResponse(f"✅ Email sent, ❌ WhatsApp failed: {e}")

    return HttpResponse("✅ Test alert sent via Email + WhatsApp")

def send_whatsapp(request):

    account_sid = "AC09a7ddcd8af97171b7a77e6c9a98b20"     # Twilio dashboard → Project Info
    auth_token = "7343c29991f58139f29cf9a4c6e19a03"       # Twilio dashboard → Auth Token
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        from_="whatsapp:+14155238886",   # Twilio sandbox number
        body="Hello from Django 🚀",
        to="whatsapp:+91XXXXXXXXXX"      # ninte WhatsApp number country code oode
    )

    return HttpResponse(f"Message sent: {message.sid}")
