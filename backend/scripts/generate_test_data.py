"""
Generate Test Data using Faker
生成測試資料：50 位病患 + 一年份日誌資料

Run with: uv run python scripts/generate_test_data.py

Generated Data:
- 5 Therapists (治療師)
- 50 Patients (病患) - 每位治療師 10 位病患
- ~18,250 Daily Logs (日誌) - 每位病患約 365 天資料
"""
import asyncio
from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import uuid4
import random

from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
import sqlalchemy as sa

from respira_ally.infrastructure.database.session import Base
from respira_ally.infrastructure.database.models.user import UserModel
from respira_ally.infrastructure.database.models.therapist_profile import TherapistProfileModel
from respira_ally.infrastructure.database.models.patient_profile import PatientProfileModel
from respira_ally.infrastructure.database.models.daily_log import DailyLogModel
from respira_ally.application.auth.use_cases.login_use_case import hash_password


# ============================================================================
# Configuration
# ============================================================================

DATABASE_URL = "postgresql+asyncpg://admin:admin@localhost:15432/respirally_db"
TEST_SCHEMA = "test_data"  # 測試資料專用 schema

fake = Faker(['zh_TW', 'en_US'])  # 繁體中文 + 英文
Faker.seed(42)  # 確保每次生成相同資料
random.seed(42)

NUM_THERAPISTS = 5
NUM_PATIENTS = 50
PATIENTS_PER_THERAPIST = NUM_PATIENTS // NUM_THERAPISTS
DAYS_OF_DATA = 365  # 一年份資料


# ============================================================================
# Data Generation Functions
# ============================================================================

def generate_therapist_data(index: int) -> dict:
    """
    生成治療師資料（萬芳醫院專用）

    - 醫院固定：萬芳醫院
    - 科別預設：胸腔內科
    """
    return {
        "line_user_id": f"therapist_{uuid4().hex[:8]}",
        "role": "THERAPIST",
        "email": f"therapist{index + 1}@respira-ally.com",
        "hashed_password": hash_password("SecurePass123!"),
        "name": fake.name(),
        "institution": "萬芳醫院",  # 固定為萬芳醫院
        "license_number": f"LIC{random.randint(100000, 999999)}",
        "specialties": ["胸腔內科"]  # 預設為胸腔內科
    }


def generate_patient_data(therapist_id: str) -> dict:
    """
    生成病患資料（符合 COPD 病患特徵）

    - 年齡：50-85 歲（COPD 好發年齡）
    - BMI：18-35（涵蓋過輕到肥胖）
    - 性別：隨機分布
    """
    # 生成 50-85 歲的出生日期
    age = random.randint(50, 85)
    birth_date = date.today() - timedelta(days=age * 365 + random.randint(0, 365))

    # 生成身高體重（BMI 18-35）
    gender = random.choice(["MALE", "FEMALE", "OTHER"])
    if gender == "MALE":
        height_cm = random.randint(160, 180)
    else:
        height_cm = random.randint(150, 170)

    # 計算合理體重（BMI 18-35）
    target_bmi = random.uniform(18, 35)
    weight_kg = round(target_bmi * (height_cm / 100) ** 2, 1)

    # Smoking status and years (must satisfy constraint)
    smoking_status = random.choices(
        ["NEVER", "FORMER", "CURRENT"],
        weights=[30, 50, 20]  # COPD 病患多為前吸煙者
    )[0]

    # Constraint: NEVER must have NULL or 0 smoking_years
    if smoking_status == "NEVER":
        smoking_years = None
    else:  # FORMER or CURRENT
        smoking_years = random.randint(10, 40)

    return {
        "line_user_id": f"patient_{uuid4().hex[:8]}",
        "role": "PATIENT",
        "therapist_id": therapist_id,
        "name": fake.name(),
        "birth_date": birth_date,
        "gender": gender,
        "height_cm": height_cm,
        "weight_kg": Decimal(str(weight_kg)),
        "smoking_status": smoking_status,
        "smoking_years": smoking_years,
        "contact_info": {
            "phone": fake.phone_number(),
            "emergency_contact": fake.name(),
            "emergency_phone": fake.phone_number()
        },
        "medical_history": {
            "copd_stage": random.choice(["stage_1", "stage_2", "stage_3", "stage_4"]),
            "diagnosis_date": (date.today() - timedelta(days=random.randint(365, 3650))).isoformat(),
            "comorbidities": random.sample(
                ["Hypertension", "Diabetes", "Heart Disease", "Asthma", "Arthritis"],
                k=random.randint(0, 3)
            ),
            "medications": random.sample(
                ["Bronchodilator", "Corticosteroid", "Oxygen Therapy", "Antibiotic"],
                k=random.randint(1, 3)
            )
        }
    }


def generate_daily_log_data(patient_id: str, log_date: date, patient_profile: dict) -> dict:
    """
    生成每日日誌資料（符合真實情境）

    - 服藥遵從率：60-95%
    - 水分攝取：500-3000ml（年長者較少）
    - 步數：0-10000（年長者活動量較少）
    - 心情分布：Good 40%, Neutral 40%, Bad 20%
    """
    # 服藥遵從率（部分病患較不規律）
    medication_adherence = random.random()
    medication_taken = medication_adherence > 0.3  # 70% 遵從率

    # 水分攝取（年長者較少，但需要提醒多喝水）
    water_intake_ml = random.randint(500, 3000)
    if random.random() < 0.2:  # 20% 機率攝取不足
        water_intake_ml = random.randint(300, 800)

    # 步數（年長者活動量較少，COPD 病患更少）
    copd_stage = patient_profile.get("medical_history", {}).get("copd_stage", "stage_2")
    if copd_stage in ["stage_3", "stage_4"]:
        steps_count = random.randint(0, 3000)  # 嚴重期活動量低
    else:
        steps_count = random.randint(1000, 8000)  # 輕中度可活動

    # 症狀描述（20% 機率有症狀）
    symptoms = None
    if random.random() < 0.2:
        symptoms = random.choice([
            "輕微咳嗽",
            "呼吸短促",
            "胸悶",
            "痰多",
            "咳嗽加劇",
            "氣喘",
            "疲倦",
            "無明顯症狀"
        ])

    # 心情分布（Good 40%, Neutral 40%, Bad 20%）
    mood = random.choices(
        ["GOOD", "NEUTRAL", "BAD"],
        weights=[40, 40, 20]
    )[0]

    return {
        "patient_id": patient_id,
        "log_date": log_date,
        "medication_taken": medication_taken,
        "water_intake_ml": water_intake_ml,
        "steps_count": steps_count,
        "symptoms": symptoms,
        "mood": mood
    }


# ============================================================================
# Database Population
# ============================================================================

async def populate_database():
    """填充資料庫（使用獨立 schema）"""
    print("🚀 開始生成測試資料...")
    print(f"📊 目標：{NUM_THERAPISTS} 位治療師, {NUM_PATIENTS} 位病患, 約 {NUM_PATIENTS * DAYS_OF_DATA} 筆日誌")
    print(f"📁 Schema: {TEST_SCHEMA}")

    # Create async engine
    engine = create_async_engine(DATABASE_URL, echo=False)

    # 1. Create test schema (drop if exists)
    print(f"\n1️⃣ 創建測試 schema: {TEST_SCHEMA}...")
    async with engine.begin() as conn:
        # Drop schema if exists
        await conn.execute(sa.text(f"DROP SCHEMA IF EXISTS {TEST_SCHEMA} CASCADE"))
        # Create new schema
        await conn.execute(sa.text(f"CREATE SCHEMA {TEST_SCHEMA}"))
        # Set search_path to use test schema
        await conn.execute(sa.text(f"SET search_path TO {TEST_SCHEMA}, public"))
        print(f"✅ Schema {TEST_SCHEMA} 創建完成")

        # Create all tables in test schema
        print(f"   創建資料表...")
        await conn.run_sync(Base.metadata.create_all)
        print(f"✅ 資料表創建完成")

    # Create session factory with test schema
    async_session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_factory() as session:
        # Set search_path for this session
        await session.execute(sa.text(f"SET search_path TO {TEST_SCHEMA}, public"))
        # 2. Create Therapists
        print(f"\n2️⃣ 創建 {NUM_THERAPISTS} 位治療師...")
        therapists = []
        for i in range(NUM_THERAPISTS):
            therapist_data = generate_therapist_data(i)

            # Create user
            therapist_user = UserModel(
                line_user_id=therapist_data["line_user_id"],
                role=therapist_data["role"],
                email=therapist_data["email"],
                hashed_password=therapist_data["hashed_password"],
            )
            session.add(therapist_user)
            await session.flush()

            # Create therapist profile
            therapist_profile = TherapistProfileModel(
                user_id=therapist_user.user_id,
                name=therapist_data["name"],
                institution=therapist_data["institution"],
                license_number=therapist_data["license_number"],
                specialties=therapist_data["specialties"],
            )
            session.add(therapist_profile)
            therapists.append(therapist_user)

            print(f"  ✅ {therapist_data['name']} ({therapist_data['email']})")

        await session.commit()
        print(f"✅ {NUM_THERAPISTS} 位治療師創建完成")

        # 3. Create Patients
        print(f"\n3️⃣ 創建 {NUM_PATIENTS} 位病患...")
        patients = []
        patient_profiles_data = []

        for i in range(NUM_PATIENTS):
            # Assign to therapist (round-robin)
            therapist = therapists[i % NUM_THERAPISTS]

            patient_data = generate_patient_data(therapist.user_id)

            # Create user
            patient_user = UserModel(
                line_user_id=patient_data["line_user_id"],
                role=patient_data["role"],
                email=None,
                hashed_password=None,
            )
            session.add(patient_user)
            await session.flush()

            # Create patient profile
            patient_profile = PatientProfileModel(
                user_id=patient_user.user_id,
                therapist_id=patient_data["therapist_id"],
                name=patient_data["name"],
                birth_date=patient_data["birth_date"],
                gender=patient_data["gender"],
                height_cm=patient_data["height_cm"],
                weight_kg=patient_data["weight_kg"],
                smoking_status=patient_data["smoking_status"],
                smoking_years=patient_data["smoking_years"],
                contact_info=patient_data["contact_info"],
                medical_history=patient_data["medical_history"],
            )
            session.add(patient_profile)
            patients.append(patient_user)
            patient_profiles_data.append(patient_data)

            if (i + 1) % 10 == 0:
                print(f"  ✅ 已創建 {i + 1}/{NUM_PATIENTS} 位病患")

        await session.commit()
        print(f"✅ {NUM_PATIENTS} 位病患創建完成")

        # 4. Create Daily Logs
        print(f"\n4️⃣ 創建日誌資料（每位病患 {DAYS_OF_DATA} 天）...")
        total_logs = 0

        for idx, patient_user in enumerate(patients):
            patient_profile_data = patient_profiles_data[idx]

            # Generate logs for past year
            start_date = date.today() - timedelta(days=DAYS_OF_DATA)
            for day_offset in range(DAYS_OF_DATA):
                log_date = start_date + timedelta(days=day_offset)

                # 模擬真實情境：80% 機率有填寫日誌
                if random.random() < 0.8:
                    log_data = generate_daily_log_data(
                        patient_user.user_id,
                        log_date,
                        patient_profile_data
                    )

                    daily_log = DailyLogModel(
                        patient_id=log_data["patient_id"],
                        log_date=log_data["log_date"],
                        medication_taken=log_data["medication_taken"],
                        water_intake_ml=log_data["water_intake_ml"],
                        steps_count=log_data["steps_count"],
                        symptoms=log_data["symptoms"],
                        mood=log_data["mood"],
                    )
                    session.add(daily_log)
                    total_logs += 1

            # Commit every 10 patients
            if (idx + 1) % 10 == 0:
                await session.commit()
                print(f"  ✅ 已完成 {idx + 1}/{NUM_PATIENTS} 位病患的日誌資料 (累計 {total_logs} 筆)")

        await session.commit()
        print(f"✅ {total_logs} 筆日誌資料創建完成")

    await engine.dispose()

    # 5. Summary
    print("\n" + "=" * 80)
    print("🎉 測試資料生成完成！")
    print("=" * 80)
    print(f"📋 統計資料:")
    print(f"  - Schema: {TEST_SCHEMA}")
    print(f"  - 治療師: {NUM_THERAPISTS} 位")
    print(f"  - 病患: {NUM_PATIENTS} 位")
    print(f"  - 日誌: {total_logs} 筆 (約 {total_logs / NUM_PATIENTS:.1f} 筆/人)")
    print(f"  - 時間範圍: {DAYS_OF_DATA} 天 ({start_date} ~ {date.today()})")
    print("\n🔐 測試帳號:")
    print(f"  - Email: therapist1@respira-ally.com")
    print(f"  - Password: SecurePass123!")
    print("\n📖 使用方式:")
    print(f"  查詢資料: SELECT * FROM {TEST_SCHEMA}.users;")
    print(f"  清理資料: DROP SCHEMA {TEST_SCHEMA} CASCADE;")
    print(f"  重新生成: uv run python scripts/generate_test_data.py")
    print("=" * 80)


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    asyncio.run(populate_database())
