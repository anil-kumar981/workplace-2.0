import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import engine, Base, async_session
from app.models.users import User
from app.models.roles import Role
from app.models.permissions import Permission
from app.shared.utils.security import hash_password

__all__ = ["AsyncSession"]
# 1. Translate TypeScript permission seed data
# Systematically define resources and their standard CRUD + Manage permissions
RESOURCES = [
    "User", "Project", "ProjectAssignedUser", "Attendance", "Leave", 
    "HolidayMaster", "WeekendConfig", "HolidayCalendar", "Announcement", 
    "JobOpening", "Applicant", "Role", "Permission", "Lead", "Comment", 
    "Task", "TaskActivityHistory", "TaskAssignmentHistory", "Employee"
]
ACTIONS = ["manage", "create", "update", "view", "delete"]
SCOPES = ["any", "own"]

INITIAL_PERMISSIONS = []
# Generate systematic permissions for all resources
for r in RESOURCES:
    for a in ACTIONS:
        for s in SCOPES:
            INITIAL_PERMISSIONS.append({
                "resource": r,
                "action": a,
                "scope": s
            })

# Add legacy or custom actions to ensure backward compatibility
INITIAL_PERMISSIONS.extend([
    {"resource": "User", "action": "ManageStaff", "scope": "any"},
    {"resource": "User", "action": "ResetPassword", "scope": "own"},
    {"resource": "Project", "action": "assign", "scope": "any"},
    {"resource": "Project", "action": "revoke", "scope": "any"},
    {"resource": "Attendance", "action": "checkout", "scope": "own"},
    {"resource": "Leave", "action": "approve", "scope": "any"},
    {"resource": "Leave", "action": "request", "scope": "own"},
])


# 2. Roles configurations
INITIAL_ROLES = {
    "admin": {
        "permissions": ["*:*:any"]  # Gets all database permissions dynamically
    },
    "hr": {
        "permissions": [
            "Project:view:any",
            "User:ManageStaff:any",
            "User:view:any",
            "Role:view:any",
            "Permission:view:any",
            "Leave:manage:any",
            "HolidayMaster:manage:any",
            "HolidayMaster:view:any",
            "JobOpening:manage:any",
            "Applicant:manage:any",
            "ProjectAssignedUser:manage:any",
            "HolidayCalendar:manage:any",
            "Employee:manage:any",
            "Employee:view:any",
            "Employee:view:own",
            "User:ResetPassword:own",
            "Announcement:manage:any",
            "Attendance:create:own",
            "Attendance:checkout:own",
            "Attendance:view:own",
            "Attendance:manage:any",
            "WeekendConfig:manage:any",
            "Comment:manage:any",
        ]
    },
    "manager": {
        "permissions": [
            "User:view:any",
            "Project:view:any",
            "Project:create:any",
            "Project:update:any",
            "Project:delete:any",
            "Project:manage:own",
            "Attendance:create:own",
            "Attendance:checkout:own",
            "Leave:request:own",
            "Leave:view:own",
            "Attendance:view:own",
            "Lead:view:own",
            "ProjectAssignedUser:manage:any",
            "TaskAssignmentHistory:manage:any",
            "User:ResetPassword:own",
            "HolidayCalendar:view:any",
            "Comment:manage:any",
        ]
    },
    "project_manager": {
        "permissions": [
            "Project:view:any",
            "Task:create:any",
            "Task:view:any",
            "Task:update:any",
            "Task:manage:own",
            "TaskActivityHistory:view:any",
            "TaskActivityHistory:create:any",
            "TaskAssignmentHistory:manage:any",
            "TaskAssignmentHistory:view:any",
            "TaskAssignmentHistory:create:any",
            "Employee:view:own",
            "User:ResetPassword:own",
            "Attendance:create:own",
            "Attendance:checkout:own",
            "Attendance:view:own",
            "HolidayCalendar:view:any",
            "Comment:manage:any",
        ]
    },
    "team_leader": {
        "permissions": [
            "Task:create:any",
            "Task:view:any",
            "Task:update:any",
            "TaskActivityHistory:view:any",
            "TaskActivityHistory:create:any",
            "TaskAssignmentHistory:view:any",
            "Employee:view:own",
            "User:ResetPassword:own",
            "Attendance:create:own",
            "Attendance:checkout:own",
            "Attendance:view:own",
            "HolidayCalendar:view:any",
            "Comment:manage:own",
        ]
    },
    "employee": {
        "permissions": [
            "User:view:own",
            "Attendance:create:own",
            "Attendance:checkout:own",
            "Attendance:view:own",
            "Leave:request:own",
            "Leave:view:own",
            "Project:view:own",
            "Lead:view:own",
            "ProjectAssignedUser:view:own",
            "Task:view:own",
            "Task:create:own",
            "Task:update:own",
            "TaskActivityHistory:create:any",
            "TaskActivityHistory:view:own",
            "Employee:view:own",
            "User:ResetPassword:own",
            "HolidayCalendar:view:any",
            "Comment:manage:own",
        ]
    },
    "intern": {
        "permissions": ["User:view:own"]  # Plus employee defaults
    },
    "contractor": {
        "permissions": ["User:view:own"]  # Plus employee defaults
    },
}

# 3. Superadmin Initial Details
SUPERADMIN_DATA = {
    "name": "Anil",
    "email": "anilkumar.dcttechnology@gmail.com",
    "password": "Admin@123",
}


async def seed_database():
    print("--------------------------------------------------")
    print("[START] STARTING BACKEND DATABASE SEED RUNNER...")
    print("--------------------------------------------------")

    # Step A: Reset database tables for a clean seed environment
    print("[STEP A] Resetting database tables for a clean seed environment...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("[SUCCESS] Database tables recreated successfully.")

    async with async_session() as db:
        # Step B: Seed Permissions
        print("\n[STEP B] Seeding permissions...")
        db_permissions = {}
        for p in INITIAL_PERMISSIONS:
            stmt = select(Permission).where(
                Permission.resource == p["resource"],
                Permission.action == p["action"],
                Permission.scope == p["scope"],
            )
            res = await db.execute(stmt)
            existing_p = res.scalars().first()

            if not existing_p:
                new_p = Permission(
                    resource=p["resource"], action=p["action"], scope=p["scope"]
                )
                db.add(new_p)
                await db.flush()  # Populate the ID
                existing_p = new_p
                print(
                    f"   [+] Seeded permission: {p['resource']}:{p['action']}:{p['scope']}"
                )

            key = f"{p['resource']}:{p['action']}:{p['scope']}"
            db_permissions[key] = existing_p

        # Step C: Seed Roles & Link Permissions
        print("\n[STEP C] Seeding roles and mapping permissions...")
        all_perms = list(db_permissions.values())

        db_roles = {}
        for role_name, data in INITIAL_ROLES.items():
            from sqlalchemy.orm import selectinload

            stmt = (
                select(Role)
                .where(Role.name == role_name)
                .options(selectinload(Role.permissions))
            )
            res = await db.execute(stmt)
            existing_role = res.scalars().first()

            if not existing_role:
                existing_role = Role(name=role_name)
                db.add(existing_role)
                print(f"   [+] Created role: {role_name}")

            db_roles[role_name] = existing_role

            # Setup permissions association
            current_perms = existing_role.permissions

            if role_name == "admin":
                # Admin gets ALL database permissions
                for perm in all_perms:
                    if perm not in current_perms:
                        existing_role.permissions.append(perm)
            else:
                # Map specific permissions
                for perm_key in data["permissions"]:
                    if perm_key in db_permissions:
                        target_perm = db_permissions[perm_key]
                        if target_perm not in current_perms:
                            existing_role.permissions.append(target_perm)
                    else:
                        # Fallback parsing in case of direct mappings
                        try:
                            res_name, act_name, scp_name = perm_key.split(":")
                            # Try to look it up from seeded list
                            key = f"{res_name}:{act_name}:{scp_name}"
                            if key in db_permissions:
                                target_perm = db_permissions[key]
                                if target_perm not in current_perms:
                                    existing_role.permissions.append(target_perm)
                        except ValueError:
                            pass

        await db.flush()
        print("[SUCCESS] Roles seeded and permissions mapped successfully.")

        # Step D: Seed Superadmin account
        print("\n[STEP D] Seeding Superadmin account...")
        admin_role = db_roles.get("admin")
        if not admin_role:
            print("[ERROR] Critical Failure: Admin role was not found in DB!")
            return

        stmt = select(User).where(User.email == SUPERADMIN_DATA["email"])
        res = await db.execute(stmt)
        existing_admin = res.scalars().first()

        if not existing_admin:
            hashed_pw = hash_password(SUPERADMIN_DATA["password"])
            new_admin = User(
                email=SUPERADMIN_DATA["email"],
                username=SUPERADMIN_DATA["name"],
                hashed_password=hashed_pw,
                role_id=admin_role.id,
                is_active=True,
                is_verified=True,
            )
            db.add(new_admin)
            print(f"   [+] Seeded Superadmin account: {SUPERADMIN_DATA['email']}")
        else:
            # Enforce that existing account has admin role mapping
            existing_admin.role_id = admin_role.id
            print(
                f"   [*] Superadmin account already exists: {SUPERADMIN_DATA['email']}"
            )

        # Commit all operations
        await db.commit()
        print("\n[SUCCESS] All database seed transactions committed successfully!")
        print("--------------------------------------------------")
        print("[FINISHED] SEEDING COMPLETED SUCCESSFULLY!")
        print("--------------------------------------------------")


if __name__ == "__main__":
    # Bootstrap async execution context
    asyncio.run(seed_database())
