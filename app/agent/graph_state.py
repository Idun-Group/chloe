import operator
from typing import Annotated
from langgraph.graph import MessagesState
from app.models.invoke_models import InvokeRequest
from app.models.invoke_models import InvokeResponse
from app.models.models import (
    Lead,
    Experience,
    Education,
    Certification,
    Post,
    Reaction,
    ProfileInsight,
    InteractionsInsight,
    OutreachMessages,
)


class ChloeState(MessagesState):

    invoke_request: InvokeRequest
    invoke_response: InvokeResponse

    # Model data
    lead: Lead
    experiences: list[Experience]
    educations: list[Education]
    certifications: list[Certification]
    posts: list[Post]
    reactions: list[Reaction]

    # AI-generated insights
    profile_insight: ProfileInsight
    interactions_insight: InteractionsInsight
    outreach_messages: OutreachMessages

    # Raw data
    linkedin_profile_raw_data: dict
    linkedin_posts_raw_data: dict
    linkedin_reactions_raw_data: dict

    # Utils
    date_now: str
    # Use operator.add to handle concurrent updates from parallel nodes
    # This will append all warning lists together automatically
    warnings: Annotated[list[str], operator.add]
