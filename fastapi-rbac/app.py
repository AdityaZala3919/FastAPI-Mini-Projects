import secrets
from fastapi import APIRouter, FastAPI, Depends
from fastapi.responses import RedirectResponse
from auth import rbac_dependency, is_leader_dependency

app = FastAPI()
router = APIRouter(prefix="/api/rbac")

@app.get("/")
def get_root():
    return RedirectResponse("/docs")

@app.get("/hex")
def get_hex_id():
    return {
        "hex_id": secrets.token_hex(16)
    }

@router.get("/roles_and_ids")
def return_roles_and_ids(allowed: bool = Depends(is_leader_dependency)):
    return {
        "Leader": "8882ab1ef43e6107498389f7c5490563",
        "Co-Leader": "d97f2fc30e804ad1c9509cecede601e8",
        "Elder": "b9036e63783751545fc2d8a6edcca5b7",
        "Member": "b00912b712b2176ece1783c11fdf6265",
    }

@router.get("/leader")
def leader_func(
    your_role: tuple = Depends(rbac_dependency("Leader"))
):
    return {
        "your_role": your_role,
        "role": "Leader",
        "message": "Congrats, You are the leader of this clan."
    }

@router.get("/co-leader/{id}")
def co_leader_func(
    your_role: tuple = Depends(rbac_dependency("Co-Leader"))
):
    return {
        "your_role": your_role,
        "role": "Co-Leader",
        "message": "Congrats, You are co-leader of this clan. Better luck next time for leader."
    }

@router.get("/elder/{id}")
def elder_func(
    your_role: tuple = Depends(rbac_dependency("Elder"))
):
    return {
        "your_role": your_role,
        "role": "Elder",
        "message": "Hmm, You are still elder? LOL."
    }

@router.get("/member/{id}")
def member_func(
    your_role: tuple = Depends(rbac_dependency("Member"))
):
    return {
        "your_role": your_role,
        "role": "Member",
        "message": "Welcome to clan, Bro."
    }

app.include_router(router)