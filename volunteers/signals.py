from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum
from .models import Attendance, Badge, UserBadge

@receiver(post_save, sender=Attendance)
def update_volunteer_milestones(sender, instance, **kwargs):
    # Only execute calculations and gamified milestones if the attendance record is approved
    if instance.is_approved:
        volunteer = instance.volunteer
        
        # Calculate sum of all approved hours for this volunteer
        total_approved_hours = Attendance.objects.filter(
            volunteer=volunteer,
            is_approved=True
        ).aggregate(total=Sum('hours_worked'))['total'] or 0.00
        
        # Update volunteer's total hours. 
        # Using save(update_fields=...) prevents recursive triggers on general user changes.
        volunteer.total_hours = total_approved_hours
        volunteer.save(update_fields=['total_hours'])
        
        # Determine eligible badges based on total approved hours
        eligible_badges = Badge.objects.filter(hours_required__lte=total_approved_hours)
        
        for badge in eligible_badges:
            # Award the badge using get_or_create to guarantee idempotency and prevent duplicates
            UserBadge.objects.get_or_create(user=volunteer, badge=badge)
