# Chloé API Models Documentation

## Overview

This directory contains all Pydantic models for the Chloé API v1.0.4.

## Structure

```
models/
├── __init__.py          # Package exports
├── models.py            # Core response schemas
├── invoke_models.py     # Request/Response models
└── README.md           # This file
```

## Model Hierarchy

### InvokeResponse (Root)
```
InvokeResponse
├── metadata: Metadata
│   ├── version: str
│   ├── request_id: str
│   ├── started_at: str (ISO-8601)
│   ├── duration_ms: int
│   ├── mode: ProcessingMode
│   └── warnings: list[str]
│
├── lead: Lead
│   ├── linkedin_url: str
│   ├── full_name: str?
│   ├── first_name: str?
│   ├── last_name: str?
│   ├── headline: str?
│   ├── current_title: str?
│   ├── current_company: str?
│   ├── location: Location?
│   │   ├── city: str?
│   │   ├── region: str?
│   │   └── country: str?
│   └── languages: list[str]
│
├── posts: list[Post]
│   └── Post
│       ├── id: str
│       ├── platform_post_id: str?
│       ├── url: str?
│       ├── created_at: str? (ISO-8601)
│       ├── post_type: PostType
│       ├── language: str? (BCP-47)
│       ├── text: str?
│       └── stats: PostStats
│           ├── reactions_total: int
│           ├── reactions_breakdown: ReactionsBreakdown
│           │   ├── like: int
│           │   ├── support: int
│           │   ├── love: int
│           │   ├── insightful: int
│           │   ├── celebrate: int
│           │   └── funny: int
│           ├── comments: int
│           └── reposts: int
│
├── reactions: list[Reaction]
│   └── Reaction
│       ├── id: str
│       ├── created_at: str? (ISO-8601)
│       ├── action: ReactionAction
│       ├── comment_text: str?
│       └── post: ReactionPost
│           ├── platform_post_id: str?
│           ├── url: str?
│           ├── post_type: PostType
│           ├── text_excerpt: str?
│           ├── author: PostAuthor?
│           │   ├── first_name: str?
│           │   ├── last_name: str?
│           │   ├── headline: str?
│           │   └── profile_url: str?
│           └── stats: PostStats
│
├── insights: Insights
│   ├── profile_insight: ProfileInsight?
│   │   ├── summary: str
│   │   ├── work_experience_summary: str?
│   │   ├── education_summary: str?
│   │   ├── topics_of_interest: list[str]
│   │   ├── keywords: list[str]
│   │   ├── interests: list[str]
│   │   ├── notable_projects: str?
│   │   └── confidence: float (0.0-1.0)
│   │
│   ├── interactions_insight: InteractionsInsight?
│   │   ├── summary: str
│   │   ├── pain_points: list[str]
│   │   ├── approach_angles: list[str]
│   │   ├── engagement_style: str?
│   │   └── confidence: float (0.0-1.0)
│   │
│   └── outreach_messages: OutreachMessages?
│       ├── summary: str
│       ├── languages: list[str] (BCP-47)
│       ├── post_comments: list[PostComment]
│       │   └── PostComment
│       │       ├── post_id: str
│       │       ├── post_url: str?
│       │       └── comment: str
│       ├── linkedin_messages: LinkedInMessages?
│       │   ├── initial: str
│       │   ├── follow_up_day3: str?
│       │   ├── follow_up_day7: str?
│       │   └── objection_response: str?
│       ├── emails: EmailSequence?
│       │   ├── initial: EmailMessage
│       │   ├── follow_up_day3: EmailMessage?
│       │   ├── follow_up_day7: EmailMessage?
│       │   └── objection_response: EmailMessage?
│       │       └── EmailMessage
│       │           ├── subject: str
│       │           ├── body_text: str
│       │           └── body_html: str?
│       ├── triggers_posts: list[str]
│       ├── triggers_reactions: list[str]
│       └── confidence: float (0.0-1.0)
│
├── raw_data: RawData?
│   ├── profile: dict?
│   ├── posts: list[dict]?
│   └── reactions: list[dict]?
│
└── errors: list[ResponseError]
    └── ResponseError
        ├── code: str
        ├── message: str
        └── details: dict?
```

## Enums

### ProcessingMode
```python
class ProcessingMode(str, Enum):
    FAST = "fast"         # Quick results, lower depth
    BALANCED = "balanced" # Balanced precision (default)
    PRO = "pro"           # Deeper context & analysis
```

### PostType
```python
class PostType(str, Enum):
    REGULAR = "regular"   # Standard post
    REPOST = "repost"     # Shared post
    QUOTE = "quote"       # Quote post
    ARTICLE = "article"   # Article/long-form
```

### ReactionAction
```python
class ReactionAction(str, Enum):
    LIKE = "like"
    SUPPORT = "support"
    LOVE = "love"
    INSIGHTFUL = "insightful"
    CELEBRATE = "celebrate"
    FUNNY = "funny"
    COMMENT = "comment"
```

## Usage Examples

### Importing Models

```python
from app.models import (
    InvokeRequest,
    InvokeResponse,
    Metadata,
    Lead,
    Post,
    Reaction,
    Insights,
    ProfileInsight,
    OutreachMessages,
)
```

### Creating a Response

```python
from app.models import InvokeResponse, Metadata, Lead, Insights
from app.models.models import ProcessingMode

response = InvokeResponse(
    metadata=Metadata(
        version="1.0.4",
        request_id="req_abc123_456",
        started_at="2025-10-19T12:00:00Z",
        duration_ms=1500,
        mode=ProcessingMode.BALANCED,
        warnings=[]
    ),
    lead=Lead(
        linkedin_url="https://www.linkedin.com/in/john-doe/",
        full_name="John Doe",
        first_name="John",
        last_name="Doe"
    ),
    posts=[],
    reactions=[],
    insights=Insights(),
    raw_data=None,
    errors=[]
)
```

## Field Conventions

1. **Optional Fields**: Marked with `?` or `Optional[T]`
2. **Timestamps**: ISO-8601 UTC format (e.g., `2025-10-19T12:34:56Z`)
3. **Languages**: BCP-47 codes (e.g., `["en", "fr"]`)
4. **IDs**: String format with prefixes (e.g., `post_local_1`, `req_abc_123`)
5. **Confidence**: Float between 0.0 and 1.0
6. **Enums**: Lowercase string values

## Validation

All models include Pydantic validation:
- Type checking
- Required field enforcement
- Range validation (e.g., confidence 0.0-1.0)
- Custom validators (e.g., LinkedIn URL format)

## Documentation

- See `SCHEMA_GUIDE.md` for detailed field documentation
- See `IMPLEMENTATION_SUMMARY.md` for implementation details
- API docs available at `/docs` when running the server

---

**Models Version:** 1.0.4  
**Last Updated:** 2025-10-19

