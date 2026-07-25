import os
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Configure Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ngo_project.settings')
django.setup()

from volunteers.models import User, Skill, Opportunity, Badge

def seed_database():
    print("🌱 Seeding database with dynamic test data...")

    # 1. Clear existing data to prevent unique constraint conflicts
    Opportunity.objects.all().delete()
    Skill.objects.all().delete()
    Badge.objects.all().delete()
    User.objects.filter(is_superuser=False).delete()

    # 2. Add Sample Skills
    skill_names = [
        'Graphic Design', 'Social Media Management', 'Data Entry & Analytics', 
        'Disaster Relief Support', 'First Aid & CPR', 'Event Coordination'
    ]
    skills = [Skill.objects.create(name=name, description=f"Expertise in {name.lower()}.") for name in skill_names]
    print(f"✔ Created {len(skills)} Skills.")

    # 3. Add Gamification Badges
    badges_data = [
        ('Bronze Helper', 'Log 10 approved volunteer hours', 10, 'fas fa-medal text-amber-600'),
        ('Silver Champion', 'Log 25 approved volunteer hours', 25, 'fas fa-award text-slate-400'),
        ('Gold Community Hero', 'Log 50 approved volunteer hours', 50, 'fas fa-trophy text-yellow-400'),
    ]
    for name, desc, hrs, icon in badges_data:
        Badge.objects.create(name=name, description=desc, hours_required=hrs, icon=icon)
    print("✔ Created Gamification Milestones.")

    # 4. Create an NGO Staff Coordinator
    staff_user = User.objects.create_user(
        username='manager_jane',
        email='jane@ngo.org',
        password='Password123!',
        role=User.Role.NGO_STAFF
    )
    print("✔ Created Staff User: manager_jane (Password: Password123!)")

    # 5. Create a Volunteer with Matching Skills
    volunteer_user = User.objects.create_user(
        username='sam_volunteer',
        email='sam@gmail.com',
        password='Password123!',
        role=User.Role.VOLUNTEER
    )
    # Assign specific skills to trigger our matching algorithm
    volunteer_user.skills.add(skills[0], skills[1]) # Graphic Design & Social Media
    print("✔ Created Volunteer User: sam_volunteer (Password: Password123!)")

    # 6. Generate Dynamic Opportunities
    # Match event: Requires Graphic Design
    Opportunity.objects.create(
        title='Design Charity Drive Flyers',
        description='Help us build social media banners and printable graphics for our upcoming fundraising campaign.',
        creator=staff_user,
        start_time=timezone.now() + timedelta(days=2),
        end_time=timezone.now() + timedelta(days=2, hours=4),
        location='Remote / Online',
        max_capacity=5
    ).required_skills.add(skills[0])

    # Non-match event: Requires Disaster Relief
    Opportunity.objects.create(
        title='Food Distribution Logistics',
        description='Sorting and packing emergency food supplies for local community pantries.',
        creator=staff_user,
        start_time=timezone.now() + timedelta(days=5),
        end_time=timezone.now() + timedelta(days=5, hours=6),
        location='Main NGO Warehouse',
        max_capacity=15
    ).required_skills.add(skills[3])

    print("✔ Generated Dynamic Opportunity Shifts.")
    print("🎉 Seeding complete! Go check your dashboard.")

if __name__ == '__main__':
    seed_database()