from datetime import datetime, timedelta

from api.api_v1.auth_route import api_key_header
from fastapi import APIRouter, HTTPException, Security
from snmp_sample import add_snmp_to_data_base

router = APIRouter(tags=["Snmp Control"], dependencies=[Security(api_key_header)])


last_run_time = None
lock_duration = timedelta(minutes=15)


@router.get("/", response_model=dict)
async def update_snmp():
    """
    В разработке, возможны ошибки.\n

    Ручной запуск snmp обхода по коммутаторам которые определены в базе данных.\n
    Returns:\n
        200 -> SNMP data updated successfully - операция прошла успешно.
        429 -> SNMP update is already in progress. Please try again later. - операция уже была выполнена ранее. Таймаут - 15 минут.
        500 -> Failed to update SNMP data. - в результате обхода произошла ошибка. Подробнее в "detail"
    """
    global last_run_time

    # Проверка времени последнего выполнения
    if last_run_time and datetime.now() < last_run_time + lock_duration:
        raise HTTPException(status_code=429, detail="SNMP update is already in progress. Please try again later.")

    try:
        last_run_time = datetime.now()
        result = await add_snmp_to_data_base()
        if result:
            return {"message": "SNMP data updated successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to update SNMP data")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
