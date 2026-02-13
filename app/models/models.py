"""
Pydantic models for Chloé API response schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from enum import Enum


# ============================================
# Enums
# ============================================


class ProcessingMode(str, Enum):
    """
    AI processing mode options - controls quality vs speed trade-off.

    - **fast**: Quick analysis with lower quality (~3-5s)
    - **balanced**: Recommended balance of quality and speed (~8-12s)
    - **pro**: Highest quality insights with slower processing (~15-30s)
    """

    FAST = "fast"
    BALANCED = "balanced"
    PRO = "pro"


# ============================================
# Metadata
# ============================================


class Metadata(BaseModel):
    """
    Response metadata containing execution details and status information.

    Includes version, unique request ID for tracing, timing information,
    processing mode used, and any non-fatal warnings encountered.
    """

    version: str = Field(
        default="1.0.4",
        description="API version that processed this request",
    )
    request_id: str = Field(
        ...,
        description="Server-generated unique ID for request tracing and support",
    )
    started_at: str = Field(
        ...,
        description="Request start timestamp in ISO-8601 UTC format (e.g., 2025-10-19T12:34:56Z)",
    )
    duration_ms: int = Field(
        ...,
        description="Total processing time in milliseconds from start to completion",
    )
    mode: ProcessingMode = Field(
        ...,
        description="AI processing mode used for this request (fast/balanced/pro)",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Non-fatal issues encountered (e.g., 'Only 3 posts found', 'No language detected'). Empty array if no warnings.",
    )


# ============================================
# Lead Information
# ============================================


class Lead(BaseModel):
    """
    Structured lead profile information extracted from LinkedIn.

    Contains core identifying information and professional details about the lead,
    extracted and normalized from their LinkedIn profile.
    """

    linkedin_url: str = Field(
        ...,
        description="Validated LinkedIn profile URL of the lead",
    )
    full_name: Optional[str] = Field(
        None,
        description="Lead's full display name (e.g., 'John Doe')",
    )
    first_name: Optional[str] = Field(
        None,
        description="Lead's first/given name (e.g., 'John')",
    )
    last_name: Optional[str] = Field(
        None,
        description="Lead's last/family name (e.g., 'Doe')",
    )
    headline: Optional[str] = Field(
        None,
        description="LinkedIn headline/tagline (e.g., 'Head of Product at Acme Corp | AI Enthusiast')",
    )
    current_title: Optional[str] = Field(
        None,
        description="Current job title extracted from most recent experience (e.g., 'Head of Product')",
    )
    current_company: Optional[str] = Field(
        None,
        description="Current employer extracted from most recent experience (e.g., 'Acme Corp')",
    )
    location: Optional[str] = Field(
        None,
        description="Geographic location in format: City, Region, Country (e.g., 'Paris, Île-de-France, France')",
    )
    languages: Optional[str] = Field(
        None,
        description="Primary language detected from profile or specified by user for outreach (e.g., 'English', 'French')",
    )


class Experience(BaseModel):
    """Experience information"""

    title: Optional[str] = Field(None, description="Job title")
    company: Optional[str] = Field(None, description="Company name")
    location: Optional[str] = Field(
        None, description="Location (city, region, country)"
    )
    duration: Optional[str] = Field(None, description="Duration of the experience")
    description: Optional[str] = Field(None, description="Job description")
    employment_type: Optional[str] = Field(
        None,
        description="Employment type (full-time, part-time, freelance, internship)",
    )
    location_type: Optional[str] = Field(
        None, description="Location type (remote, on-site, hybrid)"
    )
    skills: Optional[str] = Field(None, description="Skills")
    is_current: Optional[bool] = Field(
        None, description="Whether the experience is current"
    )


class Education(BaseModel):
    """Education information"""

    school: Optional[str] = Field(None, description="School name")
    degree: Optional[str] = Field(None, description="Degree")
    degree_name: Optional[str] = Field(None, description="Degree name")
    field_of_study: Optional[str] = Field(None, description="Field of study")
    duration: Optional[str] = Field(None, description="Duration of the education")
    description: Optional[str] = Field(None, description="Education description")


class Certification(BaseModel):
    """Certification information"""

    name: Optional[str] = Field(None, description="Certification name")
    issuer: Optional[str] = Field(None, description="Issuing organization")
    issued_date: Optional[str] = Field(None, description="Issued date (ISO-8601 UTC)")


# ============================================
# Posts & Reactions
# ============================================
class PostAuthor(BaseModel):
    """Author information for a post"""

    first_name: Optional[str] = Field(None, description="Author's first name")
    last_name: Optional[str] = Field(None, description="Author's last name")
    headline: Optional[str] = Field(None, description="Author's headline")


class Post(BaseModel):
    """LinkedIn post authored by the lead"""

    id: str = Field(..., description="Stable local identifier")
    url: Optional[str] = Field(None, description="Public post URL")
    posted_at: Optional[str] = Field(None, description="Post datetime (ISO-8601 UTC)")
    post_type: Optional[str] = Field(None, description="Type of post")
    author: Optional[PostAuthor] = Field(None, description="Post author information")
    text: Optional[str] = Field(None, description="Post text content (sanitized)")
    stats: Optional[str] = Field(
        default="",
        description="Engagement statistics (reactions_total, reactions_breakdown, comments, reposts)",
    )


class Reaction(BaseModel):
    """Lead's interaction on another user's post"""

    id: str = Field(..., description="Stable local identifier")
    action: Optional[str] = Field(None, description="Type of reaction")
    reacted_at: Optional[str] = Field(
        None, description="When the reaction occurred (ISO-8601 UTC)"
    )
    post_text: Optional[str] = Field(
        None, description="Text of the post the reaction was made on"
    )
    post_author: Optional[PostAuthor] = Field(
        None, description="Author of the post the reaction was made on"
    )
    post_url: Optional[str] = Field(
        None, description="URL of the post the reaction was made on"
    )


# ============================================
# Insights (AI-Generated)
# ============================================


class ProfileInsight(BaseModel):
    """AI-generated profile insight"""

    summary: str = Field(..., description="1-3 sentence synopsis")
    work_experience_summary: Optional[str] = Field(
        None, description="Condensed highlights of roles"
    )
    education_summary: Optional[str] = Field(
        None, description="Degrees/certifications summary"
    )
    topics_of_interest: list[str] = Field(
        default_factory=list, description="Thematic areas"
    )
    keywords: list[str] = Field(
        default_factory=list, description="Searchable skills/tags"
    )
    interests: list[str] = Field(
        default_factory=list, description="Personal/professional interests"
    )
    notable_projects: Optional[str] = Field(
        None, description="Key projects if inferable"
    )
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")


class InteractionsInsight(BaseModel):
    """AI-generated interactions insight"""

    summary: str = Field(..., description="Behavioral overview")
    pain_points: list[str] = Field(
        default_factory=list, description="Problems inferred from interactions"
    )
    approach_angles: list[str] = Field(
        default_factory=list, description="Recommended positioning angles"
    )
    engagement_style: Optional[str] = Field(
        None, description="Typical interaction pattern"
    )
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")


class PostComment(BaseModel):
    """Ready-to-post comment suggestion"""

    post_id: str = Field(..., description="Reference to post ID")
    post_url: Optional[str] = Field(
        None, description="Post URL, fill the url of the related referenced post"
    )
    comment: str = Field(..., description="Suggested comment text")


class LinkedInMessages(BaseModel):
    """LinkedIn direct message sequence"""

    initial: str = Field(..., description="Initial outreach message")
    follow_up_day3: Optional[str] = Field(None, description="Follow-up after 3 days")
    follow_up_day7: Optional[str] = Field(None, description="Follow-up after 7 days")
    objection_response: Optional[str] = Field(
        None, description="Response to common objections"
    )


class EmailMessage(BaseModel):
    """Email message template"""

    subject: str = Field(..., description="Email subject line")
    body_text: str = Field(..., description="Plain text email body")
    body_html: Optional[str] = Field(None, description="HTML email body")
    html: Optional[str] = Field(
        default="Restricted: Get a SSR-Rendered HTML Email with your template by contacting contact@idun-group.com",
        description="SSR-Rendered HTML Email",
    )


class EmailSequence(BaseModel):
    """Email outreach sequence"""

    initial: EmailMessage = Field(..., description="Initial email")
    follow_up_day3: Optional[EmailMessage] = Field(
        None, description="Follow-up after 3 days"
    )
    follow_up_day7: Optional[EmailMessage] = Field(
        None, description="Follow-up after 7 days"
    )
    objection_response: Optional[EmailMessage] = Field(
        None, description="Response to objections"
    )


class OutreachMessages(BaseModel):
    """AI-generated outreach suggestions"""

    summary: str = Field(..., description="How to approach this lead effectively")
    languages: Optional[str] = Field(None, description="Generation language(s) BCP-47")
    post_comments: list[PostComment] = Field(
        default_factory=list, description="Ready-to-post comments"
    )
    linkedin_messages: Optional[LinkedInMessages] = Field(
        None, description="Direct message sequence"
    )
    emails: Optional[EmailSequence] = Field(None, description="Email sequence")
    triggers_posts: list[str] = Field(
        default_factory=list, description="Post IDs worth engaging on"
    )
    triggers_reactions: list[str] = Field(
        default_factory=list, description="Reaction IDs indicating timing/interest"
    )
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")


class Insights(BaseModel):
    """
    Complete bundle of AI-generated insights from the Chloé Sales Agent.

    Contains three types of AI analysis:
    - **Profile Insight**: Who the lead is (background, interests, expertise)
    - **Interactions Insight**: How the lead behaves (engagement patterns, pain points)
    - **Outreach Messages**: What to say (personalized messages, emails, comments)

    Each insight is optional and only generated if the corresponding flag is enabled in the request.
    """

    profile_insight: Optional[ProfileInsight] = Field(
        None,
        description="AI-generated profile analysis: summary, work experience, education, topics of interest, keywords, notable projects. Null if not requested or generation failed.",
    )
    interactions_insight: Optional[InteractionsInsight] = Field(
        None,
        description="AI-generated interactions analysis: engagement style, pain points, approach angles based on LinkedIn activity. Null if not requested or generation failed.",
    )
    outreach_messages: Optional[OutreachMessages] = Field(
        None,
        description="AI-generated outreach content: personalized post comments, LinkedIn DM sequences, email templates. Null if not requested or generation failed.",
    )


# ============================================
# Raw Data
# ============================================


class RawData(BaseModel):
    """Verbatim data payloads"""

    lead: Optional[Lead] = Field(None, description="Verbatim profile payload")
    experiences: Optional[list[Experience]] = Field(
        None, description="Verbatim experiences payloads"
    )
    educations: Optional[list[Education]] = Field(
        None, description="Verbatim educations payloads"
    )
    certifications: Optional[list[Certification]] = Field(
        None, description="Verbatim certifications payloads"
    )
    posts: Optional[list[Post]] = Field(None, description="Verbatim posts payloads")
    reactions: Optional[list[Reaction]] = Field(
        None, description="Verbatim reactions payloads"
    )


# ============================================
# Errors
# ============================================


class ResponseError(BaseModel):
    """Error information"""

    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable summary")
    details: Optional[Dict[str, Any]] = Field(None, description="Extra context")
