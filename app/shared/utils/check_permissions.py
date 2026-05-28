from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.dependencies.get_db import get_db
from app.dependencies.auth_dependencies import get_current_user
from app.models.users import User
from app.models.permissions import Permission
from app.models.role_permission import role_permissions
from app.shared.exceptions import AppException

class PermissionChecker:
    """
    A parameterized dependency guard to check if a user's role has the
    required permission (defined by resource and action).
    
    It dynamically evaluates the user's permission scope from the database:
    1. "any": Allows manipulating any record of the resource.
    2. "own": Restricts access to only the user's own data by verifying path/query/body ownership.
    """
    def __init__(self, resource: str, action: str):
        self.resource = resource
        self.action = action

    async def __call__(
        self,
        request: Request,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        """
        Enforces granular role-based resource permissions and resource ownership.
        """
        # If the user has no role assigned, deny access immediately
        if not current_user.role_id:
            raise AppException("Access denied. You have no role assigned to your account.", 403)

        # A role having the wildcard "manage" action has rights to any lower action
        allowed_actions = [self.action, "manage"]

        # 1. Check if the user's role has broad 'any' scope permission
        any_stmt = (
            select(Permission)
            .join(role_permissions, role_permissions.c.permission_id == Permission.id)
            .where(
                role_permissions.c.role_id == current_user.role_id,
                Permission.resource == self.resource,
                Permission.action.in_(allowed_actions),
                Permission.scope == "any"
            )
        )
        any_result = await db.execute(any_stmt)
        has_any_permission = any_result.scalars().first()

        if has_any_permission:
            # Broad permission exists: grant access to any record immediately
            return current_user

        # 2. Check if the user's role has restricted 'own' scope permission
        own_stmt = (
            select(Permission)
            .join(role_permissions, role_permissions.c.permission_id == Permission.id)
            .where(
                role_permissions.c.role_id == current_user.role_id,
                Permission.resource == self.resource,
                Permission.action.in_(allowed_actions),
                Permission.scope == "own"
            )
        )
        own_result = await db.execute(own_stmt)
        has_own_permission = own_result.scalars().first()

        if has_own_permission:
            # Restricted permission exists: enforce object-level ownership checks
            found_identifier = False

            # Check Path Parameters for User ID keys
            id_keys = {"user_id", "id", "userId", "employee_id", "employeeId"}
            for key in id_keys:
                path_val = request.path_params.get(key)
                if path_val is not None:
                    found_identifier = True
                    try:
                        if int(path_val) != current_user.id:
                            raise AppException("Access denied. You only have permission to access your own data.", 403)
                    except ValueError:
                        raise AppException(f"Invalid identifier '{path_val}' in request path parameters.", 400)

            # Check Query Parameters for User ID keys or email
            for key in id_keys:
                query_val = request.query_params.get(key)
                if query_val is not None:
                    found_identifier = True
                    try:
                        if int(query_val) != current_user.id:
                            raise AppException("Access denied. You only have permission to access your own data.", 403)
                    except ValueError:
                        raise AppException(f"Invalid identifier '{query_val}' in query parameters.", 400)

            query_email = request.query_params.get("email")
            if query_email is not None:
                found_identifier = True
                if str(query_email).strip().lower() != current_user.email.strip().lower():
                    raise AppException("Access denied. You only have permission to access your own data.", 403)

            # Check JSON Request Body (if request content-type is json)
            if request.headers.get("content-type") == "application/json":
                try:
                    # request.json() caches the parsed body internally, making it safe for downstream FastAPI routing
                    body_json = await request.json()
                    if isinstance(body_json, dict):
                        # check id keys
                        body_id_keys = {"user_id", "id", "userId", "employee_id", "employeeId", "created_by", "createdBy"}
                        for key in body_id_keys:
                            body_val = body_json.get(key)
                            if body_val is not None:
                                found_identifier = True
                                try:
                                    if int(body_val) != current_user.id:
                                        raise AppException("Access denied. You only have permission to access your own data.", 403)
                                except ValueError:
                                    raise AppException(f"Invalid identifier '{body_val}' in request body.", 400)
                        
                        # check email keys
                        body_email = body_json.get("email")
                        if body_email is not None:
                            found_identifier = True
                            if str(body_email).strip().lower() != current_user.email.strip().lower():
                                raise AppException("Access denied. You only have permission to access your own data.", 403)
                except Exception:
                    pass

            # If no identifier was found to tie this request to the caller
            if not found_identifier:
                # Under "own" scope, they are not allowed to query generic collections or other resources
                raise AppException(
                    f"Access denied. You only have permission to perform '{self.action}' on your own data, but no matching identifier was found in the request.",
                    403
                )

            return current_user

        # 3. Neither 'any' nor 'own' permission exists for this role
        raise AppException(
            f"Access denied. You do not have permission to perform '{self.action}' on '{self.resource}'.",
            403
        )
