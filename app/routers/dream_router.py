"""
dream_router.py - web addresses (endpoints) for dreams, part of feature 9.

PURPOSE
    Lets the website add, list, view and delete dreams. A user can keep
    several dreams at once. The router only receives requests and
    returns replies; the real work is done by dream_service.py.

ENDPOINTS
    POST   /dreams            -> add a dream (reply 201)
    GET    /dreams            -> list all dreams
    GET    /dreams/{id}       -> view one dream (404 if it does not exist)
    DELETE /dreams/{id}       -> delete a dream (reply 204, no body)

WHO USES IT
    - Tanushree's dreamApi.js and DreamListPage
    - main.py must include this router (Riya owns main.py):
          app.include_router(dream_router.router)

THE ONE PLACE THAT CHANGES LATER
    get_dream_repo() is where Ananya's database repository plugs in.
    Until then it raises an error. Tests replace it with a fake store.
"""

from fastapi import APIRouter, Depends, status          # tools for building endpoints

from app.schemas.dream_schema import DreamCreate, DreamResponse   # input / output shapes
from app.services import dream_service                            # the real logic

# every address in this file starts with /dreams
router = APIRouter(prefix="/dreams", tags=["Dreams"])


def get_dream_repo():
    # TO DO: return Ananya's dream repository once it exists
    raise NotImplementedError("Connect the dream repository from M1 here")


@router.post("", response_model=DreamResponse, status_code=status.HTTP_201_CREATED)
def add_dream(data: DreamCreate, repo=Depends(get_dream_repo)):
    # FastAPI has already checked `data` against DreamCreate
    return dream_service.create_dream(repo, data)


@router.get("", response_model=list[DreamResponse])
def list_all_dreams(repo=Depends(get_dream_repo)):
    return dream_service.list_dreams(repo)


@router.get("/{dream_id}", response_model=DreamResponse)
def view_dream(dream_id: int, repo=Depends(get_dream_repo)):
    # the service raises NotFoundError (404) if the dream is missing
    return dream_service.get_dream(repo, dream_id)


@router.delete("/{dream_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_dream(dream_id: int, repo=Depends(get_dream_repo)):
    dream_service.delete_dream(repo, dream_id)