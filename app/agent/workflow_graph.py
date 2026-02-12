from asyncio import Semaphore
from datetime import datetime

from langchain_apify import ApifyActorsTool
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, StateGraph

from app.agent.graph_state import ChloeState
from app.agent.le_wagon_context import LE_WAGON_CONTEXT
from app.agent.prompts import (
    INTERACTIONS_INSIGHT_PROMPT,
    OUTREACH_MESSAGES_PROMPT,
    PROFILE_INSIGHT_PROMPT,
    format_certifications_for_prompt,
    format_educations_for_prompt,
    format_experiences_for_prompt,
    format_posts_for_comments,
    format_posts_for_prompt,
    format_reactions_for_prompt,
)
from app.agent.utils import (
    clean_raw_data,
    define_llm,
    invoke_with_structured_output_retry,
    transform_posts_raw_to_posts,
    transform_profile_raw_to_certifications,
    transform_profile_raw_to_educations,
    transform_profile_raw_to_experiences,
    transform_profile_raw_to_lead,
    transform_reactions_raw_to_reactions,
)
from app.config import get_settings
from app.logging import LogEmoji, get_logger
from app.models.models import InteractionsInsight, OutreachMessages, ProfileInsight

logger = get_logger("agent.workflow_graph")

# Semaphore for controlling concurrent LLM calls
MAX_CONCURRENCY = 30
llm_semaphore: Semaphore = Semaphore(MAX_CONCURRENCY)

linkedin_profile_detail = ApifyActorsTool(actor_id="apimaestro/linkedin-profile-detail")
linkedin_profile_posts = ApifyActorsTool(actor_id="apimaestro/linkedin-profile-posts")
linkedin_profile_reactions = ApifyActorsTool(
    actor_id="apimaestro/linkedin-profile-reactions"
)
settings = get_settings()


async def init_agent(state: ChloeState, config: RunnableConfig):
    logger.info("Initializing agent...")
    logger.info(f"Input state keys: {list(state.keys()) if state else 'Empty state'}")
    logger.info(f"Input config: {config}")

    output_state = {
        "date_now": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "warnings": [],  # Initialize warnings list
    }
    return output_state


async def get_linkedin_profile(state: ChloeState, config: RunnableConfig):
    logger.info("Getting LinkedIn profile...")
    # Create a new warnings list for this node (operator.add will combine with others)
    node_warnings = []

    profile_input = {
        "run_input": {
            "username": state["invoke_request"].linkedin_url,
            "includeEmail": False,
        }
    }
    linkedin_profile_raw_data = await linkedin_profile_detail.ainvoke(profile_input)
    linkedin_profile_raw_data_clean = clean_raw_data(linkedin_profile_raw_data)
    lead = transform_profile_raw_to_lead(
        linkedin_profile_raw_data_clean, state["invoke_request"].linkedin_url
    )
    experiences = transform_profile_raw_to_experiences(linkedin_profile_raw_data_clean)
    educations = transform_profile_raw_to_educations(linkedin_profile_raw_data_clean)

    # Check for missing or limited profile data
    if not experiences or len(experiences) == 0:
        warning_msg = "No professional experience found in LinkedIn profile. Profile insight may be limited."
        node_warnings.append(warning_msg)
        logger.warning(f"{LogEmoji.WARNING} {warning_msg}")

    if not educations or len(educations) == 0:
        warning_msg = "No education information found in LinkedIn profile."
        node_warnings.append(warning_msg)
        logger.warning(f"{LogEmoji.WARNING} {warning_msg}")

    # Override lead preferred languages if forced by the user for outreach messages
    # Note: This is stored in lead.languages for use by outreach messages generation
    # If user specifies outreach_messages_languages, we'll use that; otherwise use detected language
    language_was_overridden = False
    if state["invoke_request"].outreach_messages_languages:
        lead.languages = state["invoke_request"].outreach_messages_languages.value
        language_was_overridden = True
    # If no override and no detected language, default to French
    elif not lead.languages:
        lead.languages = "French"
        warning_msg = "No preferred language detected from profile. Defaulting outreach language to French."
        node_warnings.append(warning_msg)
        logger.warning(f"{LogEmoji.WARNING} {warning_msg}")

    certifications = transform_profile_raw_to_certifications(
        linkedin_profile_raw_data_clean
    )

    if not certifications or len(certifications) == 0:
        logger.info(
            f"{LogEmoji.INFO} No certifications found in LinkedIn profile (this is optional)."
        )

    output_state = {
        "linkedin_profile_raw_data": linkedin_profile_raw_data_clean,
        "lead": lead,
        "experiences": experiences,
        "educations": educations,
        "certifications": certifications,
        "warnings": node_warnings,  # Return this node's warnings only
    }
    return output_state


async def get_linkedin_posts(state: ChloeState, config: RunnableConfig):
    logger.info("Getting LinkedIn posts...")
    # Create a new warnings list for this node (operator.add will combine with others)
    node_warnings = []

    posts_input = {
        "run_input": {
            "username": state["invoke_request"].linkedin_url,
            "page_number": 1,
            "limit": state["invoke_request"].posts_limit,
            "total_posts": state["invoke_request"].posts_limit,
        }
    }
    linkedin_posts_raw_data = await linkedin_profile_posts.ainvoke(posts_input)
    linkedin_posts_raw_data_clean = clean_raw_data(linkedin_posts_raw_data)
    posts = transform_posts_raw_to_posts(linkedin_posts_raw_data_clean)

    # Check for missing or limited posts
    if not posts or len(posts) == 0:
        warning_msg = "No LinkedIn posts found for this profile. Interactions insight and post comments will be limited."
        node_warnings.append(warning_msg)
        logger.warning(f"{LogEmoji.WARNING} {warning_msg}")
    elif len(posts) < state["invoke_request"].posts_limit:
        warning_msg = f"Only {len(posts)} posts found (requested {state['invoke_request'].posts_limit}). Lead may have limited posting activity."
        node_warnings.append(warning_msg)
        logger.warning(f"{LogEmoji.WARNING} {warning_msg}")

    output_state = {
        "linkedin_posts_raw_data": linkedin_posts_raw_data_clean,
        "posts": posts,
        "warnings": node_warnings,  # Return this node's warnings only
    }
    return output_state


async def get_linkedin_reactions(state: ChloeState, config: RunnableConfig):
    logger.info("Getting LinkedIn reactions...")
    # Create a new warnings list for this node (operator.add will combine with others)
    node_warnings = []

    reactions_input = {
        "run_input": {
            "username": state["invoke_request"].linkedin_url,
            "page_number": 1,
            "limit": state["invoke_request"].reactions_limit,
            "total_reactions": state["invoke_request"].reactions_limit,
        }
    }
    linkedin_reactions_raw_data = await linkedin_profile_reactions.ainvoke(
        reactions_input
    )
    linkedin_reactions_raw_data_clean = clean_raw_data(linkedin_reactions_raw_data)
    reactions = transform_reactions_raw_to_reactions(linkedin_reactions_raw_data_clean)

    # Check for missing or limited reactions
    if not reactions or len(reactions) == 0:
        warning_msg = "No LinkedIn reactions found for this profile. Interactions insight will be based solely on posts."
        node_warnings.append(warning_msg)
        logger.warning(f"{LogEmoji.WARNING} {warning_msg}")
    elif len(reactions) < state["invoke_request"].reactions_limit:
        warning_msg = f"Only {len(reactions)} reactions found (requested {state['invoke_request'].reactions_limit}). Lead may have limited engagement activity."
        node_warnings.append(warning_msg)
        logger.warning(f"{LogEmoji.WARNING} {warning_msg}")

    output_state = {
        "linkedin_reactions_raw_data": linkedin_reactions_raw_data_clean,
        "reactions": reactions,
        "warnings": node_warnings,  # Return this node's warnings only
    }
    return output_state


async def intermediate_node(state: ChloeState, config: RunnableConfig):
    """Intermediate node - marks completion of data collection phase"""
    logger.info(
        f"{LogEmoji.SUCCESS} Data collection phase completed, proceeding to insights generation"
    )
    return state


# ============================================
# AI Insight Generation Nodes
# ============================================


async def generate_profile_insight(state: ChloeState, config: RunnableConfig):
    """Generate AI-powered profile insight using LLM with structured output"""
    logger.info(f"{LogEmoji.AI_THINKING} Generating profile insight...")

    # Check if profile insight generation is enabled
    if not state["invoke_request"].get_profile_insight:
        logger.info(f"{LogEmoji.INFO} Profile insight generation disabled, skipping")
        return {"profile_insight": None}

    try:
        # Get lead and profile data
        lead = state.get("lead")
        experiences = state.get("experiences", [])
        educations = state.get("educations", [])
        certifications = state.get("certifications", [])
        date_now = state.get("date_now", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        # Format data for prompt
        experiences_summary = format_experiences_for_prompt(experiences)
        educations_summary = format_educations_for_prompt(educations)
        certifications_summary = format_certifications_for_prompt(certifications)

        # Get insights language from request
        insights_languages = state["invoke_request"].insights_languages.value

        # Build prompt
        prompt = PROFILE_INSIGHT_PROMPT.format(
            le_wagon_context=LE_WAGON_CONTEXT,
            insights_languages=insights_languages,
            date_now=date_now,
            full_name=lead.full_name or "Unknown",
            headline=lead.headline or "N/A",
            current_title=lead.current_title or "N/A",
            current_company=lead.current_company or "N/A",
            location=lead.location or "N/A",
            languages=lead.languages or "N/A",
            experiences_summary=experiences_summary,
            educations_summary=educations_summary,
            certifications_summary=certifications_summary,
        )

        # Initialize LLM
        mode = state["invoke_request"].mode
        llm = define_llm()

        # Get langfuse handler from config if available
        callbacks = []
        if config and config.get("callbacks"):
            callbacks = config["callbacks"]

        # Generate insight with retry logic using semaphore for concurrency control
        logger.info(f"{LogEmoji.AI_THINKING} Invoking LLM for profile insight...")
        async with llm_semaphore:
            profile_insight = await invoke_with_structured_output_retry(
                llm=llm,
                prompt=prompt,
                schema_class=ProfileInsight,
                config={"callbacks": callbacks},
                max_retries=2,
            )

        if profile_insight:
            logger.info(f"{LogEmoji.SUCCESS} Profile insight generated successfully")
            logger.debug(f"{LogEmoji.INFO} Confidence: {profile_insight.confidence}")
            return {"profile_insight": profile_insight}
        else:
            logger.error(
                f"{LogEmoji.ERROR} Failed to generate profile insight after retries"
            )
            # Create a new warnings list for this node
            node_warnings = [
                "Failed to generate profile insight after multiple attempts. Profile analysis unavailable."
            ]
            return {"profile_insight": None, "warnings": node_warnings}

    except Exception as e:
        logger.error(f"{LogEmoji.ERROR} Failed to generate profile insight: {e}")
        # Create a new warnings list for this node
        node_warnings = [f"Error generating profile insight: {str(e)[:100]}"]
        return {"profile_insight": None, "warnings": node_warnings}


async def generate_interactions_insight(state: ChloeState, config: RunnableConfig):
    """Generate AI-powered interactions insight using LLM with structured output"""
    logger.info(f"{LogEmoji.AI_THINKING} Generating interactions insight...")

    # Check if interactions insight generation is enabled
    if not state["invoke_request"].get_interactions_insight:
        logger.info(
            f"{LogEmoji.INFO} Interactions insight generation disabled, skipping"
        )
        return {"interactions_insight": None}

    try:
        # Get lead and activity data
        lead = state.get("lead")
        posts = state.get("posts", [])
        reactions = state.get("reactions", [])
        date_now = state.get("date_now", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        # Create a new warnings list for this node
        node_warnings = []

        # Warn if both posts and reactions are empty
        if (not posts or len(posts) == 0) and (not reactions or len(reactions) == 0):
            warning_msg = "No posts or reactions available. Interactions insight will be very limited or generic."
            node_warnings.append(warning_msg)
            logger.warning(f"{LogEmoji.WARNING} {warning_msg}")

        # Format data for prompt
        posts_summary = format_posts_for_prompt(posts, limit=10)
        reactions_summary = format_reactions_for_prompt(reactions, limit=20)

        # Get insights language from request
        insights_languages = state["invoke_request"].insights_languages.value

        # Build prompt
        prompt = INTERACTIONS_INSIGHT_PROMPT.format(
            le_wagon_context=LE_WAGON_CONTEXT,
            insights_languages=insights_languages,
            date_now=date_now,
            full_name=lead.full_name or "Unknown",
            current_title=lead.current_title or "N/A",
            current_company=lead.current_company or "N/A",
            posts_count=len(posts),
            posts_summary=posts_summary,
            reactions_count=len(reactions),
            reactions_summary=reactions_summary,
        )

        # Initialize LLM
        mode = state["invoke_request"].mode
        llm = define_llm()

        # Get langfuse handler from config if available
        callbacks = []
        if config and config.get("callbacks"):
            callbacks = config["callbacks"]

        # Generate insight with retry logic using semaphore for concurrency control
        logger.info(f"{LogEmoji.AI_THINKING} Invoking LLM for interactions insight...")
        async with llm_semaphore:
            interactions_insight = await invoke_with_structured_output_retry(
                llm=llm,
                prompt=prompt,
                schema_class=InteractionsInsight,
                config={"callbacks": callbacks},
                max_retries=2,
            )

        if interactions_insight:
            logger.info(
                f"{LogEmoji.SUCCESS} Interactions insight generated successfully"
            )
            logger.debug(
                f"{LogEmoji.INFO} Confidence: {interactions_insight.confidence}"
            )
            return {
                "interactions_insight": interactions_insight,
                "warnings": node_warnings,
            }
        else:
            logger.error(
                f"{LogEmoji.ERROR} Failed to generate interactions insight after retries"
            )
            node_warnings.append(
                "Failed to generate interactions insight after multiple attempts. Engagement analysis unavailable."
            )
            return {"interactions_insight": None, "warnings": node_warnings}

    except Exception as e:
        logger.error(f"{LogEmoji.ERROR} Failed to generate interactions insight: {e}")
        # Create a new warnings list for this node
        node_warnings = [f"Error generating interactions insight: {str(e)[:100]}"]
        return {"interactions_insight": None, "warnings": node_warnings}


async def generate_outreach_messages(state: ChloeState, config: RunnableConfig):
    """Generate AI-powered outreach messages using LLM with structured output"""
    logger.info(f"{LogEmoji.AI_THINKING} Generating outreach messages...")

    # Check if outreach messages generation is enabled
    if not state["invoke_request"].get_outreach_messages:
        logger.info(f"{LogEmoji.INFO} Outreach messages generation disabled, skipping")
        return {"outreach_messages": None}

    try:
        # Get lead and insight data
        lead = state.get("lead")
        posts = state.get("posts", [])
        profile_insight = state.get("profile_insight")
        interactions_insight = state.get("interactions_insight")
        date_now = state.get("date_now", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        # Create a new warnings list for this node
        node_warnings = []

        # Warn if key insights are missing
        if not profile_insight:
            warning_msg = (
                "Profile insight unavailable. Outreach personalization will be limited."
            )
            # node_warnings.append(warning_msg)
            logger.warning(f"{LogEmoji.WARNING} {warning_msg}")

        if not interactions_insight:
            warning_msg = "Interactions insight unavailable. Outreach will lack engagement-based personalization."
            # node_warnings.append(warning_msg)
            logger.warning(f"{LogEmoji.WARNING} {warning_msg}")

        if not posts or len(posts) == 0:
            warning_msg = "No posts available for commenting. Post comment suggestions will be empty."
            node_warnings.append(warning_msg)
            logger.warning(f"{LogEmoji.WARNING} {warning_msg}")

        # Format data for prompt
        recent_posts_for_comments = format_posts_for_comments(posts, limit=10)

        # Prepare insight summaries
        profile_insight_summary = (
            profile_insight.summary
            if profile_insight
            else "No profile insight available"
        )
        interactions_insight_summary = (
            interactions_insight.summary
            if interactions_insight
            else "No interactions insight available"
        )

        # Get outreach messages language (already set in lead.languages during profile node)
        outreach_messages_languages = lead.languages or "French"

        logger.info(
            f"{LogEmoji.INFO} Using outreach language: {outreach_messages_languages}"
        )

        # Build prompt
        prompt = OUTREACH_MESSAGES_PROMPT.format(
            le_wagon_context=LE_WAGON_CONTEXT,
            date_now=date_now,
            full_name=lead.full_name or "Unknown",
            first_name=lead.first_name or "Unknown",
            current_title=lead.current_title or "N/A",
            current_company=lead.current_company or "N/A",
            languages=lead.languages or "French",
            outreach_messages_languages=outreach_messages_languages,
            profile_insight_summary=profile_insight_summary,
            interactions_insight_summary=interactions_insight_summary,
            recent_posts_for_comments=recent_posts_for_comments,
        )

        # Initialize LLM
        mode = state["invoke_request"].mode
        llm = define_llm()

        # Get langfuse handler from config if available
        callbacks = []
        if config and config.get("callbacks"):
            callbacks = config["callbacks"]

        # Generate outreach messages with retry logic using semaphore for concurrency control
        logger.info(f"{LogEmoji.AI_THINKING} Invoking LLM for outreach messages...")
        async with llm_semaphore:
            outreach_messages = await invoke_with_structured_output_retry(
                llm=llm,
                prompt=prompt,
                schema_class=OutreachMessages,
                config={"callbacks": callbacks},
                max_retries=2,
            )

        if outreach_messages:
            logger.info(f"{LogEmoji.SUCCESS} Outreach messages generated successfully")
            logger.debug(f"{LogEmoji.INFO} Confidence: {outreach_messages.confidence}")
            logger.debug(
                f"{LogEmoji.INFO} Generated {len(outreach_messages.post_comments)} post comments"
            )
            return {"outreach_messages": outreach_messages, "warnings": node_warnings}
        else:
            logger.error(
                f"{LogEmoji.ERROR} Failed to generate outreach messages after retries"
            )
            node_warnings.append(
                "Failed to generate outreach messages after multiple attempts. No outreach suggestions available."
            )
            return {"outreach_messages": None, "warnings": node_warnings}

    except Exception as e:
        logger.error(f"{LogEmoji.ERROR} Failed to generate outreach messages: {e}")
        # Create a new warnings list for this node
        node_warnings = [f"Error generating outreach messages: {str(e)[:100]}"]
        return {"outreach_messages": None, "warnings": node_warnings}


async def final_node(state: ChloeState, config: RunnableConfig):
    logger.info(f"{LogEmoji.SUCCESS} Final node - workflow completed")
    return state


# ============================================
# Build LangGraph Workflow
# ============================================


def build_chloe_graph(checkpointer=None):
    """
    Build and compile the Chloé agent workflow graph.

    Graph structure:
    1. init_agent (entry point)
    2. get_linkedin_profile, get_linkedin_posts, get_linkedin_reactions (parallel data collection)
    3. intermediate_node (sync point)
    4. generate_profile_insight, generate_interactions_insight, generate_outreach_messages (parallel AI generation)
    5. final_node (completion)
    6. END

    Args:
        checkpointer: Optional checkpointer for persistence (e.g., PostgresSaver)

    Returns:
        Compiled StateGraph
    """
    logger.info(f"{LogEmoji.STARTUP} Building Chloé workflow graph...")

    # Initialize StateGraph with ChloeState
    workflow = StateGraph(ChloeState)

    # Add all nodes
    workflow.add_node("init_agent", init_agent)
    workflow.add_node("get_linkedin_profile", get_linkedin_profile)
    workflow.add_node("get_linkedin_posts", get_linkedin_posts)
    workflow.add_node("get_linkedin_reactions", get_linkedin_reactions)
    workflow.add_node("intermediate_node", intermediate_node)
    workflow.add_node("generate_profile_insight", generate_profile_insight)
    workflow.add_node("generate_interactions_insight", generate_interactions_insight)
    workflow.add_node("generate_outreach_messages", generate_outreach_messages)
    workflow.add_node("final_node", final_node)

    # Set entry point
    workflow.set_entry_point("init_agent")

    # Phase 1: Data Collection (parallel)
    # From init_agent to three parallel data collection nodes
    workflow.add_edge("init_agent", "get_linkedin_profile")
    workflow.add_edge("init_agent", "get_linkedin_posts")
    workflow.add_edge("init_agent", "get_linkedin_reactions")

    # All data collection nodes converge to intermediate_node
    workflow.add_edge("get_linkedin_profile", "intermediate_node")
    workflow.add_edge("get_linkedin_posts", "intermediate_node")
    workflow.add_edge("get_linkedin_reactions", "intermediate_node")

    # Phase 2: AI Insight Generation (parallel)
    # From intermediate_node to three parallel AI generation nodes
    workflow.add_edge("intermediate_node", "generate_profile_insight")
    workflow.add_edge("intermediate_node", "generate_interactions_insight")
    workflow.add_edge("intermediate_node", "generate_outreach_messages")

    # All AI generation nodes converge to final_node
    workflow.add_edge("generate_profile_insight", "final_node")
    workflow.add_edge("generate_interactions_insight", "final_node")
    workflow.add_edge("generate_outreach_messages", "final_node")

    # Final node to END
    workflow.add_edge("final_node", END)

    # Compile the graph with checkpointer if provided
    logger.info(f"{LogEmoji.SUCCESS} Chloé workflow graph compiled successfully")
    logger.info(
        f"{LogEmoji.INFO} Graph structure: init → [profile, posts, reactions] → intermediate → [profile_insight, interactions_insight, outreach] → final → END"
    )

    return workflow


app = build_chloe_graph()
