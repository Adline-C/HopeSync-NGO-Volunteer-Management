from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class User(AbstractUser):
    class Role(models.TextChoices):
        VOLUNTEER = 'VOLUNTEER', 'Volunteer'
        NGO_STAFF = 'NGO_STAFF', 'NGO Staff'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.VOLUNTEER
    )
    skills = models.ManyToManyField(Skill, blank=True, related_name='volunteers')
    total_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Total approved volunteer hours")
    badges = models.ManyToManyField('Badge', through='UserBadge', related_name='users', blank=True)

    def is_ngo_staff(self):
        return self.role == self.Role.NGO_STAFF

    def is_volunteer(self):
        return self.role == self.Role.VOLUNTEER

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class Opportunity(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    creator = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='created_opportunities',
        limit_choices_to={'role': 'NGO_STAFF'}
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=255)
    required_skills = models.ManyToManyField(Skill, related_name='opportunities', blank=True)
    max_capacity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time.")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Opportunities"

class Attendance(models.Model):
    volunteer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='attendances',
        limit_choices_to={'role': 'VOLUNTEER'}
    )
    opportunity = models.ForeignKey(
        Opportunity, 
        on_delete=models.CASCADE, 
        related_name='attendances'
    )
    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='approved_attendances',
        limit_choices_to={'role': 'NGO_STAFF'}
    )
    hours_worked = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, help_text="Calculated hours after check-out and approval")

    def clean(self):
        super().clean()
        if self.check_in and self.check_out and self.check_in >= self.check_out:
            raise ValidationError("Check-out time must be after check-in time.")

    def __str__(self):
        return f"{self.volunteer.username} - {self.opportunity.title}"

class Badge(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    hours_required = models.PositiveIntegerField(help_text="Hours milestone needed to unlock this badge")
    icon = models.CharField(max_length=100, help_text="Tailwind/FontAwesome class name for display")

    def __str__(self):
        return self.name

class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='user_badges')
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'badge')

    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"

class ImpactJournal(models.Model):
    volunteer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='impact_journals')
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='impact_journals')
    rating = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    reflection = models.TextField()
    photo = models.ImageField(upload_to='impact_photos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Journal by {self.volunteer.username} for {self.opportunity.title}"

