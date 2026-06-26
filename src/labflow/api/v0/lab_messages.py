from uuid import uuid4

from fastapi import APIRouter, status

from labflow.schemas.lab_message import LabMessage, LabMessageCreateResponse

router = APIRouter()


@router.post(
    "/lab-messages",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=LabMessageCreateResponse,
)
def create_lab_message(body: LabMessage) -> LabMessageCreateResponse:
    # Persistence, idempotency (200/409), and workflow.created land in the Postgres PR.
    return LabMessageCreateResponse(
        workflow_run_id=f"wr_{uuid4().hex[:12]}",
        message_id=body.message_id,
    )
