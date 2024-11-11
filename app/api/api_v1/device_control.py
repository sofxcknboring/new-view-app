from fastapi import APIRouter, HTTPException
from core.services.device_control.device_controller import get_win_user
router = APIRouter(tags=["DeviceControl"])



@router.get("/get_user/{ip_address}", response_model=dict)
def get_active_user(ip_address: str):
    """
    Тестовый endpoint, получает пользователя с OS Windows
    Timeout = 5sec
    Args:
        ip_address: str

    Returns:
        user: str
    """
    try:
        user = get_win_user(ip_address=ip_address)
        return {'message': user}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
