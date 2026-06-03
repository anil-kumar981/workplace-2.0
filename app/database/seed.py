import asyncio
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import config
from app.database import Base, async_session, engine
from app.models.permissions import Permission
from app.models.roles import Role
from app.models.users import User
from app.shared.utils.security import hash_password

__all__ = ["AsyncSession"]

# 1. Seed data: permissions, roles, and initial admin account.

INITIAL_PERMISSIONS = [
    # User Management
    {
        "key": "User:ManageStaff:any",
        "resource": "User",
        "action": "ManageStaff",
        "scope": "any",
        "description": "Manage users (Create/Edit/Delete)",
    },
    {
        "key": "User:view:any",
        "resource": "User",
        "action": "view",
        "scope": "any",
        "description": "View any user",
    },
    {
        "key": "User:view:own",
        "resource": "User",
        "action": "view",
        "scope": "own",
        "description": "View own user",
    },
    {
        "key": "User:ResetPassword:own",
        "resource": "User",
        "action": "ResetPassword",
        "scope": "own",
        "description": "Reset own password",
    },
    # Project Management
    {
        "key": "Project:view:any",
        "resource": "Project",
        "action": "view",
        "scope": "any",
        "description": "View any project",
    },
    {
        "key": "Project:assign:any",
        "resource": "Project",
        "action": "assign",
        "scope": "any",
        "description": "Assign project to anyone",
    },
    {
        "key": "Project:revoke:any",
        "resource": "Project",
        "action": "revoke",
        "scope": "any",
        "description": "Revoke project from anyone",
    },
    {
        "key": "Project:manage:any",
        "resource": "Project",
        "action": "manage",
        "scope": "any",
        "description": "Manage projects (Create/Edit/Delete)",
    },
    {
        "key": "Project:view:own",
        "resource": "Project",
        "action": "view",
        "scope": "own",
        "description": "View assigned projects",
    },
    {
        "key": "Project:create:any",
        "resource": "Project",
        "action": "create",
        "scope": "any",
        "description": "Create new project",
    },
    {
        "key": "Project:update:any",
        "resource": "Project",
        "action": "update",
        "scope": "any",
        "description": "Update project details",
    },
    {
        "key": "Project:delete:any",
        "resource": "Project",
        "action": "delete",
        "scope": "any",
        "description": "Delete project",
    },
    {
        "key": "Project:manage:own",
        "resource": "Project",
        "action": "manage",
        "scope": "own",
        "description": "Manage assigned projects",
    },
    # Project Assignments
    {
        "key": "ProjectAssignedUser:manage:any",
        "resource": "ProjectAssignedUser",
        "action": "manage",
        "scope": "any",
        "description": "Manage project assignments (Create/Update/Delete/View)",
    },
    {
        "key": "ProjectAssignedUser:view:own",
        "resource": "ProjectAssignedUser",
        "action": "view",
        "scope": "own",
        "description": "View own project assignments",
    },
    # Attendance & Leaves
    {
        "key": "Attendance:manage:any",
        "resource": "Attendance",
        "action": "manage",
        "scope": "any",
        "description": "Manage attendance create update delete view",
    },
    {
        "key": "Attendance:create:own",
        "resource": "Attendance",
        "action": "create",
        "scope": "own",
        "description": "Check-in",
    },
    {
        "key": "Attendance:checkout:own",
        "resource": "Attendance",
        "action": "checkout",
        "scope": "own",
        "description": "Check-out",
    },
    {
        "key": "Attendance:view:own",
        "resource": "Attendance",
        "action": "view",
        "scope": "own",
        "description": "View own attendance",
    },
    {
        "key": "Leave:approve:any",
        "resource": "Leave",
        "action": "approve",
        "scope": "any",
        "description": "Approve any leave",
    },
    {
        "key": "Leave:request:own",
        "resource": "Leave",
        "action": "request",
        "scope": "own",
        "description": "Request leave",
    },
    {
        "key": "Leave:view:own",
        "resource": "Leave",
        "action": "view",
        "scope": "own",
        "description": "View own leaves",
    },
    {
        "key": "Leave:manage:any",
        "resource": "Leave",
        "action": "manage",
        "scope": "any",
        "description": "Manage leave policies",
    },
    # Holiday Master
    {
        "key": "HolidayMaster:manage:any",
        "resource": "HolidayMaster",
        "action": "manage",
        "scope": "any",
        "description": "Manage holiday master",
    },
    {
        "key": "HolidayMaster:view:any",
        "resource": "HolidayMaster",
        "action": "view",
        "scope": "any",
        "description": "View holiday master",
    },
    # Weekend Config
    {
        "key": "WeekendConfig:manage:any",
        "resource": "WeekendConfig",
        "action": "manage",
        "scope": "any",
        "description": "Manage weekend config",
    },
    {
        "key": "WeekendConfig:create:any",
        "resource": "WeekendConfig",
        "action": "create",
        "scope": "any",
        "description": "Create weekend config",
    },
    # Holiday Calendar
    {
        "key": "HolidayCalendar:manage:any",
        "resource": "HolidayCalendar",
        "action": "manage",
        "scope": "any",
        "description": "Manage holiday calendar(create, update, view)",
    },
    {
        "key": "HolidayCalendar:create:any",
        "resource": "HolidayCalendar",
        "action": "create",
        "scope": "any",
        "description": "Create holiday calendar",
    },
    {
        "key": "HolidayCalendar:update:any",
        "resource": "HolidayCalendar",
        "action": "update",
        "scope": "any",
        "description": "Update holiday calendar",
    },
    {
        "key": "HolidayCalendar:view:any",
        "resource": "HolidayCalendar",
        "action": "view",
        "scope": "any",
        "description": "View holiday calendar",
    },
    # Announcements
    {
        "key": "Announcement:manage:any",
        "resource": "Announcement",
        "action": "manage",
        "scope": "any",
        "description": "Manage announcements (Create/Edit/Delete)",
    },
    {
        "key": "Announcement:view:any",
        "resource": "Announcement",
        "action": "view",
        "scope": "any",
        "description": "View announcements",
    },
    # Recruitment
    {
        "key": "JobOpening:manage:any",
        "resource": "JobOpening",
        "action": "manage",
        "scope": "any",
        "description": "Manage job openings",
    },
    {
        "key": "Applicant:manage:any",
        "resource": "Applicant",
        "action": "manage",
        "scope": "any",
        "description": "Manage applicants",
    },
    # Role & Permission Management
    {
        "key": "Role:view:any",
        "resource": "Role",
        "action": "view",
        "scope": "any",
        "description": "View any role",
    },
    {
        "key": "Role:manage:any",
        "resource": "Role",
        "action": "manage",
        "scope": "any",
        "description": "Manage roles",
    },
    {
        "key": "Permission:view:any",
        "resource": "Permission",
        "action": "view",
        "scope": "any",
        "description": "View any permission",
    },
    {
        "key": "Permission:manage:any",
        "resource": "Permission",
        "action": "manage",
        "scope": "any",
        "description": "Manage permissions",
    },
    # Leads & Comments
    {
        "key": "Lead:view:any",
        "resource": "Lead",
        "action": "view",
        "scope": "any",
        "description": "View any lead",
    },
    {
        "key": "Lead:view:own",
        "resource": "Lead",
        "action": "view",
        "scope": "own",
        "description": "View assigned leads",
    },
    {
        "key": "Lead:manage:any",
        "resource": "Lead",
        "action": "manage",
        "scope": "any",
        "description": "Manage leads",
    },
    {
        "key": "Comment:manage:own",
        "resource": "Comment",
        "action": "manage",
        "scope": "own",
        "description": "Manage comments",
    },
    {
        "key": "Comment:manage:any",
        "resource": "Comment",
        "action": "manage",
        "scope": "any",
        "description": "Manage comments",
    },
    # Task Management
    {
        "key": "Task:manage:any",
        "resource": "Task",
        "action": "manage",
        "scope": "any",
        "description": "Manage any task",
    },
    {
        "key": "Task:view:any",
        "resource": "Task",
        "action": "view",
        "scope": "any",
        "description": "View any task",
    },
    {
        "key": "Task:manage:own",
        "resource": "Task",
        "action": "manage",
        "scope": "own",
        "description": "Manage tasks assigned by/to me",
    },
    {
        "key": "Task:view:own",
        "resource": "Task",
        "action": "view",
        "scope": "own",
        "description": "View tasks assigned to/by me",
    },
    {
        "key": "Task:update:own",
        "resource": "Task",
        "action": "update",
        "scope": "own",
        "description": "Update tasks assigned to me",
    },
    {
        "key": "Task:create:any",
        "resource": "Task",
        "action": "create",
        "scope": "any",
        "description": "Create any task",
    },
    {
        "key": "Task:create:own",
        "resource": "Task",
        "action": "create",
        "scope": "own",
        "description": "Create task for self",
    },
    {
        "key": "Task:update:any",
        "resource": "Task",
        "action": "update",
        "scope": "any",
        "description": "Update any task",
    },
    # Task Activity History
    {
        "key": "TaskActivityHistory:view:any",
        "resource": "TaskActivityHistory",
        "action": "view",
        "scope": "any",
        "description": "View any task activity history",
    },
    {
        "key": "TaskActivityHistory:create:any",
        "resource": "TaskActivityHistory",
        "action": "create",
        "scope": "any",
        "description": "Create task activity history",
    },
    {
        "key": "TaskActivityHistory:view:own",
        "resource": "TaskActivityHistory",
        "action": "view",
        "scope": "own",
        "description": "View own task activity history",
    },
    # Task Assignment History
    {
        "key": "TaskAssignmentHistory:view:any",
        "resource": "TaskAssignmentHistory",
        "action": "view",
        "scope": "any",
        "description": "View any task assignment history",
    },
    {
        "key": "TaskAssignmentHistory:create:any",
        "resource": "TaskAssignmentHistory",
        "action": "create",
        "scope": "any",
        "description": "Create task assignment history",
    },
    {
        "key": "TaskAssignmentHistory:manage:any",
        "resource": "TaskAssignmentHistory",
        "action": "manage",
        "scope": "any",
        "description": "Manage task assignment history",
    },
    # Employee
    {
        "key": "Employee:view:any",
        "resource": "Employee",
        "action": "view",
        "scope": "any",
        "description": "View any employee",
    },
    {
        "key": "Employee:view:own",
        "resource": "Employee",
        "action": "view",
        "scope": "own",
        "description": "View own employee",
    },
    {
        "key": "Employee:manage:any",
        "resource": "Employee",
        "action": "manage",
        "scope": "any",
        "description": "Manage any employee",
    },
    # Applicants
    {
        "key": "Applicant:manage:any",
        "resource": "Applicant",
        "action": "manage",
        "scope": "any",
        "description": "Manage any applicant",
    },
]

INITIAL_ROLES = {
    "admin": {
        "description": "System Administrator with full access",
        "isSystem": True,
        "permissions": ["*:*:any"],  # Wildcard covers everything
        "inherits": None,
        "level": 0,
    },
    # Common and act as parent role, purpose if we create a role and that role inherit this employee so he will assign all the permissions of this role.
    # Example: If We create a role(Developer or Tester) and if he inherit employee(as he this role points like he is employee) so we don't need to assign all the permissions to Developer or Tester role, we just need to inherit this employee role to Developer or Tester role.
    "employee": {
        "description": "Standard Employee role",
        "isSystem": True,
        "permissions": [
            "Attendance:checkout:own",
            "Attendance:create:own",
            "Attendance:view:own",
            "Comment:create:own",
            "Comment:manage:own",
            "Employee:view:own",
            "HolidayCalendar:view:any",
            "Lead:view:own",
            "Leave:request:own",
            "Leave:view:own",
            "Project:view:own",
            "ProjectAssignedUser:view:own",
            "Task:create:own",
            "Task:update:own",
            "Task:view:own",
            "TaskActivityHistory:create:any",
            "TaskActivityHistory:view:own",
            "User:ResetPassword:own",
            "User:view:own",
        ],
        "inherits": None,
        "level": 2,
    },
    "hr": {
        "description": "Human Resources role",
        "isSystem": True,
        "permissions": [
            "Announcement:manage:any",
            "Applicant:manage:any",
            "Attendance:manage:any",
            "Comment:manage:any",
            "Employee:manage:any",
            "Employee:view:any",
            "HolidayCalendar:manage:any",
            "HolidayMaster:manage:any",
            "HolidayMaster:view:any",
            "JobOpening:manage:any",
            "Leave:manage:any",
            "Permission:view:any",
            "Role:view:any",
            "User:ManageStaff:any",
            "User:view:any",
            "WeekendConfig:manage:any",
        ],
        "inherits": "employee",
        "level": 1,
    },
    "product_manager": {
        "description": "Team Manager role",
        "isSystem": True,
        "permissions": [
            "Project:manage:any",
            "ProjectAssignedUser:manage:any",
            "TaskAssignmentHistory:manage:any",
            "User:view:any",
        ],
        "inherits": "employee",
        "level": 1,
    },
    "intern": {
        "description": "Intern role",
        "isSystem": True,
        "permissions": [],  # Inherits from employee
        "inherits": "employee",
        "level": 3,
    },
    "contractor": {
        "description": "Contractor role",
        "isSystem": True,
        "permissions": [],  # Inherits from employee
        "inherits": "employee",
        "level": 3,
    },
}

# These will be used by the seed runner to build the Hierarchy and Roles in DB
ROLES = [
    {
        "name": name,
        "description": role["description"],
        "isSystem": role["isSystem"],
        "permissions": role["permissions"],
        "inherits": role["inherits"],
        "level": role["level"],
    }
    for name, role in INITIAL_ROLES.items()
]

SUPERADMIN = {
    "userId": config.ADMIN_ID,
    "name": config.ADMIN_NAME,
    "email": config.ADMIN_MAIL,
    "password": config.ADMIN_PASSWORD,
    "joinDate": datetime.now(),
}


def resolve_role_permissions(role_name: str, roles_dict: dict) -> set:
    """
    Recursively gather all permissions for a role including inherited permissions.
    """
    role_data = roles_dict[role_name]
    perms = set(role_data.get("permissions", []))
    parent = role_data.get("inherits")
    if parent and parent in roles_dict:
        perms.update(resolve_role_permissions(parent, roles_dict))
    return perms


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
        seeded_permissions = set()

        for p in INITIAL_PERMISSIONS:
            key = f"{p['resource']}:{p['action']}:{p['scope']}"
            if key in seeded_permissions:
                continue
            seeded_permissions.add(key)

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

            db_permissions[key] = existing_p

        # Resolve all permissions for all roles including inheritance
        resolved_roles_perms = {}
        for role_name in INITIAL_ROLES:
            resolved_roles_perms[role_name] = resolve_role_permissions(
                role_name, INITIAL_ROLES
            )

        # Pre-seed/query any extra referenced permissions to avoid lazy loading issues later
        for role_name, perm_keys in resolved_roles_perms.items():
            for perm_key in perm_keys:
                if perm_key == "*:*:any":
                    continue
                if perm_key not in db_permissions:
                    try:
                        res_name, act_name, scp_name = perm_key.split(":")
                        key = f"{res_name}:{act_name}:{scp_name}"
                        if key not in db_permissions:
                            stmt = select(Permission).where(
                                Permission.resource == res_name,
                                Permission.action == act_name,
                                Permission.scope == scp_name,
                            )
                            res = await db.execute(stmt)
                            existing_p = res.scalars().first()

                            if not existing_p:
                                existing_p = Permission(
                                    resource=res_name,
                                    action=act_name,
                                    scope=scp_name,
                                )
                                db.add(existing_p)
                                await db.flush()
                                print(
                                    f"   [+] Seeded missing referenced permission: {key}"
                                )

                            db_permissions[key] = existing_p
                    except ValueError:
                        pass

        # Step C: Seed Roles & Link Permissions
        print("\n[STEP C] Seeding roles and mapping permissions...")

        db_roles = {}
        for role_name in INITIAL_ROLES:
            from sqlalchemy.orm import selectinload

            stmt = (
                select(Role)
                .where(Role.name == role_name)
                .options(selectinload(Role.permissions))
            )
            res = await db.execute(stmt)
            existing_role = res.scalars().first()

            if not existing_role:
                existing_role = Role(name=role_name, permissions=[])
                db.add(existing_role)
                print(f"   [+] Created role: {role_name}")

            db_roles[role_name] = existing_role

            current_perms = existing_role.permissions
            role_perm_keys = resolved_roles_perms[role_name]

            if role_name == "admin" or "*:*:any" in role_perm_keys:
                # Admin gets ALL database permissions, mapped in final step
                continue

            for perm_key in role_perm_keys:
                if perm_key in db_permissions:
                    target_perm = db_permissions[perm_key]
                    if target_perm not in current_perms:
                        existing_role.permissions.append(target_perm)

        # Populate Admin role with ALL database permissions
        admin_role = db_roles.get("admin")
        if admin_role:
            all_perms = list(db_permissions.values())
            current_perms = admin_role.permissions
            for perm in all_perms:
                if perm not in current_perms:
                    admin_role.permissions.append(perm)
            print("   [+] Admin role populated with all database permissions.")

        await db.flush()
        print("[SUCCESS] Roles seeded and permissions mapped successfully.")

        # Step D: Seed Superadmin account
        print("\n[STEP D] Seeding Superadmin account...")
        admin_role = db_roles.get("admin")
        if not admin_role:
            print("[ERROR] Critical Failure: Admin role was not found in DB!")
            return

        stmt = select(User).where(User.email == SUPERADMIN["email"])
        res = await db.execute(stmt)
        existing_admin = res.scalars().first()

        if not existing_admin:
            hashed_pw = hash_password(SUPERADMIN["password"])
            new_admin = User(
                email=SUPERADMIN["email"],
                username=SUPERADMIN["name"],
                hashed_password=hashed_pw,
                role_id=admin_role.id,
                is_active=True,
                is_verified=True,
            )
            db.add(new_admin)
            print(f"   [+] Seeded Superadmin account: {SUPERADMIN['email']}")
        else:
            # Enforce that existing account has admin role mapping
            existing_admin.role_id = admin_role.id
            print(f"   [*] Superadmin account already exists: {SUPERADMIN['email']}")

        # Commit all operations
        await db.commit()
        print("\n[SUCCESS] All database seed transactions committed successfully!")
        print("--------------------------------------------------")
        print("[FINISHED] SEEDING COMPLETED SUCCESSFULLY!")
        print("--------------------------------------------------")


if __name__ == "__main__":
    # Bootstrap async execution context
    asyncio.run(seed_database())
