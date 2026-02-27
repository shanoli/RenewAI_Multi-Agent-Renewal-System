"""
RAG Population Script — pushes dummy policy docs, objections, regulations to Chroma.
Run: python scripts/populate_rag.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.rag.chroma_store import add_documents, init_chroma, get_collection
from app.core.config import get_settings

settings = get_settings()

# ── Policy Documents ──────────────────────────────────────────────────────────
POLICY_DOCUMENTS = [
    {
        "id": "doc_term_shield_plus",
        "text": """Term Shield Plus Policy — Suraksha Life Insurance
Policy Type: Pure Term Life Insurance
Sum Assured Options: ₹25 lakh to ₹10 crore
Premium Range: ₹5,000 to ₹1,00,000 per year
Policy Terms: 10, 15, 20, 25, 30 years
Key Benefits:
1. Life cover up to age 75 — ensures family is protected even if policyholder passes away
2. Critical illness rider available — covers 34 critical illnesses including cancer, heart attack, kidney failure
3. Accidental death benefit rider — 2x sum assured on accidental death
4. Premium waiver on disability — future premiums waived if permanent disability occurs
5. Tax benefit under Section 80C — premium up to ₹1.5 lakh deductible
6. Tax-free maturity benefit under Section 10(10D)
Grace period: 30 days for annual/semi-annual, 15 days for monthly
Lapse revival: Policy can be revived within 5 years of lapse
Free-look period: 30 days from policy receipt
Payment modes: Annual, Semi-Annual, Quarterly, Monthly
""",
        "metadata": {"policy_type": "Term Shield Plus", "category": "term", "version": "v3", "approved_by_compliance": True}
    },
    {
        "id": "doc_secure_endowment",
        "text": """Secure Endowment Plan — Suraksha Life Insurance
Policy Type: Endowment with Guaranteed Returns
Sum Assured Options: ₹1 lakh to ₹25 lakh
Premium Range: ₹10,000 to ₹1,00,000 per year
Policy Terms: 10, 15, 20 years
Key Benefits:
1. Guaranteed maturity benefit — 125% of total premiums paid on maturity
2. Life cover throughout policy term — sum assured paid on death
3. Bonus additions — reversionary bonus declared annually (~4-6%)
4. Loan facility — borrow up to 90% of surrender value after 3 years
5. Partial withdrawal allowed — up to 50% after 5 years
6. Tax benefits — Section 80C deduction + Section 10(10D) maturity exemption
7. Guaranteed additions — ₹500 per ₹1000 sum assured for first 5 years
Surrender Value: Available after 3 years (30% of paid premiums in year 3, rising each year)
Grace period: 30 days
Revival period: 2 years from lapse date
Payment modes: Annual, Semi-Annual, Quarterly, Monthly (ECS/NACH)
""",
        "metadata": {"policy_type": "Secure Endowment Plan", "category": "endowment", "version": "v2", "approved_by_compliance": True}
    },
    {
        "id": "doc_ulip_growth",
        "text": """ULIP Growth Advantage — Suraksha Life Insurance
Policy Type: Unit Linked Insurance Plan
Sum Assured Options: 10x annual premium (minimum)
Premium Range: ₹25,000 to ₹5,00,000 per year
Policy Terms: 10, 15, 20 years
Fund Options:
- Equity Growth Fund: 80% equity, 20% debt — for aggressive investors
- Balanced Advantage Fund: 60% equity, 40% debt — moderate risk
- Secure Income Fund: 20% equity, 80% debt — conservative investors
- Pure Debt Fund: 100% debt — capital preservation
Key Benefits:
1. Market-linked returns with life cover — best of both worlds
2. Fund switching — up to 4 free switches per year
3. Premium redirection — change fund allocation for future premiums free of charge
4. Systematic Transfer Option (STO) — gradual fund migration
5. Loyalty additions — additional units added from year 6 onwards
6. Life cover: higher of sum assured or fund value
7. Mortality charges deducted from fund — transparency in pricing
Lock-in: 5 years (IRDAI mandated for all ULIPs)
Partial withdrawal: After 5-year lock-in, up to 25% per year
Fund charges: 1.35% per annum fund management charge
Tax: LTCG tax above ₹1 lakh gain (post-2021 IRDAI circular)
""",
        "metadata": {"policy_type": "ULIP Growth Advantage", "category": "ulip", "version": "v4", "approved_by_compliance": True}
    },
    {
        "id": "doc_family_protection",
        "text": """Family Protection Plan — Suraksha Life Insurance
Policy Type: Whole Life + Family Income Benefit
Sum Assured Options: ₹5 lakh to ₹5 crore
Premium Range: ₹8,000 to ₹80,000 per year
Policy Terms: Whole life (up to age 99)
Key Benefits:
1. Lifetime coverage — policy does not expire at any age
2. Family income benefit — monthly income to family for 10 years after policyholder's death
3. Critical illness cover — lump sum on diagnosis of 36 specified illnesses
4. Accidental disability benefit — monthly income if permanently disabled
5. Children's education benefit rider — funds released at child's education milestones
6. Waiver of premium on critical illness — no premiums due after CI diagnosis
7. Guaranteed surrender value after 5 years
Premium payment terms: 10, 15, 20 years (then policy continues premium-free)
Grace period: 30 days
Loan: Up to 80% of surrender value after 5 years
""",
        "metadata": {"policy_type": "Family Protection Plan", "category": "whole_life", "version": "v2", "approved_by_compliance": True}
    },
    {
        "id": "doc_jeevan_raksha",
        "text": """Jeevan Raksha Plan — Suraksha Life Insurance
Policy Type: Traditional Participating Endowment (Regional Focus)
Sum Assured Options: ₹50,000 to ₹10 lakh
Premium Range: ₹5,000 to ₹50,000 per year
Target Segment: Budget Conscious, Rural, Senior Citizens
Available Languages: Hindi, Marathi, Bengali, Tamil, Telugu, Kannada, Malayalam, Gujarati
Key Benefits:
1. Simple savings + protection — no complex fund choices
2. Guaranteed maturity benefit — 110% of sum assured guaranteed at maturity
3. Bonus declared annually — typically 3-5% of sum assured
4. Affordable premiums — designed for middle-income families
5. Easy claim settlement — simplified documentation process
6. Village/rural bank payment accepted — no need for online banking
7. Joint life option — cover husband and wife under one policy
8. Child marriage/education goal planning — milestones aligned to common family needs
Grace period: 60 days (extended for rural customers)
Revival: 3 years from lapse
Nomination: Easy nomination and assignment process
""",
        "metadata": {"policy_type": "Jeevan Raksha Plan", "category": "endowment", "version": "v1", "approved_by_compliance": True}
    },
    {
        "id": "doc_senior_care",
        "text": """Senior Care Plus — Suraksha Life Insurance
Policy Type: Senior Citizen Annuity + Protection Plan
Entry Age: 55 to 75 years
Sum Assured Options: ₹1 lakh to ₹25 lakh
Premium Range: ₹20,000 to ₹5,00,000 (single premium or limited pay)
Key Benefits:
1. Immediate annuity option — regular monthly income from day 1
2. Joint life annuity — continued payment to spouse after policyholder's death
3. Return of purchase price — original premium returned to nominees on death
4. Hospital cash benefit — ₹2,000 per day for hospitalization (up to 30 days/year)
5. Domiciliary treatment covered — in-home medical care post-hospitalization
6. Tax benefit under Section 80C and 80D
7. Inflation-adjusted annuity option available (+5% per year)
Medical underwriting: Only basic health declaration (no medical tests for SA up to ₹5 lakh)
Surrender: Not allowed for annuity plans; surrender allowed for pure protection plans after 2 years
""",
        "metadata": {"policy_type": "Senior Care Plus", "category": "annuity", "version": "v1", "approved_by_compliance": True}
    }
]

# ── Objection Library ─────────────────────────────────────────────────────────
OBJECTIONS = [
    # Financial Hardship
    {"id": "obj_001", "text": "I lost my job and cannot pay the premium right now. Please understand my situation.", "metadata": {"category": "financial_hardship", "language": "English", "severity": "high"}},
    {"id": "obj_002", "text": "Meri naukri chali gayi hai, premium nahi bhar sakta. Koi raasta hai? (I lost my job, can't pay premium. Is there a way?)", "metadata": {"category": "financial_hardship", "language": "Hindi", "severity": "high"}},
    {"id": "obj_003", "text": "My husband passed away last month. I don't know what to do with this policy.", "metadata": {"category": "bereavement_distress", "language": "English", "severity": "critical"}},
    {"id": "obj_004", "text": "En kaalathu pathi pesinadhillai. Premiun paymaent pannadharkku panam illai. (Difficult time. No money for premium.)", "metadata": {"category": "financial_hardship", "language": "Tamil", "severity": "high"}},
    {"id": "obj_005", "text": "I am in hospital with my father. This is not a good time to talk about insurance.", "metadata": {"category": "personal_crisis", "language": "English", "severity": "high"}},
    {"id": "obj_006", "text": "Aami ekhon boro bipode achi. Chaakriti haariyechi, premium ditey parbo na. (In big trouble. Lost job, can't pay.)", "metadata": {"category": "financial_hardship", "language": "Bengali", "severity": "high"}},

    # Pricing Objections
    {"id": "obj_007", "text": "The premium is too high this year. Can you reduce it?", "metadata": {"category": "pricing_objection", "language": "English", "severity": "medium"}},
    {"id": "obj_008", "text": "Premium bahut zyada lag raha hai, thoda kam kar sakte ho? (Premium is very high, can you reduce?)", "metadata": {"category": "pricing_objection", "language": "Hindi", "severity": "medium"}},
    {"id": "obj_009", "text": "Naan premium reducku panna mudiyuma? Too expensive for me now.", "metadata": {"category": "pricing_objection", "language": "Tamil", "severity": "medium"}},
    {"id": "obj_010", "text": "Insurance pe itna kharch? Bache ke school fees bhi deni hai. (Spending on insurance? School fees also due.)", "metadata": {"category": "pricing_objection", "language": "Hindi", "severity": "medium"}},

    # EMI / Payment Options
    {"id": "obj_011", "text": "Can I pay in monthly installments instead of annual?", "metadata": {"category": "emi_query", "language": "English", "severity": "low"}},
    {"id": "obj_012", "text": "Kya main monthly pay kar sakta hoon? Ek baar mein poora nahi de sakta.", "metadata": {"category": "emi_query", "language": "Hindi", "severity": "low"}},
    {"id": "obj_013", "text": "Is there an EMI option? I prefer to break the payment.", "metadata": {"category": "emi_query", "language": "English", "severity": "low"}},

    # Product Confusion
    {"id": "obj_014", "text": "What is the benefit of continuing this policy? Explain clearly.", "metadata": {"category": "product_query", "language": "English", "severity": "medium"}},
    {"id": "obj_015", "text": "Mera ULIP fund value kya hai abhi? Market down hai toh renew kyon karoon? (What is my ULIP fund value? Market is down, why renew?)", "metadata": {"category": "product_query", "language": "Hindi", "severity": "medium"}},
    {"id": "obj_016", "text": "I heard insurance premiums are not tax-free anymore. Is that true?", "metadata": {"category": "regulatory_concern", "language": "English", "severity": "medium"}},
    {"id": "obj_017", "text": "I want to surrender this policy and take my money. What will I get?", "metadata": {"category": "surrender_intent", "language": "English", "severity": "high"}},
    {"id": "obj_018", "text": "Kya yeh policy maturity pe paisa deti hai? Mujhe samajh nahi aaya. (Does this policy give money at maturity? Not understood.)", "metadata": {"category": "product_confusion", "language": "Hindi", "severity": "medium"}},

    # Not Interested / Rejection
    {"id": "obj_019", "text": "I am not interested in renewing. Please remove my number.", "metadata": {"category": "not_interested", "language": "English", "severity": "high"}},
    {"id": "obj_020", "text": "Mujhe yeh insurance nahi chahiye. Call mat karo. (Don't want this insurance. Don't call.)", "metadata": {"category": "not_interested", "language": "Hindi", "severity": "high"}},
    {"id": "obj_021", "text": "I already bought another policy from LIC. This one is not needed.", "metadata": {"category": "competitor_switch", "language": "English", "severity": "high"}},

    # Timing Objections
    {"id": "obj_022", "text": "Please call me after March. Very busy right now.", "metadata": {"category": "timing_objection", "language": "English", "severity": "low"}},
    {"id": "obj_023", "text": "Festival time chal raha hai, baad mein baat karte hain. (Festival time going on, let's talk later.)", "metadata": {"category": "timing_objection", "language": "Hindi", "severity": "low"}},

    # Regional Specific
    {"id": "obj_024", "text": "Naan WhatsApp-la premium pay panna mudiyuma? Online payment panna theriyaadhu. (Can I pay premium via WhatsApp? Don't know online payment.)", "metadata": {"category": "digital_literacy", "language": "Tamil", "severity": "medium"}},
    {"id": "obj_025", "text": "Ente bank account number maattiyathaanu. Enikku appol eniku premium cheyyaan kazhiyilla. (My bank account changed. So I can't pay premium.)", "metadata": {"category": "payment_issue", "language": "Malayalam", "severity": "medium"}},
    {"id": "obj_026", "text": "Ninna insurance company trust maadthini. Namage seriyaagi claim settle maadalla. (Don't trust your company. Claims not settled properly.)", "metadata": {"category": "trust_issue", "language": "Kannada", "severity": "high"}},
    {"id": "obj_027", "text": "Aami insurance company-r upor bishwaas kori na. Claim dile dey na. (Don't trust insurance company. They don't pay claims.)", "metadata": {"category": "trust_issue", "language": "Bengali", "severity": "high"}},

    # Playbook responses for objections
    {"id": "resp_001", "text": "For financial hardship: Offer Premium Pause (holiday) for 3 months — policyholder keeps coverage. Mention NACH mandate change for smaller installments. Offer to connect with Relationship Manager for hardship deferral.", "metadata": {"category": "financial_hardship_response", "language": "English", "severity": "playbook"}},
    {"id": "resp_002", "text": "For pricing objections: Compare premium as daily cost (₹24,000/year = ₹66/day — less than a cup of chai). Highlight tax savings (80C deduction). Show riders being offered free. Offer to remove paid riders to reduce premium.", "metadata": {"category": "pricing_response", "language": "English", "severity": "playbook"}},
    {"id": "resp_003", "text": "For surrender intent: Offer paid-up policy option instead of surrender. Show surrender value vs maturity benefit comparison. Escalate to Relationship Manager with calculation sheet.", "metadata": {"category": "surrender_response", "language": "English", "severity": "playbook"}},
    {"id": "resp_004", "text": "For competitor switch: Acknowledge customer's choice without pressure. Share Suraksha's claim settlement ratio (98.2%). Mention the cost of re-underwriting at older age. Offer a product comparison call.", "metadata": {"category": "competitor_response", "language": "English", "severity": "playbook"}},
]

# ── Regulatory Guidelines ─────────────────────────────────────────────────────
REGULATIONS = [
    {"id": "reg_001", "text": "IRDAI Circular 2024: All AI-generated customer communications must clearly disclose that the message originates from an automated AI system. The disclosure must appear in the same language as the communication. Mandatory text: 'This message is from an AI assistant. You can request a human agent at any time.' This is non-negotiable and non-waivable.", "metadata": {"regulator": "IRDAI", "year": 2024, "category": "ai_disclosure"}},
    {"id": "reg_002", "text": "IRDAI Technology Framework 2024: Insurers using AI for customer communication must maintain complete audit logs of every AI-generated message including: system prompt used, model name, timestamp, channel, and customer identifier. These logs must be retained for 7 years and made available to regulators on demand.", "metadata": {"regulator": "IRDAI", "year": 2024, "category": "audit_compliance"}},
    {"id": "reg_003", "text": "IRDAI Guidelines on Grievance Redressal 2024: Any customer expressing financial distress, bereavement, or seeking policy surrender must be immediately connected to a human agent. AI systems must not attempt to persuade distressed customers to continue without human intervention. A human agent must respond within 2 hours for Priority 1 cases.", "metadata": {"regulator": "IRDAI", "year": 2024, "category": "distress_handling"}},
    {"id": "reg_004", "text": "RBI FREE-AI Framework 2024: AI customer communication must not include false urgency tactics, misleading statistics, or fabricated policy benefits. All premium figures, maturity amounts, and benefit claims must be sourced from verified policy documents. Any deviation from actual policy terms is a regulatory violation.", "metadata": {"regulator": "RBI", "year": 2024, "category": "accuracy_compliance"}},
    {"id": "reg_005", "text": "IRDAI Policyholder Protection Regulations: Customers have the right to opt out of automated communications at any time. Any message that prompts opting out ('STOP', 'HUMAN', 'OPT OUT') must immediately route to human queue. WhatsApp opt-out via 'STOP' and email opt-out via unsubscribe links are mandatory.", "metadata": {"regulator": "IRDAI", "year": 2023, "category": "opt_out_compliance"}},
    {"id": "reg_006", "text": "IRDAI Data Privacy Guidelines: Customer personal information (name, age, policy details) used in AI communications must be handled under data minimization principles. AI systems must not request or process sensitive financial information (bank account, OTPs, passwords) over automated channels. Any such request by AI is a compliance violation.", "metadata": {"regulator": "IRDAI", "year": 2024, "category": "data_privacy"}},
    {"id": "reg_007", "text": "Insurance Ombudsman Rule 2024: AI renewal communications that misrepresent lapse consequences (falsely claiming policy becomes void immediately on due date) are prohibited. Actual grace period of 30 days must be communicated. Creating false urgency by misrepresenting lapse timing is grounds for consumer complaint.", "metadata": {"regulator": "Insurance Ombudsman", "year": 2024, "category": "lapse_communication"}},
    {"id": "reg_008", "text": "IRDAI WhatsApp/Digital Channel Guidelines: Renewal reminders via WhatsApp must be sent only between 8 AM and 8 PM local time. Voice calls for renewal are restricted to 9 AM - 7 PM. Weekend calls require prior customer consent. Maximum 3 outbound contacts per renewal cycle per channel. Exceeding this triggers mandatory Do Not Disturb registration.", "metadata": {"regulator": "IRDAI", "year": 2024, "category": "contact_frequency"}},
    {"id": "reg_009", "text": "IRDAI Anti-Misselling Guidelines: AI systems must not promise guaranteed returns on ULIP products. ULIP illustrations must show 4% and 8% scenarios only. Claims about 'best returns' or 'market-beating performance' are prohibited. All performance references must include standard disclaimer: 'Past performance is not indicative of future returns.'", "metadata": {"regulator": "IRDAI", "year": 2023, "category": "ulip_misselling"}},
    {"id": "reg_010", "text": "IRDAI Senior Citizen Protection: For policyholders above 60 years, all automated communications must be available in their preferred regional language. Font sizes in digital communications must meet accessibility standards. If a senior citizen requests human agent, response time SLA is 1 hour (Priority 0).", "metadata": {"regulator": "IRDAI", "year": 2024, "category": "senior_protection"}},
]


def populate_rag():
    print("🔧 Initializing Chroma collections...")
    init_chroma()
    
    print("📚 Pushing policy documents...")
    add_documents(
        "policy_documents",
        documents=[d["text"] for d in POLICY_DOCUMENTS],
        metadatas=[d["metadata"] for d in POLICY_DOCUMENTS],
        ids=[d["id"] for d in POLICY_DOCUMENTS]
    )
    print(f"   ✅ {len(POLICY_DOCUMENTS)} policy documents indexed")

    print("💬 Pushing objection library...")
    add_documents(
        "objection_library",
        documents=[o["text"] for o in OBJECTIONS],
        metadatas=[o["metadata"] for o in OBJECTIONS],
        ids=[o["id"] for o in OBJECTIONS]
    )
    print(f"   ✅ {len(OBJECTIONS)} objection entries indexed")

    print("⚖️  Pushing regulatory guidelines...")
    add_documents(
        "regulatory_guidelines",
        documents=[r["text"] for r in REGULATIONS],
        metadatas=[r["metadata"] for r in REGULATIONS],
        ids=[r["id"] for r in REGULATIONS]
    )
    print(f"   ✅ {len(REGULATIONS)} regulatory guidelines indexed")
    
    print("\n✅ RAG population complete!")
    print("   Collections: objection_library, policy_documents, regulatory_guidelines")
    print("   Embedding model: text-embedding-004")


if __name__ == "__main__":
    populate_rag()
