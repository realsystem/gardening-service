"""User API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token, UserProfileUpdate
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.climate_zone_service import ClimateZoneService
from app.services.location_service import LocationService
from app.api.dependencies import get_current_user
from app.models.user import User
from app.utils.feature_gating import get_feature_flags

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

    # Process ZIP code to determine unit system and coordinates
    unit_system, geocoded_lat, geocoded_lon = LocationService.process_user_zip_code(user_data.zip_code)

    # Use geocoded coordinates if available, otherwise use provided coordinates
    latitude = geocoded_lat if geocoded_lat is not None else user_data.latitude
    longitude = geocoded_lon if geocoded_lon is not None else user_data.longitude

    # Determine USDA zone
    usda_zone = None
    if user_data.zip_code:
        usda_zone = ClimateZoneService.get_zone_from_zip(user_data.zip_code)
    elif latitude and longitude:
        usda_zone = ClimateZoneService.get_zone_from_coordinates(latitude, longitude)

    # Create user
    user = repo.create(
        email=user_data.email,
        hashed_password=hashed_password,
        zip_code=user_data.zip_code,
        latitude=latitude,
        longitude=longitude,
        usda_zone=usda_zone,
        unit_system=unit_system
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
    Get current user information with feature flags.

    Feature flags indicate which features are available based on:
    - User group (amateur/farmer/researcher)
    - User preferences (show_trees, enable_alerts)

    Example response:
    {
        "id": 1,
        "email": "user@example.com",
        "user_group": "amateur_gardener",
        "show_trees": false,
        "enable_alerts": false,
        "feature_flags": {
            "hydroponics": false,
            "tree_shadows": false,
            "alerts_enabled": false
        }
    }
    """
    # Convert user model to dict to add computed fields
    user_dict = {
        "id": current_user.id,
        "email": current_user.email,
        "display_name": current_user.display_name,
        "avatar_url": current_user.avatar_url,
        "city": current_user.city,
        "gardening_preferences": current_user.gardening_preferences,
        "zip_code": current_user.zip_code,
        "latitude": current_user.latitude,
        "longitude": current_user.longitude,
        "usda_zone": current_user.usda_zone,
        "unit_system": current_user.unit_system,
        "is_admin": current_user.is_admin,
        "user_group": current_user.user_group,
        "show_trees": current_user.show_trees,
        "enable_alerts": current_user.enable_alerts,
        "created_at": current_user.created_at,
        "feature_flags": get_feature_flags(current_user)
    }

    return user_dict


@router.patch("/me", response_model=UserResponse)
def update_user_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile information.
    If ZIP code is updated, re-geocode and update coordinates if available.
    """
    repo = UserRepository(db)

    # Get update data
    update_data = profile_data.model_dump(exclude_unset=True)

    # If ZIP code is being updated, process it
    if 'zip_code' in update_data and update_data['zip_code']:
        new_zip = update_data['zip_code']

        # Re-geocode if ZIP code changed
        if new_zip != current_user.zip_code:
            unit_system, geocoded_lat, geocoded_lon = LocationService.process_user_zip_code(new_zip)

            # Update coordinates if geocoding succeeded
            if geocoded_lat is not None and geocoded_lon is not None:
                update_data['latitude'] = geocoded_lat
                update_data['longitude'] = geocoded_lon

            # Update unit system based on new ZIP
            # Only update if user hasn't explicitly set a different unit system
            if 'unit_system' not in update_data:
                update_data['unit_system'] = unit_system

    # Update user
    user = repo.update(current_user, **update_data)

    return user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_current_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete current user account and all associated data.

    This will CASCADE delete:
    - All gardens
    - All planting events
    - All care tasks
    - All seed batches
    - All soil samples
    - All irrigation zones, sources, and watering events
    - All sensor readings
    - All germination events
    - All lands
    - All password reset tokens
    """
    repo = UserRepository(db)
    repo.delete(current_user)
    db.commit()

    return None
