from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_current_user, get_db
from app.config import settings
from app.models import User
from app.schemas import AuthResponse, LoginRequest, SignUpRequest, UpdateProfileRequest, UserPublic
from app.services import create_access_token, hash_password, verify_password


router = APIRouter(prefix="/auth", tags=["auth"])


def _password_matches(plain_password: str, hashed_password: str) -> bool:
    try:
        return verify_password(plain_password, hashed_password)
    except Exception:  # noqa: BLE001
        return False


def _recover_bootstrap_admin(email: str, password: str, db: Session) -> User | None:
    bootstrap_email = settings.bootstrap_admin_email.strip().lower()
    bootstrap_password = settings.bootstrap_admin_password
    bootstrap_name = settings.bootstrap_admin_name.strip() or "Responsable"

    if not bootstrap_email or not bootstrap_password:
        return None

    if email != bootstrap_email or password != bootstrap_password:
        return None

    admin = db.execute(select(User).where(User.email == bootstrap_email)).scalar_one_or_none()
    if admin is None:
        admin = User(
            name=bootstrap_name,
            email=bootstrap_email,
            password_hash=hash_password(bootstrap_password),
        )
    else:
        admin.name = bootstrap_name
        admin.password_hash = hash_password(bootstrap_password)
        admin.is_active = True

    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: SignUpRequest, db: Session = Depends(get_db)) -> AuthResponse:
    email = payload.email.strip().lower()
    name = payload.name.strip()

    if payload.password != payload.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Les mots de passe ne correspondent pas.")

    existing = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Un compte avec cet email existe deja.")

    user = User(name=name, email=email, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=user.email, user_id=user.id)
    return AuthResponse(access_token=token, user=UserPublic.model_validate(user))


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    email = payload.email.strip().lower()
    user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()

    if user and _password_matches(payload.password, user.password_hash):
        token = create_access_token(subject=user.email, user_id=user.id)
        return AuthResponse(access_token=token, user=UserPublic.model_validate(user))

    recovered_admin = _recover_bootstrap_admin(email=email, password=payload.password, db=db)
    if recovered_admin is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ou mot de passe incorrect.")

    token = create_access_token(subject=recovered_admin.email, user_id=recovered_admin.id)
    return AuthResponse(access_token=token, user=UserPublic.model_validate(recovered_admin))


@router.get("/me", response_model=UserPublic)
def me(current_user: User = Depends(get_current_user)) -> UserPublic:
    return UserPublic.model_validate(current_user)


@router.put("/me", response_model=UserPublic)
def update_me(
    payload: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserPublic:
    email = payload.email.strip().lower()
    name = payload.name.strip()

    existing = db.execute(
        select(User).where(User.email == email, User.id != current_user.id),
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Un compte avec cet email existe deja.")

    current_user.name = name
    current_user.email = email
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return UserPublic.model_validate(current_user)
