from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


# --- Request schemas ---


class BatchCallRecipient(BaseModel):
    phone_number: str
    dynamic_variables: Optional[Dict[str, str]] = None


class SubmitBatchCallRequest(BaseModel):
    call_name: str
    agent_id: str
    recipients: List[BatchCallRecipient]
    scheduled_time_unix: Optional[int] = None
    agent_phone_number_id: Optional[str] = None
    timezone: Optional[str] = None


# --- Response schemas ---


class AgentSummary(BaseModel):
    model_config = ConfigDict(extra="ignore")

    agent_id: str
    name: str


class AgentListResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    agents: List[AgentSummary]
    next_cursor: Optional[str] = None


class AgentDetailResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    agent_id: str
    name: str
    phone_numbers: List[Dict[str, Any]] = []
    conversation_config: Optional[Dict[str, Any]] = None


class PhoneNumberItem(BaseModel):
    model_config = ConfigDict(extra="ignore")

    phone_number_id: str
    phone_number: Optional[str] = None
    label: Optional[str] = None
    provider: Optional[str] = None


class BatchJob(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    name: Optional[str] = None
    agent_id: str
    status: str
    total_calls_scheduled: int = 0
    total_calls_dispatched: int = 0
    total_calls_finished: int = 0
    retry_count: int = 0
    created_at_unix: Optional[int] = None
    scheduled_time_unix: Optional[int] = None
    last_updated_at_unix: Optional[int] = None
    agent_name: Optional[str] = None
    phone_number_id: Optional[str] = None


class BatchJobListResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    batch_calls: List[BatchJob]
    next_doc: Optional[str] = None
    has_more: bool = False


class SubmitBatchCallResponse(BatchJob):
    pass


# --- Batch detail / monitoring schemas ---


class BatchRecipientStatus(BaseModel):
    model_config = ConfigDict(extra="ignore")

    phone_number: str
    status: str
    conversation_id: Optional[str] = None
    call_duration_secs: Optional[float] = None


class BatchDetailResponse(BatchJob):
    recipients: List[BatchRecipientStatus] = []


# --- Conversation schemas ---


class ConversationSummary(BaseModel):
    model_config = ConfigDict(extra="ignore")

    conversation_id: str
    agent_id: str
    status: str
    start_time_unix: Optional[int] = None
    end_time_unix: Optional[int] = None
    call_duration_secs: Optional[float] = None
    call_successful: Optional[str] = None


class ConversationListResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    conversations: List[ConversationSummary] = []
    next_cursor: Optional[str] = None
    has_more: bool = False


# --- Conversation detail schemas ---


class TranscriptMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")

    role: str  # "agent" or "user"
    message: str
    time_in_call_secs: Optional[float] = None
    duration_secs: Optional[float] = None

    @field_validator("message", mode="before")
    @classmethod
    def _coerce_message(cls, v: Any) -> str:
        # Upstream sometimes returns null messages; frontend expects a string.
        if v is None:
            return ""
        return str(v)


class EvaluationCriterionResult(BaseModel):
    model_config = ConfigDict(extra="ignore")

    criteria_id: Optional[str] = None
    name: Optional[str] = None
    result: Optional[str] = None  # "success", "failure", etc.
    rationale: Optional[str] = None

    @field_validator("result", mode="before")
    @classmethod
    def _coerce_result(cls, v: Any) -> Optional[str]:
        if v is None:
            return None
        return str(v)


class DataCollectionResult(BaseModel):
    model_config = ConfigDict(extra="ignore")

    data_collection_id: Optional[str] = None
    name: Optional[str] = None
    value: Optional[str] = None
    rationale: Optional[str] = None

    @field_validator("value", mode="before")
    @classmethod
    def _coerce_value(cls, v: Any) -> Optional[str]:
        if v is None:
            return None
        return str(v)


class ConversationAnalysis(BaseModel):
    model_config = ConfigDict(extra="ignore")

    call_successful: Optional[str] = None
    transcript_summary: Optional[str] = None
    evaluation_criteria_results: Optional[List[EvaluationCriterionResult]] = None
    data_collection_results: Optional[List[DataCollectionResult]] = None

    @model_validator(mode="before")
    @classmethod
    def _coerce_result_maps_to_lists(cls, data: Any) -> Any:
        """
        ElevenLabs can return *_results as either:
        - a list of objects (expected by our schema), or
        - a dict keyed by id/name with object values.
        """
        if not isinstance(data, dict):
            return data

        ecr = data.get("evaluation_criteria_results")
        if isinstance(ecr, dict):
            coerced: List[Dict[str, Any]] = []
            for key, value in ecr.items():
                if isinstance(value, dict):
                    item = dict(value)
                    item.setdefault("criteria_id", str(key))
                    coerced.append(item)
                else:
                    coerced.append({"criteria_id": str(key), "result": str(value)})
            data["evaluation_criteria_results"] = coerced

        dcr = data.get("data_collection_results")
        if isinstance(dcr, dict):
            coerced2: List[Dict[str, Any]] = []
            for key, value in dcr.items():
                if isinstance(value, dict):
                    item = dict(value)
                    item.setdefault("data_collection_id", str(key))
                    coerced2.append(item)
                else:
                    coerced2.append({"data_collection_id": str(key), "value": str(value)})
            data["data_collection_results"] = coerced2

        return data


class ConversationDetailResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    conversation_id: str
    agent_id: str
    status: str
    start_time_unix: Optional[int] = None
    end_time_unix: Optional[int] = None
    call_duration_secs: Optional[float] = None
    has_audio: bool = False
    transcript: List[TranscriptMessage] = []
    metadata: Optional[Dict[str, Any]] = None
    analysis: Optional[ConversationAnalysis] = None
