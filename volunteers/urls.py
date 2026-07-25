from django.urls import path
from . import views

urlpatterns = [
    path('', views.LandingPageView.as_view(), name='landing'),
    path('opportunities/', views.OpportunityListView.as_view(), name='opportunity_list'),
    path('dashboard/', views.VolunteerDashboardView.as_view(), name='volunteer_dashboard'),
    path('opportunity/<int:opportunity_id>/checkin/', views.AttendanceCheckInView.as_view(), name='check_in'),
    path('attendance/<int:attendance_id>/checkout/', views.AttendanceCheckOutView.as_view(), name='check_out'),
    path('attendance/<int:attendance_id>/approve/', views.AttendanceApprovalView.as_view(), name='approve_attendance'),
    path('profile/card/', views.VolunteerCardView.as_view(), name='volunteer_card'),
    path('attendance/<int:attendance_id>/journal/', views.SubmitJournalView.as_view(), name='submit_journal'),
    path('certificates/download/', views.DownloadCertificateView.as_view(), name='download_certificate'),
]
