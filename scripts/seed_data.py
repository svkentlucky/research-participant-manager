"""
Seed script to populate the database with realistic dummy data.
Run with: python -m scripts.seed_data
"""
import asyncio
import random
from datetime import datetime, date, timedelta
from decimal import Decimal

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.config import get_settings
from app.models.respondent import Respondent
from app.models.study import Study
from app.models.screener_criteria import ScreenerCriteria
from app.models.study_assignment import StudyAssignment

settings = get_settings()

# Sample data pools
FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Lisa", "Daniel", "Nancy",
    "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
    "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle",
    "Kenneth", "Dorothy", "Kevin", "Carol", "Brian", "Amanda", "George", "Melissa",
    "Timothy", "Deborah", "Ronald", "Stephanie", "Edward", "Rebecca", "Jason", "Sharon",
    "Jeffrey", "Laura", "Ryan", "Cynthia", "Jacob", "Kathleen", "Gary", "Amy",
    "Nicholas", "Angela", "Eric", "Shirley", "Jonathan", "Anna", "Stephen", "Brenda",
    "Larry", "Pamela", "Justin", "Emma", "Scott", "Nicole", "Brandon", "Helen",
    "Benjamin", "Samantha", "Samuel", "Katherine", "Raymond", "Christine", "Gregory", "Debra",
    "Frank", "Rachel", "Alexander", "Carolyn", "Patrick", "Janet", "Jack", "Catherine",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
    "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White",
    "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young",
    "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker",
    "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris", "Morales", "Murphy",
]

CITIES_BY_STATE = {
    "NY": ["New York", "Brooklyn", "Queens", "Buffalo", "Rochester", "Yonkers", "Syracuse"],
    "CA": ["Los Angeles", "San Francisco", "San Diego", "San Jose", "Oakland", "Sacramento", "Fresno"],
    "TX": ["Houston", "San Antonio", "Dallas", "Austin", "Fort Worth", "El Paso", "Arlington"],
    "FL": ["Miami", "Orlando", "Tampa", "Jacksonville", "Fort Lauderdale", "St. Petersburg", "Hialeah"],
    "IL": ["Chicago", "Aurora", "Naperville", "Joliet", "Rockford", "Springfield", "Elgin"],
    "PA": ["Philadelphia", "Pittsburgh", "Allentown", "Reading", "Erie", "Scranton", "Bethlehem"],
    "OH": ["Columbus", "Cleveland", "Cincinnati", "Toledo", "Akron", "Dayton", "Parma"],
    "GA": ["Atlanta", "Augusta", "Columbus", "Savannah", "Athens", "Macon", "Roswell"],
    "NC": ["Charlotte", "Raleigh", "Greensboro", "Durham", "Winston-Salem", "Fayetteville", "Cary"],
    "MI": ["Detroit", "Grand Rapids", "Warren", "Sterling Heights", "Ann Arbor", "Lansing", "Flint"],
    "NJ": ["Newark", "Jersey City", "Paterson", "Elizabeth", "Edison", "Woodbridge", "Trenton"],
    "VA": ["Virginia Beach", "Norfolk", "Chesapeake", "Richmond", "Newport News", "Alexandria", "Hampton"],
    "WA": ["Seattle", "Spokane", "Tacoma", "Vancouver", "Bellevue", "Kent", "Everett"],
    "AZ": ["Phoenix", "Tucson", "Mesa", "Chandler", "Scottsdale", "Glendale", "Gilbert"],
    "MA": ["Boston", "Worcester", "Springfield", "Cambridge", "Lowell", "Brockton", "Quincy"],
    "CO": ["Denver", "Colorado Springs", "Aurora", "Fort Collins", "Lakewood", "Thornton", "Arvada"],
}

STATES = list(CITIES_BY_STATE.keys())

INCOME_BRACKETS = ["Under 25k", "25k-50k", "50k-75k", "75k-100k", "100k-150k", "150k+"]

GENDERS = ["male", "female", "non-binary", "prefer not to say"]

ETHNICITIES = [
    "White/Caucasian", "Black/African American", "Hispanic/Latino",
    "Asian", "Native American", "Pacific Islander", "Mixed/Multi-racial", "Other"
]

OCCUPATIONS = [
    "Software Engineer", "Teacher", "Nurse", "Marketing Manager", "Sales Representative",
    "Accountant", "Project Manager", "Designer", "Data Analyst", "Human Resources",
    "Customer Service", "Operations Manager", "Financial Analyst", "Consultant",
    "Healthcare Administrator", "Real Estate Agent", "Attorney", "Pharmacist",
    "Business Owner", "Retail Manager", "Engineer", "Writer", "Chef", "Electrician",
    "Administrative Assistant", "Social Worker", "Architect", "Researcher",
    "Product Manager", "UX Designer", "Content Creator", "Freelancer", "Student",
    "Retired", "Stay-at-home Parent", "Executive", "Entrepreneur"
]

# Study templates
STUDY_TEMPLATES = [
    {
        "title": "Coffee Consumption Habits Among Urban Professionals",
        "client_name": "Starbucks",
        "methodology": "focus_group",
        "target_count": 12,
        "incentive_amount": Decimal("150.00"),
        "criteria": [
            {"field_name": "age", "operator": "between", "value": [25, 45]},
            {"field_name": "household_income", "operator": "in", "value": ["75k-100k", "100k-150k", "150k+"]},
        ]
    },
    {
        "title": "Gen Z Shopping Preferences Study",
        "client_name": "Nike",
        "methodology": "idi",
        "target_count": 20,
        "incentive_amount": Decimal("125.00"),
        "criteria": [
            {"field_name": "age", "operator": "between", "value": [18, 27]},
        ]
    },
    {
        "title": "Home Cooking During Weeknights",
        "client_name": "HelloFresh",
        "methodology": "ethnography",
        "target_count": 8,
        "incentive_amount": Decimal("300.00"),
        "criteria": [
            {"field_name": "age", "operator": "between", "value": [28, 50]},
            {"field_name": "household_income", "operator": "in", "value": ["50k-75k", "75k-100k", "100k-150k"]},
        ]
    },
    {
        "title": "Electric Vehicle Purchase Consideration",
        "client_name": "Tesla",
        "methodology": "focus_group",
        "target_count": 15,
        "incentive_amount": Decimal("200.00"),
        "criteria": [
            {"field_name": "household_income", "operator": "in", "value": ["100k-150k", "150k+"]},
            {"field_name": "age", "operator": "gte", "value": 30},
        ]
    },
    {
        "title": "Mobile Banking App Usability",
        "client_name": "Chase",
        "methodology": "idi",
        "target_count": 25,
        "incentive_amount": Decimal("100.00"),
        "criteria": [
            {"field_name": "age", "operator": "between", "value": [21, 55]},
        ]
    },
    {
        "title": "Streaming Service Preferences",
        "client_name": "Netflix",
        "methodology": "survey",
        "target_count": 100,
        "incentive_amount": Decimal("25.00"),
        "criteria": [
            {"field_name": "age", "operator": "between", "value": [18, 65]},
        ]
    },
    {
        "title": "Luxury Skincare Routine Study",
        "client_name": "Estee Lauder",
        "methodology": "idi",
        "target_count": 18,
        "incentive_amount": Decimal("175.00"),
        "criteria": [
            {"field_name": "gender", "operator": "in", "value": ["female", "non-binary"]},
            {"field_name": "household_income", "operator": "in", "value": ["100k-150k", "150k+"]},
            {"field_name": "age", "operator": "between", "value": [25, 55]},
        ]
    },
    {
        "title": "Remote Work Technology Needs",
        "client_name": "Microsoft",
        "methodology": "focus_group",
        "target_count": 10,
        "incentive_amount": Decimal("175.00"),
        "criteria": [
            {"field_name": "age", "operator": "between", "value": [25, 50]},
            {"field_name": "household_income", "operator": "gte", "value": "50k-75k"},
        ]
    },
    {
        "title": "Pet Food Brand Perception",
        "client_name": "Purina",
        "methodology": "focus_group",
        "target_count": 12,
        "incentive_amount": Decimal("125.00"),
        "criteria": [
            {"field_name": "age", "operator": "between", "value": [25, 60]},
        ]
    },
    {
        "title": "Fitness App User Experience",
        "client_name": "Peloton",
        "methodology": "idi",
        "target_count": 15,
        "incentive_amount": Decimal("150.00"),
        "criteria": [
            {"field_name": "age", "operator": "between", "value": [22, 45]},
            {"field_name": "household_income", "operator": "in", "value": ["75k-100k", "100k-150k", "150k+"]},
        ]
    },
    {
        "title": "Parent Decision-Making for Children's Education",
        "client_name": "Kumon",
        "methodology": "focus_group",
        "target_count": 10,
        "incentive_amount": Decimal("200.00"),
        "criteria": [
            {"field_name": "age", "operator": "between", "value": [30, 50]},
        ]
    },
    {
        "title": "Craft Beer Tasting Preferences",
        "client_name": "Boston Beer Company",
        "methodology": "ethnography",
        "target_count": 6,
        "incentive_amount": Decimal("250.00"),
        "criteria": [
            {"field_name": "age", "operator": "between", "value": [21, 40]},
            {"field_name": "state", "operator": "in", "value": ["NY", "CA", "CO", "MA"]},
        ]
    },
]

ASSIGNMENT_STATUSES = ["invited", "confirmed", "completed", "no_show", "rejected"]


def generate_email(first_name: str, last_name: str, index: int) -> str:
    domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com"]
    patterns = [
        f"{first_name.lower()}.{last_name.lower()}{index}@{random.choice(domains)}",
        f"{first_name.lower()}{last_name.lower()[:3]}{index}@{random.choice(domains)}",
        f"{first_name[0].lower()}{last_name.lower()}{index}@{random.choice(domains)}",
    ]
    return random.choice(patterns)


def generate_phone() -> str:
    return f"{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"


def generate_zip(state: str) -> str:
    # Simplified zip code ranges by state
    zip_ranges = {
        "NY": (10000, 14999), "CA": (90000, 96199), "TX": (75000, 79999),
        "FL": (32000, 34999), "IL": (60000, 62999), "PA": (15000, 19699),
        "OH": (43000, 45999), "GA": (30000, 31999), "NC": (27000, 28999),
        "MI": (48000, 49999), "NJ": (7000, 8999), "VA": (22000, 24699),
        "WA": (98000, 99499), "AZ": (85000, 86599), "MA": (1000, 2799),
        "CO": (80000, 81699),
    }
    low, high = zip_ranges.get(state, (10000, 99999))
    return str(random.randint(low, high)).zfill(5)


async def seed_database():
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        print("🌱 Starting database seed...")

        # Check if data already exists
        from sqlalchemy import select, func
        result = await session.execute(select(func.count(Respondent.id)))
        existing_count = result.scalar()

        if existing_count > 5:
            print(f"⚠️  Database already has {existing_count} respondents. Skipping seed.")
            print("   To re-seed, truncate the tables first.")
            return

        # Create 150 respondents
        print("👥 Creating 150 respondents...")
        respondents = []
        for i in range(150):
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            state = random.choice(STATES)
            city = random.choice(CITIES_BY_STATE[state])

            # Weight age distribution (more 25-45)
            age_weights = [(18, 24, 0.15), (25, 34, 0.35), (35, 44, 0.25), (45, 54, 0.15), (55, 70, 0.10)]
            age_range = random.choices(age_weights, weights=[w[2] for w in age_weights])[0]
            age = random.randint(age_range[0], age_range[1])

            # Weight income by age
            if age < 25:
                income = random.choice(["Under 25k", "25k-50k", "50k-75k"])
            elif age < 35:
                income = random.choice(["25k-50k", "50k-75k", "75k-100k", "100k-150k"])
            else:
                income = random.choice(INCOME_BRACKETS)

            respondent = Respondent(
                first_name=first_name,
                last_name=last_name,
                email=generate_email(first_name, last_name, i),
                phone=generate_phone(),
                city=city,
                state=state,
                zip_code=generate_zip(state),
                age=age,
                gender=random.choice(GENDERS),
                ethnicity=random.choice(ETHNICITIES),
                household_income=income,
                occupation=random.choice(OCCUPATIONS),
                is_active=random.random() > 0.05,  # 95% active
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 365)),
            )
            respondent.updated_at = respondent.created_at
            session.add(respondent)
            respondents.append(respondent)

        await session.flush()
        print(f"   ✅ Created {len(respondents)} respondents")

        # Create studies
        print("📋 Creating 12 studies...")
        studies = []
        statuses = ["draft", "recruiting", "recruiting", "recruiting", "in_field", "in_field", "completed", "completed"]

        for i, template in enumerate(STUDY_TEMPLATES):
            status = random.choice(statuses)
            start_date = date.today() - timedelta(days=random.randint(0, 60))

            if status == "completed":
                end_date = start_date + timedelta(days=random.randint(14, 45))
            elif status in ["recruiting", "in_field"]:
                end_date = start_date + timedelta(days=random.randint(30, 90))
            else:
                end_date = None
                start_date = None

            study = Study(
                title=template["title"],
                client_name=template["client_name"],
                methodology=template["methodology"],
                target_count=template["target_count"],
                incentive_amount=template["incentive_amount"],
                status=status,
                start_date=start_date,
                end_date=end_date,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 90)),
            )
            session.add(study)
            studies.append((study, template["criteria"]))

        await session.flush()
        print(f"   ✅ Created {len(studies)} studies")

        # Add criteria to studies
        print("🎯 Adding screener criteria...")
        criteria_count = 0
        for study, criteria_list in studies:
            for criterion_data in criteria_list:
                criterion = ScreenerCriteria(
                    study_id=study.id,
                    field_name=criterion_data["field_name"],
                    operator=criterion_data["operator"],
                    value=criterion_data["value"],
                )
                session.add(criterion)
                criteria_count += 1

        await session.flush()
        print(f"   ✅ Created {criteria_count} screener criteria")

        # Create assignments for non-draft studies
        print("📝 Creating study assignments...")
        assignment_count = 0
        for study, _ in studies:
            if study.status == "draft":
                continue

            # Assign random respondents
            num_assignments = random.randint(
                min(5, len(respondents)),
                min(study.target_count + 5, len(respondents) // 2)
            )
            assigned_respondents = random.sample(respondents, num_assignments)

            for respondent in assigned_respondents:
                # Determine status based on study status
                if study.status == "completed":
                    status = random.choices(
                        ["completed", "no_show", "rejected"],
                        weights=[0.75, 0.15, 0.10]
                    )[0]
                elif study.status == "in_field":
                    status = random.choices(
                        ["confirmed", "completed", "no_show", "invited"],
                        weights=[0.4, 0.3, 0.1, 0.2]
                    )[0]
                else:  # recruiting
                    status = random.choices(
                        ["invited", "confirmed", "rejected"],
                        weights=[0.5, 0.35, 0.15]
                    )[0]

                invited_at = datetime.utcnow() - timedelta(days=random.randint(1, 30))
                confirmed_at = None
                completed_at = None

                if status in ["confirmed", "completed", "no_show"]:
                    confirmed_at = invited_at + timedelta(days=random.randint(1, 5))
                if status == "completed":
                    completed_at = confirmed_at + timedelta(days=random.randint(1, 14))

                assignment = StudyAssignment(
                    study_id=study.id,
                    respondent_id=respondent.id,
                    status=status,
                    invited_at=invited_at,
                    confirmed_at=confirmed_at,
                    completed_at=completed_at,
                    notes=random.choice([None, None, None, "Great participant", "Very engaged", "Rescheduled once", "Referred by friend"]),
                )
                session.add(assignment)
                assignment_count += 1

        await session.flush()
        await session.commit()
        print(f"   ✅ Created {assignment_count} assignments")

        print("\n🎉 Database seeding complete!")
        print(f"   • {len(respondents)} respondents")
        print(f"   • {len(studies)} studies")
        print(f"   • {criteria_count} screener criteria")
        print(f"   • {assignment_count} assignments")


if __name__ == "__main__":
    asyncio.run(seed_database())
