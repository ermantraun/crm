from .dto import LeadCreateInDTO, InsighCreateInDto
from .exceptions import InvalidLeadDataException, InvalidInsightDataException
from domen.entities import (
    EMAIL_MAX_LEN,
    PHONE_MAX_LEN,
    NAME_MAX_LEN,
    SOURCE_MAX_LEN,
    MIN_NAME_LEN,
)

class ValidateLead:
    def __init__(self, lead: LeadCreateInDTO) -> None:
        self.lead = lead

    def _norm(self, v: str | None) -> str | None:
        return v.strip() if v is not None else None

    def validate(self) -> None:
        errors: list[str] = []

        self.lead.email = self._norm(self.lead.email)
        self.lead.phone = self._norm(self.lead.phone)
        self.lead.name = self._norm(self.lead.name)
        self.lead.note = self._norm(self.lead.note)
        self.lead.source = self._norm(self.lead.source)

        if not self.lead.note:
            errors.append("note is required and cannot be blank.")

        # email (optional)
        if self.lead.email:
            email = self.lead.email
            if email.count("@") != 1:
                errors.append("email has invalid format.")
            else:
                local, domain = email.split("@", 1)
                if not local or not domain or "." not in domain:
                    errors.append("email has invalid format (invalid parts).")
            if len(email) > EMAIL_MAX_LEN:
                errors.append(f"email length must be <= {EMAIL_MAX_LEN}.")

        # phone (optional)
        if self.lead.phone:
            phone = self.lead.phone
            if not phone.isdigit():
                errors.append("phone must contain only digits.")
            if len(phone) > PHONE_MAX_LEN:
                errors.append(f"phone length must be <= {PHONE_MAX_LEN}.")

        # name (optional)
        if self.lead.name:
            name = self.lead.name
            if len(name) < MIN_NAME_LEN:
                errors.append(f"name must be at least {MIN_NAME_LEN} chars.")
            if len(name) > NAME_MAX_LEN:
                errors.append(f"name length must be <= {NAME_MAX_LEN}.")

        # source (optional)
        if self.lead.source and len(self.lead.source) > SOURCE_MAX_LEN:
            errors.append(f"source length must be <= {SOURCE_MAX_LEN}.")

        if errors:
            raise InvalidLeadDataException("; ".join(errors))

class ValidateInsight:
    def __init__(self, insight: InsighCreateInDto) -> None:
        self.insight = insight

    def _norm(self, v: str | None) -> str | None:
        return v.strip() if v is not None else None

    def validate(self) -> None:
        errors: list[str] = []
        self.insight.content = self._norm(self.insight.content)
        self.insight.lead_id = self._norm(self.insight.lead_id)
        self.insight.content_hash = self._norm(self.insight.content_hash)

        if not self.insight.content:
            errors.append("content is required and cannot be blank.")
        if not self.insight.lead_id:
            errors.append("lead_id is required and cannot be blank.")
        if not self.insight.content_hash:
            errors.append("content_hash is required and cannot be blank.")

        if errors:
            raise InvalidInsightDataException("; ".join(errors))


