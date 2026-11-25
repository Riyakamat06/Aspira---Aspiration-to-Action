"""
dream_router.py - web addresses (endpoints) for dreams, part of feature 9.

PURPOSE
    Lets the website add, list, view and delete dreams. A user can keep
    several dreams at once. The router only receives requests and returns
    replies; the real work is done by dream_service.py, which uses
    Ananya's database code.

ENDPOINTS
    POST   /dreams            -> add a dream (reply 201)
    GET    /dreams            -> list this user's dreams
    GET    /dreams/{id}       -> view one dream (404 if it is not theirs)
    DELETE /dreams/{id}       -> delete a dream and everything under it (204)

WHO USES IT
    - Tanushree's dreamApi.js and DreamListPage
    - main.py must include this router (Riya owns main.py):
          app.include_router(dream_router.router)

TEMPORARY PART
    get_current_user_id() returns the demo user (id 1) until Riya's login
    (get_current_user in dependencies.py) is in main. When it is, this
    one function is the only thing that changes. The journal, task and
    analytics routers import it from here.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db                                  # Ananya's session helper
from app.schemas.dream_schema import DreamCreate, DreamResponse    # input / output shapes
from app.services import dream_service                             # the real logic

DEMO_USER_ID = 1   # the seeded demo user (Ananya's seed_data.py)

# every address in this file starts with /dreams
router = APIRouter(prefix="/dreams", tags=["Dreams"])


def get_current_user_id() -> int:
    # TO DO: replace with Riya's get_current_user once it is in main
    return DEMO_USER_ID


@router.post("", response_model=DreamResponse, status_code=status.HTTP_201_CREATED)
def add_dream(data: DreamCreate, db: Session = Depends(get_db),
              user_id: int = Depends(get_current_user_id)):
    # FastAPI has already checked `data` against DreamCreate
    return dream_service.create_dream(db, user_id, data)


@router.get("", response_model=list[DreamResponse])
def list_all_dreams(db: Session = Depends(get_db),
                    user_id: int = Depends(get_current_user_id)):
    return dream_service.list_dreams(db, user_id)


@router.get("/{dream_id}", response_model=DreamResponse)
def view_dream(dream_id: int, db: Session = Depends(get_db),
               user_id: int = Depends(get_current_user_id)):
    # the service raises NotFoundError (404) if the dream is missing or not theirs
    return dream_service.get_dream(db, user_id, dream_id)


@router.delete("/{dream_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_dream(dream_id: int, db: Session = Depends(get_db),
                 user_id: int = Depends(get_current_user_id)):
    dream_service.delete_dream(db, user_id, dream_id)
