"""
Data models for job applications and email processing.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum

class JobStatus(Enum):
    """Job application status enumeration."""
    APPLIED = "Applied"
    REJECTED = "Rejected"
    INTERVIEW_SCHEDULED = "Interview Scheduled"
    ASSESSMENT_RECEIVED = "Assessment Received"
    OFFER_RECEIVED = "Offer Received"
    WITHDRAWN = "Withdrawn"
    NO_RESPONSE = "No Response"

class EmailType(Enum):
    """Email type classification."""
    APPLICATION_CONFIRMATION = "application_confirmation"
    REJECTION = "rejection"
    INTERVIEW_INVITATION = "interview_invitation"
    ASSESSMENT_REQUEST = "assessment_request"
    OFFER = "offer"
    OTHER = "other"

@dataclass
class JobApplication:
    """Data model for a job application."""
    company: str
    position: str
    date_applied: datetime
    status: JobStatus = JobStatus.APPLIED
    email_date: Optional[datetime] = None
    notes: str = ""
    email_subject: str = ""
    email_id: str = ""
    
    def to_sheets_row(self) -> List[str]:
        """Convert to a row format for Google Sheets."""
        return [
            self.date_applied.strftime("%Y-%m-%d") if self.date_applied else "",
            self.company,
            self.position,
            self.status.value,
            self.email_date.strftime("%Y-%m-%d %H:%M") if self.email_date else "",
            self.notes,
            self.email_subject,
            self.email_id
        ]
    
    @classmethod
    def from_sheets_row(cls, row: List[str]) -> 'JobApplication':
        """Create JobApplication from Google Sheets row."""
        return cls(
            company=row[1] if len(row) > 1 else "",
            position=row[2] if len(row) > 2 else "",
            date_applied=datetime.strptime(row[0], "%Y-%m-%d") if len(row) > 0 and row[0] else datetime.now(),
            status=JobStatus(row[3]) if len(row) > 3 and row[3] else JobStatus.APPLIED,
            email_date=datetime.strptime(row[4], "%Y-%m-%d %H:%M") if len(row) > 4 and row[4] else None,
            notes=row[5] if len(row) > 5 else "",
            email_subject=row[6] if len(row) > 6 else "",
            email_id=row[7] if len(row) > 7 else ""
        )

@dataclass
class EmailData:
    """Data model for processed email information."""
    email_id: str
    subject: str
    sender: str
    date: datetime
    body: str
    email_type: EmailType = EmailType.OTHER
    company: str = ""
    position: str = ""
    confidence: float = 0.0
    
@dataclass
class NotificationData:
    """Data model for notification information."""
    job_application: JobApplication
    email_data: EmailData
    notification_type: str  # "interview" or "assessment"
    recipients: List[str] = field(default_factory=list)
