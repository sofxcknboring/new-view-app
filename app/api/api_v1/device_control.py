from fastapi import APIRouter

router = APIRouter(tags=["DeviceControl"])


@router.post("/", response_model=str)
async def just_for_tests():
    return "Undefined"
