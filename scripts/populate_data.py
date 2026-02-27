"""
Data Population Script for RenewAI
Inserts realistic customers + policies across all segments.
Run: python scripts/populate_data.py
"""
import asyncio
import aiosqlite
import sys
import os
from datetime import datetime, timedelta
import random

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import get_settings
from app.core.security import hash_password

settings = get_settings()

# ── Sample Data Sets ──────────────────────────────────────────────────────────

CUSTOMERS = [
    # Segment: Wealth Builder (High Income, ULIP/Endowment focused)
    ("CUST001", "Rajesh Sharma", 42, "Mumbai", "WhatsApp", "Hindi", "Wealth Builder"),
    ("CUST002", "Priya Mehta", 38, "Delhi", "Email", "English", "Wealth Builder"),
    ("CUST003", "Vikram Desai", 35, "Pune", "Email", "English", "High Value Investor"),
    ("CUST004", "Anjali Kapoor", 44, "Bangalore", "WhatsApp", "Kannada", "Wealth Builder"),
    ("CUST005", "Suresh Nair", 50, "Kochi", "Voice", "Malayalam", "Wealth Builder"),

    # Segment: Budget Conscious (Lower income, term plans)
    ("CUST006", "Meenakshi Iyer", 58, "Chennai", "WhatsApp", "Tamil", "Budget Conscious"),
    ("CUST007", "Ramesh Yadav", 45, "Lucknow", "Voice", "Hindi", "Budget Conscious"),
    ("CUST008", "Sunita Patil", 40, "Nagpur", "WhatsApp", "Marathi", "Budget Conscious"),
    ("CUST009", "Gopal Das", 55, "Kolkata", "Email", "Bengali", "Budget Conscious"),
    ("CUST010", "Anita Verma", 36, "Jaipur", "WhatsApp", "Hindi", "Budget Conscious"),

    # Segment: Middle Income
    ("CUST011", "Imran Khan", 39, "Hyderabad", "WhatsApp", "Urdu", "Middle Income"),
    ("CUST012", "Deepika Rao", 33, "Mysore", "Email", "Kannada", "Middle Income"),
    ("CUST013", "Arjun Singh", 48, "Chandigarh", "Voice", "Hindi", "Middle Income"),
    ("CUST014", "Kavita Joshi", 41, "Ahmedabad", "WhatsApp", "Gujarati", "Middle Income"),
    ("CUST015", "Sanjay Reddy", 52, "Vijayawada", "Email", "Telugu", "Middle Income"),

    # Segment: Senior Citizen (50+, endowment/annuity)
    ("CUST016", "Lakshmi Krishnan", 62, "Coimbatore", "Voice", "Tamil", "Senior Citizen"),
    ("CUST017", "Mohan Gupta", 65, "Varanasi", "Voice", "Hindi", "Senior Citizen"),
    ("CUST018", "Savitri Bose", 68, "Kolkata", "Email", "Bengali", "Senior Citizen"),
    ("CUST019", "Narayan Pillai", 61, "Thiruvananthapuram", "WhatsApp", "Malayalam", "Senior Citizen"),
    ("CUST020", "Shanta Devi", 70, "Patna", "Voice", "Hindi", "Senior Citizen"),

    # Segment: High Value Investor (HNI)
    ("CUST021", "Amitabh Singhania", 55, "Mumbai", "Email", "English", "High Value Investor"),
    ("CUST022", "Rohini Dalmia", 48, "Delhi", "Email", "English", "High Value Investor"),
    ("CUST023", "Kiran Mazumdar", 52, "Bangalore", "WhatsApp", "English", "High Value Investor"),

    # Segment: Young Professional (25-35, new to insurance)
    ("CUST024", "Rahul Mishra", 27, "Noida", "WhatsApp", "Hindi", "Young Professional"),
    ("CUST025", "Sneha Kulkarni", 29, "Pune", "Email", "Marathi", "Young Professional"),
    ("CUST026", "Aditya Sharma", 31, "Gurgaon", "WhatsApp", "Hindi", "Young Professional"),
    ("CUST027", "Pooja Tiwari", 26, "Indore", "WhatsApp", "Hindi", "Young Professional"),

    # Distress cases (for testing)
    ("CUST028", "Meera Pillai", 44, "Chennai", "WhatsApp", "Tamil", "Budget Conscious"),
    ("CUST029", "Rajan Nambiar", 51, "Kochi", "Voice", "Malayalam", "Middle Income"),
    ("CUST030", "Fatima Shaikh", 37, "Mumbai", "WhatsApp", "Urdu", "Budget Conscious"),
]

POLICIES = [
    # Wealth Builder
    ("SLI-2298741", "CUST001", "Term Shield Plus", 10000000, 24000, "2026-03-15", "Annual", None),
    ("SLI-9912345", "CUST002", "ULIP Growth Advantage", 5000000, 75000, "2026-03-20", "Annual", 892000),
    ("SLI-4456721", "CUST003", "ULIP Growth Advantage", 2000000, 50000, "2026-04-01", "Annual", 1245000),
    ("SLI-3345678", "CUST004", "Secure Endowment Plan", 1500000, 45000, "2026-02-28", "Annual", None),
    ("SLI-5567890", "CUST005", "Term Shield Plus", 7500000, 18000, "2026-03-10", "Annual", None),

    # Budget Conscious
    ("SLI-8872134", "CUST006", "Secure Endowment Plan", 500000, 18000, "2026-02-28", "Annual", None),
    ("SLI-7723456", "CUST007", "Term Shield Plus", 2000000, 8500, "2026-03-25", "Semi-Annual", None),
    ("SLI-6634567", "CUST008", "Jeevan Raksha Plan", 750000, 12000, "2026-03-05", "Annual", None),
    ("SLI-5545678", "CUST009", "Secure Endowment Plan", 300000, 15000, "2026-04-10", "Annual", None),
    ("SLI-4456789", "CUST010", "Term Shield Plus", 1000000, 6000, "2026-03-18", "Annual", None),

    # Middle Income
    ("SLI-7765219", "CUST011", "Family Protection Plan", 7500000, 32000, "2026-03-10", "Annual", None),
    ("SLI-8876543", "CUST012", "ULIP Growth Advantage", 1000000, 28000, "2026-04-05", "Annual", 345000),
    ("SLI-9987654", "CUST013", "Term Shield Plus", 5000000, 14000, "2026-03-22", "Annual", None),
    ("SLI-1198765", "CUST014", "Secure Endowment Plan", 800000, 22000, "2026-03-30", "Annual", None),
    ("SLI-2209876", "CUST015", "Family Protection Plan", 3000000, 19000, "2026-04-15", "Annual", None),

    # Senior Citizen
    ("SLI-3310987", "CUST016", "Secure Endowment Plan", 200000, 25000, "2026-02-25", "Annual", None),
    ("SLI-4421098", "CUST017", "Jeevan Raksha Plan", 100000, 30000, "2026-03-08", "Annual", None),
    ("SLI-5532109", "CUST018", "Secure Endowment Plan", 150000, 22000, "2026-04-20", "Annual", None),
    ("SLI-6643210", "CUST019", "Jeevan Raksha Plan", 300000, 18000, "2026-03-12", "Annual", None),
    ("SLI-7754321", "CUST020", "Senior Care Plus", 500000, 35000, "2026-02-20", "Annual", None),

    # HNI
    ("SLI-8865432", "CUST021", "ULIP Growth Advantage", 10000000, 200000, "2026-03-28", "Annual", 4250000),
    ("SLI-9976543", "CUST022", "ULIP Growth Advantage", 8000000, 150000, "2026-04-08", "Annual", 3100000),
    ("SLI-1087654", "CUST023", "Term Shield Plus", 25000000, 85000, "2026-03-15", "Annual", None),

    # Young Professional
    ("SLI-2198765", "CUST024", "Term Shield Plus", 5000000, 9500, "2026-03-20", "Annual", None),
    ("SLI-3209876", "CUST025", "Term Shield Plus", 3000000, 7200, "2026-04-02", "Annual", None),
    ("SLI-4310987", "CUST026", "ULIP Growth Advantage", 1000000, 25000, "2026-03-25", "Annual", 125000),
    ("SLI-5421098", "CUST027", "Term Shield Plus", 2000000, 5500, "2026-04-12", "Annual", None),

    # Distress cases
    ("SLI-6532109", "CUST028", "Secure Endowment Plan", 500000, 14000, "2026-03-01", "Annual", None),
    ("SLI-7643210", "CUST029", "Term Shield Plus", 3000000, 11000, "2026-02-22", "Annual", None),
    ("SLI-8754321", "CUST030", "Family Protection Plan", 2000000, 16000, "2026-03-05", "Annual", None),
]

SAMPLE_INTERACTIONS = [
    # Rajesh - WhatsApp opened, no reply
    ("SLI-2298741", "WhatsApp", "OUTBOUND", "Hi Rajesh-ji! Your Term Shield Plus renewal is due March 15. Premium: ₹24,000. Click here: [link]", 0.0),
    ("SLI-2298741", "Email", "OUTBOUND", "Dear Rajesh, your policy SLI-2298741 renewal notice...", 0.0),

    # Meenakshi - distress scenario
    ("SLI-8872134", "WhatsApp", "OUTBOUND", "Hi Meenakshi-ji! Your policy renewal is due Feb 28.", 0.0),
    ("SLI-8872134", "WhatsApp", "INBOUND", "My husband passed away last month. I don't know what to do with this policy.", -0.8),

    # Vikram - ULIP tech-savvy
    ("SLI-4456721", "Email", "OUTBOUND", "Dear Vikram, your ULIP fund is up 12.4% this year. Renew today...", 0.3),
    ("SLI-4456721", "Email", "INBOUND", "What is the current NAV?", 0.2),

    # Budget conscious objection
    ("SLI-8872134", "WhatsApp", "INBOUND", "The premium is too high, I cannot afford it right now", -0.3),

    # Rajan - financial hardship
    ("SLI-7643210", "Voice", "OUTBOUND", "Hello, this is Suraksha Life. Your renewal is due...", 0.0),
    ("SLI-7643210", "Voice", "INBOUND", "I lost my job last month and have no money right now.", -0.9),
]

DEFAULT_USERS = [
    ("admin@renewai.com", "Admin User", "admin123", "admin"),
    ("agent1@renewai.com", "Priya Renewal Agent", "agent123", "agent"),
    ("agent2@renewai.com", "Ravi Operations", "agent123", "agent"),
    ("manager@renewai.com", "Suresh Manager", "manager123", "manager"),
]


async def populate():
    os.makedirs(os.path.dirname(settings.sqlite_db_path), exist_ok=True)
    
    async with aiosqlite.connect(settings.sqlite_db_path) as db:
        print("📋 Inserting users...")
        for email, name, password, role in DEFAULT_USERS:
            try:
                await db.execute(
                    "INSERT OR IGNORE INTO users (email, name, hashed_password, role) VALUES (?, ?, ?, ?)",
                    (email, name, hash_password(password), role)
                )
            except Exception as e:
                print(f"  Skip {email}: {e}")

        print("👤 Inserting customers...")
        for row in CUSTOMERS:
            await db.execute(
                "INSERT OR IGNORE INTO customers (customer_id, name, age, city, preferred_channel, preferred_language, segment) VALUES (?, ?, ?, ?, ?, ?, ?)",
                row
            )
        
        print("📄 Inserting policies...")
        for row in POLICIES:
            policy_id, cust_id, ptype, sa, premium, due, mode, fv = row
            await db.execute(
                "INSERT OR IGNORE INTO policies (policy_id, customer_id, policy_type, sum_assured, annual_premium, premium_due_date, payment_mode, fund_value, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVE')",
                (policy_id, cust_id, ptype, sa, premium, due, mode, fv)
            )
        
        print("🔄 Initializing policy states...")
        for row in POLICIES:
            policy_id = row[0]
            await db.execute(
                "INSERT OR IGNORE INTO policy_state (policy_id, current_node) VALUES (?, 'ORCHESTRATOR')",
                (policy_id,)
            )
        
        print("💬 Inserting sample interactions...")
        for row in SAMPLE_INTERACTIONS:
            policy_id, channel, direction, content, sentiment = row
            await db.execute(
                "INSERT INTO interactions (policy_id, channel, message_direction, content, sentiment_score) VALUES (?, ?, ?, ?, ?)",
                (policy_id, channel, direction, content, sentiment)
            )
        
        # Set distress flags for known distress cases
        print("⚠️  Setting distress flags...")
        await db.execute("UPDATE policy_state SET distress_flag=1, mode='HUMAN_CONTROL' WHERE policy_id IN ('SLI-8872134','SLI-7643210')")
        await db.execute("UPDATE policy_state SET objection_count=2 WHERE policy_id='SLI-8872134'")
        
        # Create escalation cases for distress policies
        from datetime import datetime, timedelta
        sla = (datetime.utcnow() + timedelta(hours=2)).isoformat()
        await db.execute(
            "INSERT OR IGNORE INTO escalation_cases (policy_id, escalation_reason, priority_score, status, sla_deadline) VALUES (?, ?, ?, ?, ?)",
            ("SLI-8872134", "Customer expressed bereavement distress", 1.0, "OPEN", sla)
        )
        await db.execute(
            "INSERT OR IGNORE INTO escalation_cases (policy_id, escalation_reason, priority_score, status, sla_deadline) VALUES (?, ?, ?, ?, ?)",
            ("SLI-7643210", "Financial hardship — job loss", 0.9, "OPEN", sla)
        )
        
        await db.commit()
    
    print("\n✅ Data population complete!")
    print(f"   Customers: {len(CUSTOMERS)}")
    print(f"   Policies: {len(POLICIES)}")
    print(f"   Interactions: {len(SAMPLE_INTERACTIONS)}")
    print(f"\nDefault Login Credentials:")
    for email, name, password, role in DEFAULT_USERS:
        print(f"   {role:10} | {email:35} | password: {password}")


if __name__ == "__main__":
    asyncio.run(populate())
