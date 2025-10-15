"""Service layer for business logic"""
from .document_processor import DocumentProcessor
from .calendar_service import CalendarService
from .crm_service import CRMService

__all__ = [
    "DocumentProcessor",
    "CalendarService",
    "CRMService"
]

