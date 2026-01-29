"""User API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token, UserProfileUpdate
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.climate_zone_service import ClimateZoneService
from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user account.
    Automatically determines USDA climate zone from location.
    """
    repo = UserRepository(db)

    # Check if user already exists
    existing_user = repo.get_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash password
    hashed_password = AuthService.hash_password(user_data.password)

    # Determine USDA zone
    usda_zone = None
    if user_data.zip_code:
        usda_zone = ClimateZoneService.get_zone_from_zip(user_data.zip_code)
    elif user_data.latitude and user_data.longitude:
        usda_zone = ClimateZoneService.get_zone_from_coordinates(
            user_data.latitude, user_data.longitude
        )

    # Create user
    user = repo.create(
        email=user_data.email,
        hashed_password=hashed_password,
        zip_code=user_data.zip_code,
        latitude=user_data.latitude,
        longitude=user_data.longitude,
        usda_zone=usda_zone
    )

    return user


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT token.
    """
    user = AuthService.authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = AuthService.create_access_token(user.id, user.email)

    return Token(access_token=access_token)


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user information.
    """
    return current_user


@router.patch("/me", response_model=UserResponse)
def update_user_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile information.
    """
    repo = UserRepository(db)

    # Update only provided fields
    update_data = profile_data.model_dump(exclude_unset=True)
    user = repo.update(current_user, **update_data)

    return user
