"""
Chloé API - Pydantic Models Package

This package contains all the Pydantic models used in the Chloé API.

Structure:
- models.py: Core response schemas (Metadata, Lead, Post, Reaction, Insights, etc.)
- invoke_models.py: Request/Response models for the /invoke endpoint
"""

from app.models.models import (
    # Enums
    ProcessingMode,
    # Core Response Models
    Metadata,
    Lead,
    Post,
    Reaction,
    PostAuthor,
    # Insights
    Insights,
    ProfileInsight,
    InteractionsInsight,
    OutreachMessages,
    PostComment,
    LinkedInMessages,
    EmailMessage,
    EmailSequence,
    # Raw Data & Errors
    RawData,
    ResponseError,
)

from app.models.invoke_models import (
    InvokeRequest,
    InvokeResponse,
    ErrorResponse,
)

__all__ = [
    # Enums
    "ProcessingMode",
    "PostType",
    "ReactionAction",
    # Core Response Models
    "Metadata",
    "Lead",
    "Location",
    "Post",
    "Reaction",
    "PostAuthor",
    "Posts",
    "Reactions",
    # Insights
    "Insights",
    "ProfileInsight",
    "InteractionsInsight",
    "OutreachMessages",
    "PostComment",
    "LinkedInMessages",
    "EmailMessage",
    "EmailSequence",
    # Raw Data & Errors
    "RawData",
    "ResponseError",
    # Request/Response
    "InvokeRequest",
    "InvokeResponse",
    "ErrorResponse",
]
