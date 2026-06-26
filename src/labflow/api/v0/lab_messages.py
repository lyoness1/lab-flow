from fastapi import APIRouter, status

from labflow.constants import WORKFLOW_RUN_ID_PREFIX
from labflow.models.lab_message import LabMessage, LabMessageCreateResponse
from labflow.utils import create_id

router = APIRouter()


@router.post(
    "/lab-messages",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=LabMessageCreateResponse,
)
def create_lab_message(body: LabMessage) -> LabMessageCreateResponse:
    # Persistence, idempotency (200/409), and workflow.created land in the Postgres PR.
    return LabMessageCreateResponse(
        workflow_run_id=create_id(WORKFLOW_RUN_ID_PREFIX),
        message_id=body.message_id,
    )
