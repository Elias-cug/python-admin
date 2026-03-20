from sqlalchemy import text
from app.core.config import get_settings
from app.models.user import User
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserQuery, UserUpdate


def _table_ref() -> str:
    # Quote `user` because it's a reserved-ish identifier in some DBs.
    settings = get_settings()
    if settings.db_schema:
        return f'"{settings.db_schema}"."user"'
    return '"user"'


def create_user(
    db: Session,
    user_in: UserCreate,
    *,
    password_hash: str,
):
    data = user_in.model_dump()
    data["password_hash"] = password_hash
    user = User(**data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def del_user(db: Session, user_id: int):
    user = get_user(db, user_id)
    if not user:
        return None

    user.is_deleted = True
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user_in: UserUpdate):
    user = get_user(db, user_in.id)
    if not user:
        return None

    for field, value in user_in.model_dump(exclude_unset=True).items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


def update_user_password(db: Session, user_id: int, *, password_hash: str) -> User | None:
    user = get_user(db, user_id)
    if not user:
        return None

    user.password_hash = password_hash
    db.commit()
    db.refresh(user)
    return user


def get_user(db: Session, user_id: int) -> User | None:
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    return user


def list_user(db: Session, user_in: UserQuery):
    tbl = _table_ref()

    where_parts: list[str] = ["is_deleted IS FALSE"]
    params = dict()

    if user_in.tenant_id is not None:
        where_parts.append("tenant_id = :tenant_id")
        params["tenant_id"] = user_in.tenant_id

    if user_in.username is not None:
        where_parts.append("username = :username")
        params["username"] = user_in.username

    if user_in.email is not None:
        where_parts.append(f"email ILIKE :email")
        params["email"] = f"%{user_in.email}%"

    if user_in.phone is not None:
        where_parts.append(f"phone LIKE :phone")
        params["phone"] = f"%{user_in.phone}%"

    if user_in.display_name is not None:
        where_parts.append(f"display_name LIKE :display_name")
        params["display_name"] = f"%{user_in.display_name}%"

    if user_in.created_from is not None:
        where_parts.append("created_at >= :created_from")
        params["created_from"] = user_in.created_from

    if user_in.created_to is not None:
        where_parts.append("created_at <= :created_to")
        params["created_to"] = user_in.created_to

    where_sql = " AND ".join(where_parts) if where_parts else True

    count_sql = f"SELECT COUNT(*) AS total FROM {tbl} WHERE {where_sql}"

    total = db.execute(text(count_sql), params).scalar_one()

    offset = (user_in.page - 1) * user_in.page_size

    params_page = dict(params)
    params_page["limit"] = user_in.page_size
    params_page["offset"] = offset

    data_sql = f"""
      SELECT
        id,
        tenant_id,
        username,
        email,
        phone,
        status,
        display_name,
        avatar_url,
        last_login_at,
        last_login_ip,
        created_at,
        updated_at
      FROM
        {tbl}
      WHERE
        {where_sql}
      LIMIT :limit OFFSET :offset
  """

    rows = db.execute(text(data_sql), params_page).mappings().all()

    return [dict(r) for r in rows], total
