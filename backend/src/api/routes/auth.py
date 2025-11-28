from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
async def register():
    return {"msg": "To be implemented"}

@router.post("/login")
async def login():
    return {"msg": "To be implemented"}