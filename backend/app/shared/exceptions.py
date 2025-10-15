"""
Custom exceptions for RealInbox AI
Centralized exception handling for better error management
"""
from typing import Optional, Dict, Any


class RealInboxBaseException(Exception):
    """Base exception for all RealInbox exceptions"""
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


# AI Agent Exceptions
class AIAgentException(RealInboxBaseException):
    """Base exception for AI agent errors"""
    pass


class TriageException(AIAgentException):
    """Triage agent specific errors"""
    pass


class DraftGenerationException(AIAgentException):
    """Draft generation errors"""
    pass


class LeadQualificationException(AIAgentException):
    """Lead qualification errors"""
    pass


# Integration Exceptions
class IntegrationException(RealInboxBaseException):
    """Base exception for integration errors"""
    pass


class GmailIntegrationException(IntegrationException):
    """Gmail API integration errors"""
    pass


class OutlookIntegrationException(IntegrationException):
    """Outlook/Microsoft Graph API errors"""
    pass


class TwilioIntegrationException(IntegrationException):
    """Twilio SMS/WhatsApp errors"""
    pass


class PineconeException(IntegrationException):
    """Pinecone vector store errors"""
    pass


# Authentication & Authorization Exceptions
class AuthenticationException(RealInboxBaseException):
    """Authentication failures"""
    pass


class AuthorizationException(RealInboxBaseException):
    """Authorization/permission errors"""
    pass


class InvalidTokenException(AuthenticationException):
    """Invalid or expired JWT token"""
    pass


class InsufficientPermissionsException(AuthorizationException):
    """User lacks required permissions"""
    pass


# Data Validation Exceptions
class ValidationException(RealInboxBaseException):
    """Data validation errors"""
    pass


class InvalidEmailFormatException(ValidationException):
    """Invalid email format"""
    pass


class InvalidConfigurationException(ValidationException):
    """Invalid configuration or missing required settings"""
    pass


# Resource Exceptions
class ResourceException(RealInboxBaseException):
    """Base exception for resource-related errors"""
    pass


class ResourceNotFoundException(ResourceException):
    """Requested resource not found"""
    pass


class ResourceAlreadyExistsException(ResourceException):
    """Resource already exists (duplicate)"""
    pass


class ResourceConflictException(ResourceException):
    """Resource state conflict"""
    pass


# Rate Limiting Exceptions
class RateLimitException(RealInboxBaseException):
    """Rate limit exceeded"""
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        **kwargs
    ):
        self.retry_after = retry_after
        super().__init__(message, **kwargs)


# External Service Exceptions
class ExternalServiceException(RealInboxBaseException):
    """External service (API) errors"""
    pass


class AnthropicAPIException(ExternalServiceException):
    """Claude/Anthropic API errors"""
    pass


class GoogleAPIException(ExternalServiceException):
    """Google API errors"""
    pass


class MicrosoftAPIException(ExternalServiceException):
    """Microsoft API errors"""
    pass


# Database Exceptions
class DatabaseException(RealInboxBaseException):
    """Database operation errors"""
    pass


class DatabaseConnectionException(DatabaseException):
    """Database connection failures"""
    pass


class DatabaseTransactionException(DatabaseException):
    """Transaction rollback or integrity errors"""
    pass


# Task/Worker Exceptions
class TaskException(RealInboxBaseException):
    """Celery task errors"""
    pass


class TaskTimeoutException(TaskException):
    """Task exceeded time limit"""
    pass


class TaskRetryException(TaskException):
    """Task needs retry"""
    def __init__(
        self,
        message: str,
        retry_count: int = 0,
        max_retries: int = 3,
        **kwargs
    ):
        self.retry_count = retry_count
        self.max_retries = max_retries
        super().__init__(message, **kwargs)


# Business Logic Exceptions
class BusinessLogicException(RealInboxBaseException):
    """Business rule violations"""
    pass


class EmailAlreadyTriagedException(BusinessLogicException):
    """Email has already been triaged"""
    pass


class DraftNotApprovedException(BusinessLogicException):
    """Draft must be approved before sending"""
    pass


class SubscriptionLimitException(BusinessLogicException):
    """Subscription tier limit reached"""
    pass


# Security Exceptions
class SecurityException(RealInboxBaseException):
    """Security-related errors"""
    pass


class EncryptionException(SecurityException):
    """Encryption/decryption errors"""
    pass


class PhishingDetectedException(SecurityException):
    """Potential phishing email detected"""
    pass


# File/Storage Exceptions
class StorageException(RealInboxBaseException):
    """File storage errors"""
    pass


class S3UploadException(StorageException):
    """AWS S3 upload failures"""
    pass


class FileTooBigException(StorageException):
    """File exceeds size limit"""
    pass

