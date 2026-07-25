from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Q
from django.utils import timezone
from django.http import HttpResponse, HttpResponseForbidden, request
from .models import Opportunity, Attendance, Skill, User
from django.shortcuts import redirect
# Look for your models import at the top of volunteers/views.py and update it:
from .models import Opportunity, Attendance, ImpactJournal
def home_view(request):
    # If Clerk hasn't dropped an authorized session token cookie yet, bounce them straight to login
    if not request.COOKIES.get('__session'):
        clerk_login_url = "https://complete-pelican-54.clerk.accounts.dev/sign-in?redirect_url=http://127.0.0.1:8000/"
        return redirect(clerk_login_url)
        
    # Otherwise, render the home page normal layout sequence
    return render(request, 'volunteers/home.html')
def is_ngo_staff(user):
    return user.is_authenticated and user.is_ngo_staff()

def is_volunteer(user):
    return user.is_authenticated and user.is_volunteer()

class LandingPageView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('volunteer_dashboard')
        return render(request, 'volunteers/landing.html')

class OpportunityListView(LoginRequiredMixin, ListView):
    model = Opportunity
    template_name = 'volunteers/opportunity_list.html'
    context_object_name = 'opportunities'

    def get_queryset(self):
        # Optimization: select_related for creator (foreign key) and prefetch_related for skills (many-to-many)
        # prevents N+1 query problem during render
        return Opportunity.objects.select_related('creator').prefetch_related('required_skills').filter(
            end_time__gt=timezone.now()
        ).order_by('start_time')

class VolunteerDashboardView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'volunteers/volunteer_dashboard.html'
    context_object_name = 'recommended_opportunities'

    def test_func(self):
        return self.request.user.is_volunteer()

    def get_queryset(self):
        volunteer = self.request.user
        user_skills = volunteer.skills.all()

        # Database-level aggregation & matching:
        # 1. Filters upcoming opportunities
        # 2. Annotates each with matching_skills_count (intersection of volunteer's skills and opportunity's required skills)
        # 3. Orders by highest match count first, then by start_time
        return Opportunity.objects.filter(
            end_time__gt=timezone.now()
        ).select_related('creator').prefetch_related('required_skills').annotate(
            matching_skills_count=Count(
                'required_skills',
                filter=Q(required_skills__in=user_skills)
            )
        ).order_by('-matching_skills_count', 'start_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Gamification metrics
        total_hours = user.total_hours
        level = int(total_hours // 10) + 1
        hours_in_current_level = total_hours % 10
        level_progress = float((hours_in_current_level / 10) * 100)
        hours_to_next_level = 10 - hours_in_current_level

        # Database-level check for unlocked badges using Exists subquery
        from django.db.models import Exists, OuterRef
        from .models import UserBadge, Badge
        
        unlocked_subquery = UserBadge.objects.filter(user=user, badge=OuterRef('pk'))
        badges = Badge.objects.annotate(
            is_unlocked=Exists(unlocked_subquery)
        ).order_by('hours_required')
        # Fetch opportunity IDs the user has already journaled
        from .models import ImpactJournal
        journaled_opportunity_ids = set(
            ImpactJournal.objects.filter(volunteer=user).values_list('opportunity_id', flat=True)
        )

        # Dynamic active streak calculation: distinct weeks with approved shifts
        from django.db.models.functions import ExtractWeek, ExtractYear
        distinct_weeks = Attendance.objects.filter(
            volunteer=user,
            is_approved=True,
            check_in__isnull=False
        ).annotate(
            week=ExtractWeek('check_in'),
            year=ExtractYear('check_in')
        ).values('year', 'week').distinct()
        streak_count = distinct_weeks.count()

        context.update({
            'my_attendances': Attendance.objects.filter(volunteer=user).select_related('opportunity').order_by('-check_in'),
            'badges': badges,
            'level': level,
            'level_progress': level_progress,
            'hours_to_next_level': hours_to_next_level,
            'journaled_opportunity_ids': journaled_opportunity_ids,
            'streak_count': streak_count,
        })
        return context

class AttendanceCheckInView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_volunteer()

    def post(self, request, opportunity_id):
        opportunity = get_object_or_404(Opportunity, id=opportunity_id)
        
        # Check if already checked in
        existing_attendance = Attendance.objects.filter(
            volunteer=request.user,
            opportunity=opportunity,
            check_out__isnull=True
        ).first()

        if existing_attendance:
            return HttpResponse("Already checked in.", status=400)

        # Record check-in
        Attendance.objects.create(
            volunteer=request.user,
            opportunity=opportunity,
            check_in=timezone.now()
        )
        # Render a small HTMX response component
        return HttpResponse('<span class="text-green-600 font-semibold">Checked In successfully!</span>')

class AttendanceCheckOutView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_volunteer()

    def post(self, request, attendance_id):
        attendance = get_object_or_404(Attendance, id=attendance_id, volunteer=request.user)
        
        if attendance.check_out:
            return HttpResponse("Already checked out.", status=400)

        attendance.check_out = timezone.now()
        attendance.save()

        return HttpResponse('<span class="text-orange-600 font-semibold">Checked Out (Pending Approval)</span>')

class AttendanceApprovalView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_ngo_staff()

    def post(self, request, attendance_id):
        # NGO Staff approves the record
        attendance = get_object_or_404(Attendance, id=attendance_id)
        
        if attendance.is_approved:
            return HttpResponse("Already approved.", status=400)

        attendance.is_approved = True
        attendance.approved_by = request.user
        
        # Calculate hours worked
        if attendance.check_in and attendance.check_out:
            duration = attendance.check_out - attendance.check_in
            attendance.hours_worked = round(duration.total_seconds() / 3600.0, 2)
    
        attendance.save()
        # Note: Saving this will trigger the Django post_save signal (implemented in Phase 3) to update user cumulative hours and reward badges.
        return HttpResponse(f'<span class="text-green-600 font-semibold">Approved ({attendance.hours_worked} hrs)</span>')

class VolunteerCardView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = User
    template_name = 'volunteers/volunteer_card.html'
    context_object_name = 'volunteer'

    def test_func(self):
        return self.request.user.is_volunteer()

    def get_object(self, queryset=None):
        return self.request.user

class SubmitJournalView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_volunteer()

    def get(self, request, attendance_id):
        attendance = get_object_or_404(Attendance, id=attendance_id, volunteer=request.user, is_approved=True)
        existing_journal = ImpactJournal.objects.filter(volunteer=request.user, opportunity=attendance.opportunity).first()
        if existing_journal:
            return redirect('volunteer_dashboard')
        return render(request, 'volunteers/submit_journal.html', {'attendance': attendance})

    def post(self, request, attendance_id):
        attendance = get_object_or_404(Attendance, id=attendance_id, volunteer=request.user, is_approved=True)
        existing_journal = ImpactJournal.objects.filter(volunteer=request.user, opportunity=attendance.opportunity).first()
        if existing_journal:
            return redirect('volunteer_dashboard')

        rating = request.POST.get('rating')
        reflection = request.POST.get('reflection')
        photo = request.FILES.get('photo')

        if not rating or not reflection:
            return render(request, 'volunteers/submit_journal.html', {
                'attendance': attendance,
                'error': 'Rating and reflection are required.'
            })

        journal = ImpactJournal.objects.create(
            volunteer=request.user,
            opportunity=attendance.opportunity,
            rating=int(rating),
            reflection=reflection,
            photo=photo
        )
        return redirect('volunteer_dashboard')
class DownloadCertificateView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_volunteer()
    def get(self, request):
        from io import BytesIO
        from reportlab.lib.pagesizes import letter, landscape
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        user = request.user
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(letter),
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CertTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=32,
            leading=38,
            textColor=colors.HexColor('#3730a3'),
            alignment=1
        )
        subtitle_style = ParagraphStyle(
            'CertSubTitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=18,
            leading=22,
            textColor=colors.HexColor('#4b5563'),
            alignment=1
        )
        body_style = ParagraphStyle(
            'CertBody',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=16,
            leading=24,
            textColor=colors.HexColor('#1f2937'),
            alignment=1
        )
        sig_label_style = ParagraphStyle(
            'CertSigLabel',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=12,
            leading=14,
            textColor=colors.HexColor('#4b5563'),
            alignment=1
        )
        story = []
        story.append(Spacer(1, 20))
        story.append(Paragraph("H O P E S Y N C", ParagraphStyle('Sub', parent=subtitle_style, fontSize=12, leading=14, textColor=colors.HexColor('#059669'))))
        story.append(Spacer(1, 15))
        story.append(Paragraph("CERTIFICATE OF SERVICE", title_style))
        story.append(Spacer(1, 10))
        story.append(Paragraph("PROUDLY PRESENTED TO", subtitle_style))
        story.append(Spacer(1, 20))
        full_name = f"{user.first_name} {user.last_name}".strip() or user.username
        story.append(Paragraph(f"<b>{full_name.upper()}</b>", ParagraphStyle('Recip', parent=title_style, fontSize=24, textColor=colors.HexColor('#0f172a'))))
        story.append(Spacer(1, 20))
        hours_str = f"{user.total_hours:.2f}"
        statement = (
            f"This certifies that <b>{full_name}</b> has successfully contributed "
            f"<b>{hours_str}</b> hours of verified community service to community projects "
            f"associated with the HopeSync volunteer network."
        )
        story.append(Paragraph(statement, body_style))
        story.append(Spacer(1, 40))
        story.append(Paragraph("___________________________", subtitle_style))
        story.append(Spacer(1, 5))
        story.append(Paragraph("Authorized NGO Coordinator", sig_label_style))
        story.append(Paragraph("HopeSync Verification Registry", ParagraphStyle('SubLabel', parent=sig_label_style, fontSize=10, fontName='Helvetica')))
        doc.build(story)
        pdf_data = buffer.getvalue()
        buffer.close()
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="HopeSync_Certificate_{user.username}.pdf"'
        response.write(pdf_data)
        return response