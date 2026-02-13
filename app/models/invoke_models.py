"""
Pydantic models for request and response schemas
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from enum import Enum
from app.models.models import (
    ProcessingMode,
    Metadata,
    Lead,
    Insights,
    RawData,
    ResponseError,
)


class SupportedLanguage(str, Enum):
    """Supported languages for insights and outreach generation"""

    ENGLISH = "English"
    FRENCH = "French"
    SPANISH = "Spanish"
    GERMAN = "German"
    ITALIAN = "Italian"
    PORTUGUESE = "Portuguese"
    DUTCH = "Dutch"
    POLISH = "Polish"
    RUSSIAN = "Russian"
    CHINESE = "Chinese"
    JAPANESE = "Japanese"
    KOREAN = "Korean"
    ARABIC = "Arabic"


class InvokeRequest(BaseModel):
    """
    Request to analyze a LinkedIn lead profile and generate AI-powered insights.

    Configure what data to fetch, which AI insights to generate, and processing parameters.
    All AI features are enabled by default for comprehensive analysis.
    """

    # === REQUIRED FIELDS ===
    linkedin_url: str = Field(
        ...,
        description="LinkedIn profile URL of the lead to analyze (required)",
        examples=["https://www.linkedin.com/in/firstname-lastname-id/"],
    )

    # === DATA COLLECTION PARAMETERS ===
    posts_limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Number of recent LinkedIn posts to fetch and analyze (1-100). Recommended: 10-25 for balanced analysis",
    )
    reactions_limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Number of recent LinkedIn reactions to analyze (1-100). Recommended: 10-25 for engagement insights",
    )

    # === AI INSIGHTS GENERATION FLAGS ===
    get_profile_insight: bool = Field(
        default=True,
        description="Generate AI-powered profile analysis (summary, work experience, education, topics, keywords, interests)",
    )
    get_interactions_insight: bool = Field(
        default=True,
        description="Generate AI-powered interactions analysis (engagement style, pain points, approach angles)",
    )
    get_outreach_messages: bool = Field(
        default=True,
        description="Generate AI-crafted outreach suggestions (post comments, LinkedIn DMs, email sequences)",
    )

    # === LANGUAGE CONFIGURATION ===
    insights_languages: SupportedLanguage = Field(
        default=SupportedLanguage.FRENCH,
        description="Language for generating profile and interactions insights. Default: French",
    )
    outreach_messages_languages: Optional[SupportedLanguage] = Field(
        default=None,
        description="Language for outreach messages (DMs, emails, comments). If not specified, auto-detects from lead's profile. Default: English if no language detected",
    )

    # === DATA OPTIONS ===
    get_raw_data: bool = Field(
        default=False,
        description="Include complete structured data (profile, experiences, educations, certifications, posts, reactions) in raw_data field. Default: false (not included)",
    )

    # === RESTRICTED FEATURES (Require Special Access) ===
    get_emails: bool = Field(
        default=False,
        description="Retrieve email addresses (⚠️ RESTRICTED: requires special access. Contact contact@idun-group.com)",
    )
    get_phones: bool = Field(
        default=False,
        description="Retrieve phone numbers (⚠️ RESTRICTED: requires special access. Contact contact@idun-group.com)",
    )

    # === AI PROCESSING MODE ===
    mode: ProcessingMode = Field(
        default=ProcessingMode.BALANCED,
        description="AI processing mode: 'fast' (lower quality, faster), 'balanced' (recommended), or 'pro' (highest quality, slower)",
    )

    # === CUSTOM PROMPTS (Optional) ===
    company_name: Optional[str] = Field(
        default=None,
        description="Your company name. Used in prompts for personalization.",
    )
    custom_company_context: Optional[str] = Field(
        default=None,
        description="Custom company context to use instead of default. Include company info, offerings, values, target customers, etc.",
    )
    custom_profile_prompt: Optional[str] = Field(
        default=None,
        description="Custom prompt template for profile insight generation. Must include placeholders: {company_context}, {company_name}, {date_now}, {full_name}, etc.",
    )
    custom_interactions_prompt: Optional[str] = Field(
        default=None,
        description="Custom prompt template for interactions insight generation.",
    )
    custom_outreach_prompt: Optional[str] = Field(
        default=None,
        description="Custom prompt template for outreach messages generation.",
    )

    @field_validator("linkedin_url")
    @classmethod
    def validate_linkedin_url(cls, v: str) -> str:
        """Validate LinkedIn URL format"""
        if not v:
            raise ValueError("LinkedIn URL is required")

        # Basic LinkedIn URL validation
        valid_patterns = [
            "linkedin.com/in/",
            "www.linkedin.com/in/",
            "https://linkedin.com/in/",
            "https://www.linkedin.com/in/",
        ]

        if not any(pattern in v.lower() for pattern in valid_patterns):
            raise ValueError(
                "Invalid LinkedIn URL format. Expected format: "
                "https://www.linkedin.com/in/firstname-lastname-id/"
            )

        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "linkedin_url": "https://www.linkedin.com/in/geoffrey-harrazi9/",
                    "posts_limit": 15,
                    "reactions_limit": 15,
                    "get_profile_insight": True,
                    "get_interactions_insight": True,
                    "get_outreach_messages": True,
                    "insights_languages": "French",
                    "outreach_messages_languages": "English",
                    "mode": "balanced",
                }
            ]
        }
    }


class InvokeResponse(BaseModel):
    """
    Complete response from the Chloé AI Sales Agent analysis.

    This response includes lead profile, AI-generated insights, and any warnings or errors.
    Posts, reactions, and detailed profile data are available in raw_data if requested.
    Follows v1.0.4 schema specification.
    """

    metadata: Metadata = Field(
        ...,
        description="Response metadata including version, request ID, timing, processing mode, and warnings",
    )
    lead: Lead = Field(
        ...,
        description="Structured lead profile information extracted from LinkedIn (name, title, company, location, languages)",
    )
    insights: Insights = Field(
        default_factory=Insights,
        description="AI-generated insights bundle (profile analysis, interactions analysis, outreach suggestions)",
    )
    phones: str = Field(
        default="Restricted access, please contact contact@idun-group.com to get access",
        description="Lead's phone numbers (restricted feature - requires special access)",
    )
    emails: str = Field(
        default="Restricted access, please contact contact@idun-group.com to get access",
        description="Lead's email addresses (restricted feature - requires special access)",
    )
    raw_data: Optional[RawData] = Field(
        None,
        description="Complete structured data from LinkedIn including profile, experiences, educations, certifications, posts, and reactions. Only included if get_raw_data=true in request. Use this to access posts and reactions data.",
    )
    errors: list[ResponseError] = Field(
        default_factory=list,
        description="Array of error objects if any errors occurred during processing (empty on success)",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "metadata": {
                        "version": "1.0.4",
                        "request_id": "req_7a8b9c_12345",
                        "started_at": "2025-10-19T12:34:56Z",
                        "duration_ms": 8500,
                        "mode": "balanced",
                        "warnings": ["Only 5 posts found (requested 10)"],
                    },
                    "lead": {
                        "linkedin_url": "https://www.linkedin.com/in/john-doe/",
                        "full_name": "John Doe",
                        "first_name": "John",
                        "last_name": "Doe",
                        "headline": "Head of Product at Acme Corp | Building AI-powered solutions",
                        "current_title": "Head of Product",
                        "current_company": "Acme Corp",
                        "location": "Paris, Île-de-France, France",
                        "languages": "English",
                    },
                    "insights": {
                        "profile_insight": {
                            "summary": "Experienced product leader with 10+ years in tech, specializing in AI/ML products.",
                            "work_experience_summary": "Led product teams at Fortune 500 companies, shipped 15+ products.",
                            "education_summary": "MBA from Stanford, BS Computer Science from MIT.",
                            "topics_of_interest": ["AI", "Product Management", "SaaS"],
                            "keywords": [
                                "product strategy",
                                "AI/ML",
                                "team leadership",
                            ],
                            "interests": ["mentoring", "public speaking"],
                            "notable_projects": "Launched AI chatbot with 1M+ users",
                            "confidence": 0.85,
                        },
                        "interactions_insight": {
                            "summary": "Active in product and AI communities, thoughtful commenter.",
                            "pain_points": [
                                "Scaling product teams efficiently",
                                "Integrating AI into existing workflows",
                            ],
                            "approach_angles": [
                                "{company_name}'s AI product training for teams",
                                "Upskilling programs for product managers",
                            ],
                            "engagement_style": "Thoughtful, shares insights, engages with technical content.",
                            "confidence": 0.78,
                        },
                        "outreach_messages": {
                            "summary": "Approach with focus on product team upskilling and AI integration.",
                            "languages": "English",
                            "post_comments": [
                                {
                                    "post_id": "post_id_001",
                                    "post_url": "https://www.linkedin.com/posts/john-doe_ai-product-innovation-activity-123456789",
                                    "comment": "Great insights John! At {company_name} we're seeing similar trends...",
                                }
                            ],
                            "linkedin_messages": {
                                "initial": "Hi John, loved your recent post about AI in product management...",
                                "follow_up_day3": "Following up on my previous message...",
                            },
                            "emails": {
                                "initial": {
                                    "subject": "AI Training for Your Product Team",
                                    "body_text": "Hi John, I noticed your work in AI-powered products...",
                                }
                            },
                            "triggers_posts": ["post_id_001"],
                            "triggers_reactions": ["reaction_id_001"],
                            "confidence": 0.82,
                        },
                    },
                    "phones": "Restricted access, please contact contact@idun-group.com to get access",
                    "emails": "Restricted access, please contact contact@idun-group.com to get access",
                    "raw_data": None,
                    "errors": [],
                }
            ]
        }
    }


class BatchInvokeRequest(BaseModel):
    """
    Batch request to analyze multiple LinkedIn lead profiles in one API call.

    Process up to 10 LinkedIn profiles simultaneously with the same configuration.
    Each profile is analyzed independently with full AI-powered insights.

    ⚠️ **Batch Limit**: Maximum 10 LinkedIn URLs per request.
    💡 **Need more?** Contact contact@idun-group.com to increase your batch limit.
    """

    # === REQUIRED FIELDS ===
    linkedin_urls: list[str] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Array of LinkedIn profile URLs to analyze (1-10 URLs). Each URL will be processed independently.",
        examples=[
            [
                "https://www.linkedin.com/in/john-doe/",
                "https://www.linkedin.com/in/jane-smith/",
            ]
        ],
    )

    # === DATA COLLECTION PARAMETERS (Applied to all profiles) ===
    posts_limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Number of recent LinkedIn posts to fetch per profile (1-100). Recommended: 10-25 for balanced analysis",
    )
    reactions_limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Number of recent LinkedIn reactions to analyze per profile (1-100). Recommended: 10-25 for engagement insights",
    )

    # === AI INSIGHTS GENERATION FLAGS (Applied to all profiles) ===
    get_profile_insight: bool = Field(
        default=True,
        description="Generate AI-powered profile analysis for each lead",
    )
    get_interactions_insight: bool = Field(
        default=True,
        description="Generate AI-powered interactions analysis for each lead",
    )
    get_outreach_messages: bool = Field(
        default=True,
        description="Generate AI-crafted outreach suggestions for each lead",
    )

    # === LANGUAGE CONFIGURATION (Applied to all profiles) ===
    insights_languages: SupportedLanguage = Field(
        default=SupportedLanguage.FRENCH,
        description="Language for generating profile and interactions insights. Default: French",
    )
    outreach_messages_languages: Optional[SupportedLanguage] = Field(
        default=None,
        description="Language for outreach messages. If not specified, auto-detects from each lead's profile.",
    )

    # === DATA OPTIONS (Applied to all profiles) ===
    get_raw_data: bool = Field(
        default=False,
        description="Include complete structured data in raw_data field for each profile. Default: false",
    )

    # === RESTRICTED FEATURES (Applied to all profiles) ===
    get_emails: bool = Field(
        default=False,
        description="Retrieve email addresses (⚠️ RESTRICTED: requires special access. Contact contact@idun-group.com)",
    )
    get_phones: bool = Field(
        default=False,
        description="Retrieve phone numbers (⚠️ RESTRICTED: requires special access. Contact contact@idun-group.com)",
    )

    # === AI PROCESSING MODE (Applied to all profiles) ===
    mode: ProcessingMode = Field(
        default=ProcessingMode.BALANCED,
        description="AI processing mode: 'fast' (lower quality, faster), 'balanced' (recommended), or 'pro' (highest quality, slower)",
    )

    @field_validator("linkedin_urls")
    @classmethod
    def validate_linkedin_urls(cls, v: list[str]) -> list[str]:
        """Validate all LinkedIn URLs in the batch"""
        if not v:
            raise ValueError("At least one LinkedIn URL is required")

        if len(v) > 10:
            raise ValueError(
                "Maximum 10 LinkedIn URLs allowed per batch request. "
                "Contact contact@idun-group.com to increase your batch limit."
            )

        # Validate each URL
        valid_patterns = [
            "linkedin.com/in/",
            "www.linkedin.com/in/",
            "https://linkedin.com/in/",
            "https://www.linkedin.com/in/",
        ]

        for i, url in enumerate(v):
            if not url:
                raise ValueError(f"LinkedIn URL at index {i} is empty")
            if not any(pattern in url.lower() for pattern in valid_patterns):
                raise ValueError(
                    f"Invalid LinkedIn URL at index {i}: {url}. "
                    "Expected format: https://www.linkedin.com/in/firstname-lastname-id/"
                )

        # Check for duplicates
        if len(v) != len(set(v)):
            raise ValueError("Duplicate LinkedIn URLs detected in batch request")

        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "linkedin_urls": [
                        "https://www.linkedin.com/in/john-doe/",
                        "https://www.linkedin.com/in/jane-smith/",
                        "https://www.linkedin.com/in/bob-johnson/",
                    ],
                    "posts_limit": 10,
                    "reactions_limit": 10,
                    "get_profile_insight": True,
                    "get_interactions_insight": True,
                    "get_outreach_messages": True,
                    "insights_languages": "French",
                    "outreach_messages_languages": "English",
                    "get_raw_data": False,
                    "mode": "balanced",
                }
            ]
        }
    }


class BatchInvokeResponse(BaseModel):
    """
    Batch response containing results for multiple LinkedIn lead analyses.

    Each result in the array corresponds to one LinkedIn URL from the request,
    in the same order. Failed analyses include error information.
    """

    batch_metadata: dict = Field(
        ...,
        description="Batch processing metadata: total_requested, total_completed, total_failed, started_at, duration_ms",
    )
    results: list[InvokeResponse] = Field(
        ...,
        description="Array of individual analysis results, one per LinkedIn URL in request order",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "batch_metadata": {
                        "total_requested": 3,
                        "total_completed": 3,
                        "total_failed": 0,
                        "started_at": "2025-10-19T12:34:56Z",
                        "duration_ms": 25000,
                    },
                    "results": [
                        {
                            "metadata": {
                                "version": "1.0.4",
                                "request_id": "req_batch_001",
                                "started_at": "2025-10-19T12:34:56Z",
                                "duration_ms": 8500,
                                "mode": "balanced",
                                "warnings": [],
                            },
                            "lead": {
                                "linkedin_url": "https://www.linkedin.com/in/john-doe/",
                                "full_name": "John Doe",
                            },
                            "insights": {},
                            "phones": "Restricted access",
                            "emails": "Restricted access",
                            "raw_data": None,
                            "errors": [],
                        }
                    ],
                }
            ]
        }
    }


class ErrorResponse(BaseModel):
    """Simple error response model for HTTP errors"""

    success: bool = Field(default=False)
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    version: str = Field(default="1.0.4")
