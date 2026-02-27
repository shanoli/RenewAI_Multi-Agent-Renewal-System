"""
Dashboard API — metrics, escalations, audit logs.
"""
from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.core.config import get_settings
import aiosqlite

settings = get_settings()
router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/overview", summary="Get renewal operations overview")
async def get_overview(current_user: str = Depends(get_current_user)):
    async with aiosqlite.connect(settings.sqlite_db_path) as db:
        db.row_factory = aiosqlite.Row
        
        total = await (await db.execute("SELECT COUNT(*) as c FROM policies")).fetchone()
        active = await (await db.execute("SELECT COUNT(*) as c FROM policies WHERE status='ACTIVE'")).fetchone()
        ai_mode = await (await db.execute("SELECT COUNT(*) as c FROM policy_state WHERE mode='AI'")).fetchone()
        human_mode = await (await db.execute("SELECT COUNT(*) as c FROM policy_state WHERE mode='HUMAN_CONTROL'")).fetchone()
        distress = await (await db.execute("SELECT COUNT(*) as c FROM policy_state WHERE distress_flag=1")).fetchone()
        open_esc = await (await db.execute("SELECT COUNT(*) as c FROM escalation_cases WHERE status='OPEN'")).fetchone()
        
        channel_dist = await (await db.execute("""
            SELECT last_channel, COUNT(*) as count FROM policy_state 
            WHERE last_channel IS NOT NULL GROUP BY last_channel
        """)).fetchall()
        
        recent_actions = await (await db.execute("""
            SELECT action_type, COUNT(*) as count FROM audit_logs 
            WHERE created_at >= datetime('now', '-24 hours') GROUP BY action_type
        """)).fetchall()
    
    return {
        "total_policies": total["c"],
        "active_policies": active["c"],
        "ai_managed": ai_mode["c"],
        "human_managed": human_mode["c"],
        "distress_cases": distress["c"],
        "open_escalations": open_esc["c"],
        "channel_distribution": [dict(r) for r in channel_dist],
        "last_24h_actions": [dict(r) for r in recent_actions]
    }


@router.get("/escalations", summary="List all open escalation cases")
async def get_escalations(
    status: str = "OPEN",
    current_user: str = Depends(get_current_user)
):
    async with aiosqlite.connect(settings.sqlite_db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT ec.*, c.name as customer_name, p.policy_type, p.annual_premium
            FROM escalation_cases ec
            JOIN policies p ON ec.policy_id = p.policy_id
            JOIN customers c ON p.customer_id = c.customer_id
            WHERE ec.status = ?
            ORDER BY ec.priority_score DESC, ec.created_at ASC
        """, (status,))
        cases = await cursor.fetchall()
    return {"escalations": [dict(c) for c in cases], "count": len(cases)}


@router.patch("/escalations/{case_id}/resolve", summary="Resolve an escalation case")
async def resolve_escalation(
    case_id: int,
    current_user: str = Depends(get_current_user)
):
    async with aiosqlite.connect(settings.sqlite_db_path) as db:
        await db.execute(
            "UPDATE escalation_cases SET status='RESOLVED' WHERE case_id=?", (case_id,)
        )
        # Fetch policy_id to reset mode
        cursor = await db.execute("SELECT policy_id FROM escalation_cases WHERE case_id=?", (case_id,))
        row = await cursor.fetchone()
        if row:
            await db.execute(
                "UPDATE policy_state SET mode='AI', distress_flag=0, current_node='ORCHESTRATOR' WHERE policy_id=?",
                (row[0],)
            )
        await db.commit()
    return {"message": f"Case {case_id} resolved", "status": "RESOLVED"}


@router.get("/audit-logs/{policy_id}", summary="Get IRDAI-ready audit trail for a policy")
async def get_audit_logs(
    policy_id: str,
    current_user: str = Depends(get_current_user)
):
    async with aiosqlite.connect(settings.sqlite_db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM audit_logs WHERE policy_id=? ORDER BY created_at DESC",
            (policy_id,)
        )
        logs = await cursor.fetchall()
    return {"policy_id": policy_id, "audit_logs": [dict(l) for l in logs], "count": len(logs)}


@router.get("/customers", summary="List all customers with policy summary")
async def list_customers(
    segment: str = None,
    current_user: str = Depends(get_current_user)
):
    async with aiosqlite.connect(settings.sqlite_db_path) as db:
        db.row_factory = aiosqlite.Row
        if segment:
            cursor = await db.execute("""
                SELECT c.*, COUNT(p.policy_id) as policy_count 
                FROM customers c LEFT JOIN policies p ON c.customer_id=p.customer_id
                WHERE c.segment=? GROUP BY c.customer_id
            """, (segment,))
        else:
            cursor = await db.execute("""
                SELECT c.*, COUNT(p.policy_id) as policy_count 
                FROM customers c LEFT JOIN policies p ON c.customer_id=p.customer_id
                GROUP BY c.customer_id
            """)
        customers = await cursor.fetchall()
    return {"customers": [dict(c) for c in customers], "count": len(customers)}
@router.get("/policies", summary="List all policies with customer names")
async def list_policies(current_user: str = Depends(get_current_user)):
    async with aiosqlite.connect(settings.sqlite_db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT p.*, c.name as customer_name, c.segment
            FROM policies p
            JOIN customers c ON p.customer_id = c.customer_id
            ORDER BY p.premium_due_date ASC
        """)
        policies = await cursor.fetchall()
    return {"policies": [dict(p) for p in policies], "count": len(policies)}
