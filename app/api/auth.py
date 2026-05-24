from app.shared.utils.check_permissions import PermissionChecker
from fastapi import APIRouter, Depends, status
from app.schema import UserCreate
from app.schema.auth import OtpRequest, OtpVerify, LoginRequest, ForgotPasswordRequest
from app.services.auth_service import AuthService
from app.dependencies.auth_dependencies import get_auth_service, get_current_user
from app.shared.api_response.api_response import ApiResponse
from app.shared.utils.jwt_helper import generate_jwt_token
from app.core import config
from app.models.users import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", status_code=status.HTTP_201_CREATED, dependencies=[Depends(PermissionChecker("User", "ManageStaff"))])
async def register(
    user_in: UserCreate,
    service: AuthService = Depends(get_auth_service)
):
    """
    Registers a new user account.
    """
    new_user = await service.register_user(user_in)
    return ApiResponse.success(
        data=new_user,
        message="User registered successfully.",
        code=status.HTTP_201_CREATED
    )

@router.post("/otp-request", status_code=status.HTTP_200_OK)
async def request_otp(
    otp_in: OtpRequest,
    service: AuthService = Depends(get_auth_service)
):
    """
    Requests a 6-digit verification OTP code sent to the user's email.
    The OTP type must be either 'login' or 'forgot_password'.
    """
    await service.request_otp(otp_in)
    return ApiResponse.success(
        message=f"A verification code has been sent successfully to {otp_in.email}."
    )

@router.post("/otp-verify", status_code=status.HTTP_200_OK)
async def verify_otp(
    verify_in: OtpVerify,
    service: AuthService = Depends(get_auth_service)
):
    """
    Verifies a user-submitted OTP code.
    If valid, unlocks the login or forgot_password actions for the next 10 minutes.
    """
    await service.verify_otp(verify_in)
    return ApiResponse.success(
        message="Verification code matched successfully. You can now proceed."
    )

@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    login_in: LoginRequest,
    service: AuthService = Depends(get_auth_service)
):
    """
    Logs in a user and returns their account details.
    Requires prior OTP verification of type 'login' for this email within the last 10 minutes.
    """
    user_data = await service.login_user(login_in)
    
    # 1. Generate secure JWT token
    token = generate_jwt_token(user_id=user_data.id, email=user_data.email)
    
    # 2. Formulate response payload including token and user
    response = ApiResponse.success(
        data={
            "user": user_data,
            "access_token": token
        },
        message="Login successful."
    )
    
    # 3. Set secure HttpOnly cookie
    response.set_cookie(
        key=config.COOKIE_NAME,
        value=token,
        max_age=config.COOKIE_MAX_AGE,
        httponly=True,
        secure=config.COOKIE_SECURE,
        samesite=config.COOKIE_SAMESITE.lower() if config.COOKIE_SAMESITE else "lax",
    )
    
    return response

@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    reset_in: ForgotPasswordRequest,
    service: AuthService = Depends(get_auth_service)
):
    """
    Resets the user's password.
    Requires prior OTP verification of type 'forgot_password' for this email within the last 10 minutes.
    New password cannot match the current active password.
    """
    await service.reset_password(reset_in)
    return ApiResponse.success(
        message="Password has been updated successfully."
    )

@router.get("/me", status_code=status.HTTP_200_OK)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves the profile details of the currently logged-in user using JWT or Cookie auth.
    """
    return ApiResponse.success(
        data=current_user,
        message="User profile retrieved successfully."
    )
