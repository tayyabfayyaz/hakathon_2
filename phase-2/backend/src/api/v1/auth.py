from fastapi import APIRouter, HTTPException, status, Response
from pydantic import BaseModel

from src.api.deps import DbSession, CurrentUser
from src.models.user import UserCreate, UserLogin, UserRead
from src.services.user_service import create_user, get_user_by_email, authenticate_user
from src.core.security import create_access_token
from src.core.config import get_settings

router = APIRouter(prefix="/auth", tags=["Authentication"])
settings = get_settings()


class AuthResponse(BaseModel):
    user: UserRead
    message: str


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    session: DbSession,
    response: Response,
):
    """Register a new user."""
    # Check if email already exists
    existing_user = await get_user_by_email(session, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error_code": "EMAIL_EXISTS",
                "message": "Email already registered",
            },
        )

    # Create user
    user = await create_user(session, user_data)

    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})

    # Set cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax",
        max_age=settings.jwt_expire_minutes * 60,
    )

    return AuthResponse(
        user=UserRead.model_validate(user),
        message="Registration successful",
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    credentials: UserLogin,
    session: DbSession,
    response: Response,
):
    """Login with email and password."""
    user = await authenticate_user(session, credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error_code": "INVALID_CREDENTIALS",
                "message": "Invalid email or password",
            },
        )

    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})

    # Set cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax",
        max_age=settings.jwt_expire_minutes * 60,
    )

    return AuthResponse(
        user=UserRead.model_validate(user),
        message="Login successful",
    )


@router.post("/logout")
async def logout(response: Response):
    """Logout the current user."""
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax",
    )
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserRead)
async def get_current_user_info(current_user: CurrentUser):
    """Get the current authenticated user's information."""
    return UserRead.model_validate(current_user)
