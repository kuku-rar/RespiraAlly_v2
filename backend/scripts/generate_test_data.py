"""
Generate Test Data for RespiraAlly V2.0
Uses Faker to create realistic test data in development schema

Run with: uv run python scripts/generate_test_data.py

Generated Data:
- 5 Therapists (Taiwan names, 萬芳醫院, 胸腔內科)
- 50 Patients (Taiwan names, 10 per therapist)
  - All with 6-digit hospital medical record numbers
  - ~10% with exacerbation history (high-risk for dashboard testing)
- ~15,550 Daily Logs (365 days per patient × 85% fill rate)

Sprint 4 Features (Migration 005):
- ✅ Patient exacerbation fields populated (exacerbation_count, hospitalization_count, last_exacerbation_date)
- ⏳ Exacerbations & Risk Assessments tables (TODO - full Sprint 4 implementation)

All data is inserted into 'development' schema for testing
"""

import asyncio
import random
import sys
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

# Add backend src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv

# Load .env
load_dotenv(Path(__file__).parent.parent / ".env")

from faker import Faker
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Import models
from respira_ally.application.auth.use_cases.login_use_case import hash_password
from respira_ally.infrastructure.database.models.daily_log import DailyLogModel
from respira_ally.infrastructure.database.models.patient_profile import PatientProfileModel
from respira_ally.infrastructure.database.models.therapist_profile import TherapistProfileModel
from respira_ally.infrastructure.database.models.user import UserModel

# Note: Exacerbation and RiskAssessment models require migration 005

# ============================================================================
# Configuration
# ============================================================================

DATABASE_URL = "postgresql+asyncpg://admin:admin@localhost:15432/respirally_db"
TARGET_SCHEMA = "development"  # Insert data into development schema

# Data generation settings
fake = Faker(["zh_TW", "en_US"])  # General faker for mixed data
fake_tw = Faker("zh_TW")  # Taiwan Chinese names only for patients
Faker.seed(42)
random.seed(42)

NUM_THERAPISTS = 5
NUM_PATIENTS = 50
PATIENTS_PER_THERAPIST = NUM_PATIENTS // NUM_THERAPISTS
DAYS_OF_DATA = 365


# ============================================================================
# Helper Functions
# ============================================================================


def generate_copd_stage():
    """Generate COPD stage with realistic distribution"""
    stages = ["stage_1", "stage_2", "stage_3", "stage_4"]
    weights = [0.25, 0.35, 0.25, 0.15]  # Most patients in stage 2-3
    return random.choices(stages, weights=weights)[0]


def generate_gold_classification():
    """Generate GOLD classification (A, B, E)"""
    classifications = ["A", "B", "E"]
    weights = [0.40, 0.35, 0.25]  # A=low risk, B=more symptoms, E=exacerbations
    return random.choices(classifications, weights=weights)[0]


def generate_smoking_status_and_years():
    """Generate realistic smoking history"""
    status_choices = ["NEVER", "FORMER", "CURRENT"]
    weights = [0.20, 0.50, 0.30]  # Most are former smokers
    status = random.choices(status_choices, weights=weights)[0]

    if status == "NEVER":
        years = 0
    elif status == "FORMER":
        years = random.randint(5, 40)  # Quit after smoking for years
    else:  # CURRENT
        years = random.randint(1, 50)

    return status, years


def generate_daily_log_data(copd_stage: str, log_date: date) -> dict:
    """Generate realistic daily log metrics based on COPD stage"""
    # Medication compliance decreases with severity
    medication_prob = {
        "stage_1": 0.90,
        "stage_2": 0.85,
        "stage_3": 0.75,
        "stage_4": 0.70,
    }
    medication_taken = random.random() < medication_prob.get(copd_stage, 0.80)

    # Water intake
    water_intake_ml = random.randint(1000, 3000) if random.random() < 0.85 else None

    # Exercise decreases with severity
    if copd_stage in ["stage_3", "stage_4"]:
        exercise_minutes = random.randint(0, 30) if random.random() < 0.60 else None
    else:
        exercise_minutes = random.randint(10, 90) if random.random() < 0.80 else None

    # Smoking for current smokers
    smoking_count = random.randint(5, 20) if random.random() < 0.25 else None

    # Symptoms worse in advanced stages
    symptom_prob = {
        "stage_1": 0.20,
        "stage_2": 0.35,
        "stage_3": 0.55,
        "stage_4": 0.70,
    }
    if random.random() < symptom_prob.get(copd_stage, 0.35):
        symptoms_list = ["咳嗽", "喘", "胸悶", "痰多", "疲倦"]
        symptoms = ", ".join(random.sample(symptoms_list, random.randint(1, 3)))
    else:
        symptoms = None

    # Mood correlates with symptoms
    if symptoms:
        mood = random.choices(["GOOD", "NEUTRAL", "BAD"], weights=[0.1, 0.3, 0.6])[0]
    else:
        mood = random.choices(["GOOD", "NEUTRAL", "BAD"], weights=[0.6, 0.3, 0.1])[0]

    return {
        "log_date": log_date,
        "medication_taken": medication_taken,
        "water_intake_ml": water_intake_ml,
        "exercise_minutes": exercise_minutes,
        "smoking_count": smoking_count,
        "symptoms": symptoms,
        "mood": mood,
    }


# ============================================================================
# Data Generation Functions
# ============================================================================


async def create_therapists(session: AsyncSession) -> list[UserModel]:
    """Create therapist users and profiles"""
    print("\n" + "=" * 70)
    print("👨‍⚕️  Creating Therapists...")
    print("=" * 70)

    therapists = []
    for i in range(1, NUM_THERAPISTS + 1):
        user_id = uuid4()

        # Create user
        user = UserModel(
            user_id=user_id,
            email=f"therapist{i}@respira-ally.com",
            hashed_password=hash_password("SecurePass123!"),
            role="THERAPIST",
        )
        session.add(user)

        # Create therapist profile
        # Taiwan hospital departments (科別)
        departments_list = [
            "胸腔內科",  # Pulmonary Medicine (primary for COPD)
            "重症醫學科",  # Critical Care Medicine
            "呼吸治療科",  # Respiratory Therapy
            "內科",  # Internal Medicine
            "家庭醫學科",  # Family Medicine
        ]

        # Ensure all therapists have 胸腔內科 + optional secondary department
        primary_dept = "胸腔內科"
        secondary_dept = random.choice([d for d in departments_list if d != primary_dept])
        selected_depts = [primary_dept, secondary_dept] if random.random() > 0.3 else [primary_dept]

        therapist = TherapistProfileModel(
            user_id=user_id,
            name=fake_tw.name(),  # ✅ Taiwan Chinese names
            institution="萬芳醫院",  # ✅ Default: Wan Fang Hospital
            license_number=f"T{fake.random_number(digits=6, fix_len=True)}",
            specialties=selected_depts,  # ✅ Chinese department names
        )
        session.add(therapist)
        therapists.append(user)

        print(f"   ✅ {therapist.name} (therapist{i}@respira-ally.com)")

    await session.flush()
    print(f"\n✅ Created {NUM_THERAPISTS} therapists")
    return therapists


async def create_patients(session: AsyncSession, therapists: list[UserModel]) -> list[PatientProfileModel]:
    """Create patient users and profiles"""
    print("\n" + "=" * 70)
    print("🧑‍🦱 Creating Patients...")
    print("=" * 70)

    patients = []
    patient_num = 1

    for therapist_idx, therapist in enumerate(therapists):
        for i in range(PATIENTS_PER_THERAPIST):
            user_id = uuid4()

            # Create user (LINE-based auth for patients)
            user = UserModel(
                user_id=user_id,
                line_user_id=f"U{fake.random_number(digits=32, fix_len=True)}",
                role="PATIENT",
            )
            session.add(user)

            # Generate patient data
            copd_stage = generate_copd_stage()
            gold_class = generate_gold_classification()
            smoking_status, smoking_years = generate_smoking_status_and_years()

            birth_year = random.randint(1940, 1975)  # 50-85 years old
            birth_date = date(birth_year, random.randint(1, 12), random.randint(1, 28))

            # Generate hospital medical record number (6 digits)
            medical_record_number = f"{fake.random_number(digits=6, fix_len=True)}"

            # 10% of patients have exacerbation history (high-risk group for dashboard testing)
            has_exacerbation = random.random() < 0.10
            if has_exacerbation:
                exacerbation_count = random.randint(1, 3)  # 1-3 exacerbations in last 12 months
                hospitalization_count = random.randint(0, min(2, exacerbation_count))  # Some require hospitalization
                # Last exacerbation within past 12 months
                days_ago = random.randint(1, 365)
                last_exacerbation = date.today() - timedelta(days=days_ago)
            else:
                exacerbation_count = 0
                hospitalization_count = 0
                last_exacerbation = None

            # Create patient profile
            patient = PatientProfileModel(
                user_id=user_id,
                therapist_id=therapist.user_id,
                name=fake_tw.name(),  # ✅ Taiwan Chinese names only
                birth_date=birth_date,
                gender=random.choice(["MALE", "FEMALE"]),
                hospital_medical_record_number=medical_record_number,  # ✅ 6-digit medical record number
                height_cm=random.randint(150, 185),
                weight_kg=Decimal(str(random.uniform(50.0, 95.0))),
                smoking_status=smoking_status,
                smoking_years=smoking_years,
                exacerbation_count_last_12m=exacerbation_count,  # ✅ Sprint 4 field
                hospitalization_count_last_12m=hospitalization_count,  # ✅ Sprint 4 field
                last_exacerbation_date=last_exacerbation,  # ✅ Sprint 4 field
                medical_history={
                    "copd_stage": copd_stage,
                    "gold_classification": gold_class,
                    "diagnosis_year": random.randint(2015, 2023),
                    "comorbidities": random.sample(
                        ["hypertension", "diabetes", "heart_disease", "asthma"],
                        random.randint(0, 2),
                    ),
                },
                contact_info={
                    "phone": fake_tw.phone_number(),  # Taiwan phone format
                    "emergency_contact": fake_tw.phone_number(),  # Taiwan phone format
                },
            )
            session.add(patient)
            patients.append(patient)

            if patient_num % 10 == 0:
                print(f"   ✅ Created {patient_num}/{NUM_PATIENTS} patients")

            patient_num += 1

    await session.flush()
    print(f"\n✅ Created {NUM_PATIENTS} patients assigned to {NUM_THERAPISTS} therapists")
    return patients


async def create_daily_logs(session: AsyncSession, patients: list[PatientProfileModel]):
    """Create daily logs for all patients"""
    print("\n" + "=" * 70)
    print("📊 Creating Daily Logs...")
    print("=" * 70)

    end_date = date.today()
    start_date = end_date - timedelta(days=DAYS_OF_DATA - 1)

    total_logs = 0
    batch_size = 1000

    for patient in patients:
        copd_stage = patient.medical_history.get("copd_stage", "stage_2")

        for day_offset in range(DAYS_OF_DATA):
            # 85% fill rate (patients miss some days)
            if random.random() > 0.85:
                continue

            log_date = start_date + timedelta(days=day_offset)
            log_data = generate_daily_log_data(copd_stage, log_date)

            daily_log = DailyLogModel(patient_id=patient.user_id, **log_data)
            session.add(daily_log)
            total_logs += 1

            # Batch commit for performance
            if total_logs % batch_size == 0:
                await session.flush()
                print(f"   ✅ Inserted {total_logs:,} logs...")

    await session.flush()
    print(f"\n✅ Created {total_logs:,} daily logs ({DAYS_OF_DATA} days × {NUM_PATIENTS} patients × ~85% fill rate)")


# TODO: Re-enable after migration 005 is applied
# async def create_exacerbations(session: AsyncSession, patients: list[PatientProfileModel]):
#     """Create exacerbation records (requires migration 005)"""
#     pass

# async def create_risk_assessments(session: AsyncSession, patients: list[PatientProfileModel]):
#     """Create latest risk assessment for each patient (requires migration 005)"""
#     pass


# ============================================================================
# Main
# ============================================================================


async def main():
    """Generate all test data"""
    print("\n" + "=" * 70)
    print("🚀 RespiraAlly V2.0 - Test Data Generation")
    print("=" * 70)
    print(f"📌 Target Schema: {TARGET_SCHEMA}")
    print(f"📌 Database: {DATABASE_URL.split('@')[1]}")
    print()

    # Create engine with schema set
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with async_session() as session:
            # Set schema for this session
            await session.execute(text(f"SET search_path TO {TARGET_SCHEMA}"))

            # Generate data
            therapists = await create_therapists(session)
            patients = await create_patients(session, therapists)
            await create_daily_logs(session, patients)

            # TODO: Uncomment after migration 005 is applied
            # await create_exacerbations(session, patients)
            # await create_risk_assessments(session, patients)

            # Count high-risk patients (with exacerbation history)
            high_risk_count = sum(1 for p in patients if p.exacerbation_count_last_12m > 0)

            # Commit all
            await session.commit()

            print("\n" + "=" * 70)
            print("✅ Test Data Generation Complete!")
            print("=" * 70)
            print("\n📊 Summary:")
            print(f"   - Schema: {TARGET_SCHEMA}")
            print(f"   - Therapists: {NUM_THERAPISTS}")
            print(f"   - Patients: {NUM_PATIENTS}")
            print(f"     ⚠️  High-Risk Patients (with exacerbation): {high_risk_count} (~10%)")
            print(f"   - Daily Logs: ~{NUM_PATIENTS * DAYS_OF_DATA * 0.85:,.0f}")
            print()
            print("⏳ Pending (requires full Sprint 4):")
            print(f"   - Exacerbations table: 0 (TODO)")
            print(f"   - Risk Assessments table: 0 (TODO)")
            print()
            print("🔐 Test Credentials:")
            print("   Email: therapist1@respira-ally.com")
            print("   Password: SecurePass123!")
            print()
            print("📋 Verify:")
            print(f"   docker exec respirally-postgres psql -U admin -d respirally_db \\")
            print(f"     -c 'SELECT count(*) FROM {TARGET_SCHEMA}.users;'")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
