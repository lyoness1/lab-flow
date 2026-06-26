from labflow.models.lab_message import LabMessage, Observation


def lab_message_normal() -> LabMessage:
    return LabMessage(
        schema_version="lab-message-v0",
        message_id="MSG-0001",
        patient_ref="pt-8842",
        observations=[
            Observation(code="potassium", value=4.2, unit="mmol/L"),
            Observation(code="sodium", value=139, unit="mmol/L"),
        ],
    )


def lab_message_critical() -> LabMessage:
    return LabMessage(
        schema_version="lab-message-v0",
        message_id="MSG-0002",
        patient_ref="pt-9910",
        observations=[
            Observation(code="potassium", value=6.4, unit="mmol/L"),
            Observation(code="sodium", value=137, unit="mmol/L"),
        ],
    )
