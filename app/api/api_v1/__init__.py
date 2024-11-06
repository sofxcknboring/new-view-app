from core.config import settings
from fastapi import APIRouter

from .core_switches_route import router as core_switch_router
from .device_route import router as device_router
from .switch_route import router as switch_router
from .snmp_control import router as snmp_control_router

router = APIRouter(
    prefix=settings.api.v1.prefix,
)
router.include_router(core_switch_router, prefix=settings.api.v1.core_switches)
router.include_router(switch_router, prefix=settings.api.v1.switches)
router.include_router(device_router, prefix=settings.api.v1.devices)
router.include_router(snmp_control_router, prefix=settings.api.v1.snmp_control)
