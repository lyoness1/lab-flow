from fastapi import APIRouter

from labflow.api.v0 import health, lab_messages
from labflow.constants import API_V0_PREFIX

router = APIRouter(prefix=API_V0_PREFIX)
router.include_router(health.router)
router.include_router(lab_messages.router)
