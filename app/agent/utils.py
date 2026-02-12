from app.models.models import (
    Lead,
    Experience,
    Education,
    Certification,
    Post,
    PostAuthor,
    Reaction,
)
from app.config import get_settings, LLMProvider
import json
from typing import Dict, Any, List, Optional, Type, TypeVar
from pydantic import BaseModel
from langchain_core.exceptions import OutputParserException
from langchain_core.language_models.chat_models import BaseChatModel

from app.logging import get_logger, LogEmoji

T = TypeVar("T", bound=BaseModel)

logger = get_logger("agent.utils")

settings = get_settings()


def define_llm() -> BaseChatModel:
    """
    Define the LLM based on settings (provider, model name, temperature).

    Returns:
        LLM instance configured from settings

    Raises:
        ValueError: If the model name is invalid or provider is unsupported
    """
    settings = get_settings()

    logger.debug(f"{LogEmoji.AI_THINKING} Initializing {settings.llm_provider} LLM with model: {settings.llm_model_name}, temperature: {settings.llm_temperature}")

    try:
        if settings.llm_provider == LLMProvider.OPENAI:
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=settings.llm_model_name,
                temperature=settings.llm_temperature,
                api_key=settings.openai_api_key,
            )

        elif settings.llm_provider == LLMProvider.GEMINI:
            from langchain_google_genai import ChatGoogleGenerativeAI

            return ChatGoogleGenerativeAI(
                model=settings.llm_model_name,
                temperature=settings.llm_temperature,
                google_api_key=settings.gemini_api_key,
            )

        else:
            raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")

    except Exception as e:
        logger.error(f"{LogEmoji.ERROR} Failed to initialize LLM with model '{settings.llm_model_name}': {e}")
        raise ValueError(f"Failed to initialize LLM with model '{settings.llm_model_name}': {e}")


async def invoke_with_structured_output_retry(
    llm: BaseChatModel,
    prompt: str,
    schema_class: Type[T],
    config: Optional[Dict] = None,
    max_retries: int = 2,
) -> Optional[T]:
    """
    Invoke LLM with structured output and retry on parsing failures.

    Args:
        llm: The LLM instance
        prompt: The prompt to send to the LLM
        schema_class: The Pydantic model class for structured output
        config: Optional config dict with callbacks, etc.
        max_retries: Maximum number of retry attempts (default: 2)

    Returns:
        Instance of schema_class or None if all retries fail
    """
    from app.agent.prompts import STRUCTURED_OUTPUT_FIX_PROMPT

    structured_llm = llm.with_structured_output(schema_class)

    # First attempt
    try:
        logger.debug(
            f"{LogEmoji.AI_THINKING} Attempting structured output generation for {schema_class.__name__}"
        )
        result = await structured_llm.ainvoke(prompt, config=config)
        logger.debug(
            f"{LogEmoji.SUCCESS} Successfully generated {schema_class.__name__} on first attempt"
        )
        return result

    except OutputParserException as e:
        logger.warning(
            f"{LogEmoji.WARNING} Primary parsing error for {schema_class.__name__}: {e}"
        )

        # Retry attempts
        for retry_num in range(1, max_retries + 1):
            try:
                logger.info(
                    f"{LogEmoji.AI_THINKING} Retry attempt {retry_num}/{max_retries} with fix prompt..."
                )

                # Build retry/fix prompt
                retry_prompt = STRUCTURED_OUTPUT_FIX_PROMPT.format(
                    schema=schema_class.model_json_schema(),
                    previous_output=(
                        str(e.llm_output)
                        if hasattr(e, "llm_output")
                        else "No output captured"
                    ),
                    error_message=str(e),
                )

                # Try again with fix prompt
                fixed_result = await structured_llm.ainvoke(retry_prompt, config=config)
                logger.info(
                    f"{LogEmoji.SUCCESS} Successfully fixed {schema_class.__name__} on retry {retry_num}"
                )
                return fixed_result

            except OutputParserException as retry_error:
                logger.warning(
                    f"{LogEmoji.WARNING} Retry {retry_num}/{max_retries} failed for {schema_class.__name__}: {retry_error}"
                )
                if retry_num == max_retries:
                    logger.error(
                        f"{LogEmoji.ERROR} All retry attempts exhausted for {schema_class.__name__}"
                    )
                    return None
                continue

            except Exception as retry_error:
                logger.error(
                    f"{LogEmoji.ERROR} Unexpected error on retry {retry_num} for {schema_class.__name__}: {retry_error}"
                )
                return None

    except Exception as e:
        logger.error(
            f"{LogEmoji.ERROR} Unexpected error generating {schema_class.__name__}: {e}"
        )
        return None


def clean_raw_data(raw_data) -> Any:
    """
    Clean raw JSON data by removing null values

    Handles:
    - JSON strings
    - Already parsed dicts
    - Lists of JSON objects
    - Nested structures

    Args:
        raw_data: Raw JSON string, dict, or list

    Returns:
        Cleaned data structure (dict or list)
    """
    # Parse JSON string if needed
    if isinstance(raw_data, str):
        try:
            raw_data_json = json.loads(raw_data)
        except json.JSONDecodeError as e:
            logger.error(f"{LogEmoji.ERROR} Failed to parse JSON data: {e}")
            return {}
    else:
        raw_data_json = raw_data

    # Recursively clean null values
    def clean_recursive(data):
        """Recursively remove null values from data structure"""
        if isinstance(data, dict):
            # Clean dictionary: remove None values and recursively clean nested structures
            cleaned = {}
            for k, v in data.items():
                if v is not None:
                    cleaned[k] = clean_recursive(v)
            return cleaned
        elif isinstance(data, list):
            # Clean list: recursively clean each item, keep non-None items
            return [clean_recursive(item) for item in data if item is not None]
        else:
            # Return primitive values as-is
            return data

    try:
        cleaned_data = clean_recursive(raw_data_json)

        # Log cleaning statistics
        if isinstance(raw_data_json, dict) and isinstance(cleaned_data, dict):
            removed_count = len(raw_data_json) - len(cleaned_data)
            if removed_count > 0:
                logger.info(
                    f"{LogEmoji.TRANSFORM} Cleaned {removed_count} null values from raw data"
                )
        elif isinstance(raw_data_json, list) and isinstance(cleaned_data, list):
            logger.info(
                f"{LogEmoji.TRANSFORM} Cleaned list with {len(cleaned_data)} items"
            )

        return cleaned_data
    except Exception as e:
        logger.error(f"{LogEmoji.ERROR} Error cleaning raw data: {e}")
        return {} if isinstance(raw_data_json, dict) else []


def get_preferred_languages(
    languages: List[str], location: Optional[Dict[str, str]] = None
) -> str:
    """
    Determine preferred language based on languages and location

    Args:
        languages: List of language names (e.g., ["Français", "Anglais"])
        location: Location dict with 'country', 'city', 'full' keys

    Returns:
        Preferred language name in English (e.g., "French", "English")
    """
    # Language mapping from full name to English name
    language_map = {
        "français": "French",
        "french": "French",
        "anglais": "English",
        "english": "English",
        "espagnol": "Spanish",
        "spanish": "Spanish",
        "allemand": "German",
        "german": "German",
        "italien": "Italian",
        "italian": "Italian",
        "portugais": "Portuguese",
        "portuguese": "Portuguese",
        "chinois": "Chinese",
        "chinese": "Chinese",
        "japonais": "Japanese",
        "japanese": "Japanese",
        "arabe": "Arabic",
        "arabic": "Arabic",
    }

    # Country to language mapping
    country_language_map = {
        "france": "French",
        "united states": "English",
        "united kingdom": "English",
        "spain": "Spanish",
        "germany": "German",
        "italy": "Italian",
        "portugal": "Portuguese",
        "china": "Chinese",
        "japan": "Japanese",
    }

    # If only one language, return it
    if len(languages) == 1:
        lang_lower = languages[0].lower()
        return language_map.get(lang_lower, "English")

    # Try to match with location
    if location and location.get("country"):
        country_lower = location["country"].lower()
        preferred_lang = country_language_map.get(country_lower)

        if preferred_lang:
            # Check if this language is in the list
            for lang in languages:
                lang_lower = lang.lower()
                if language_map.get(lang_lower) == preferred_lang:
                    logger.debug(
                        f"{LogEmoji.VALIDATION} Preferred language matched by country: {preferred_lang}"
                    )
                    return preferred_lang

    # Default to first language
    first_lang = languages[0].lower()
    result = language_map.get(first_lang, "English")
    logger.debug(f"{LogEmoji.VALIDATION} Using first language as preferred: {result}")
    return result


def transform_profile_raw_to_lead(
    raw_data: List[Dict[str, Any]], linkedin_url: str
) -> Lead:
    """
    Transform raw LinkedIn JSON data to Lead pydantic model

    Args:
        raw_data: List containing the raw LinkedIn profile data
        linkedin_url: The LinkedIn profile URL

    Returns:
        Lead pydantic model instance
    """
    logger.info(f"{LogEmoji.TRANSFORM} Transforming raw LinkedIn data to Lead model")

    # Extract first item from list (LinkedIn scraper returns list with one item)
    if not raw_data or not isinstance(raw_data, list) or len(raw_data) == 0:
        logger.warning(
            f"{LogEmoji.WARNING} Empty or invalid raw data, returning minimal Lead"
        )
        return Lead(linkedin_url=linkedin_url)

    profile_data = raw_data[0]
    basic_info = profile_data.get("basic_info", {})
    experiences = profile_data.get("experience", [])
    languages_data = profile_data.get("languages", [])

    # Extract basic information
    full_name = basic_info.get("fullname")
    first_name = basic_info.get("first_name")
    last_name = basic_info.get("last_name")
    headline = basic_info.get("headline")

    # Extract location (priority: full > city > country > empty)
    location_data = basic_info.get("location", {})
    location = None
    if location_data:
        if location_data.get("full"):
            location = location_data["full"]
        elif location_data.get("city"):
            location = location_data["city"]
        elif location_data.get("country"):
            location = location_data["country"]

    logger.debug(f"{LogEmoji.INFO} Extracted location: {location}")

    # Extract current title and company from experience
    current_title = None
    current_company = None

    # Filter experiences where is_current is True
    current_experiences = [exp for exp in experiences if exp.get("is_current") is True]

    if current_experiences:
        # Take the first one (most recent / top one in the array)
        current_exp = current_experiences[0]
        current_title = current_exp.get("title")
        current_company = current_exp.get("company")
        logger.debug(
            f"{LogEmoji.INFO} Found current position: {current_title} at {current_company}"
        )
    else:
        logger.debug(f"{LogEmoji.WARNING} No current experience found")

    # Extract languages with "Native or bilingual proficiency"
    native_languages = [
        lang.get("language")
        for lang in languages_data
        if lang.get("proficiency") == "Native or bilingual proficiency"
        and lang.get("language")
    ]

    # Determine preferred language
    preferred_language = None
    if native_languages:
        if len(native_languages) == 1:
            # Only one native language
            preferred_language = native_languages[0]
            logger.debug(
                f"{LogEmoji.VALIDATION} Single native language: {preferred_language}"
            )
        else:
            # Multiple native languages - use location to determine preferred
            preferred_language_code = get_preferred_languages(
                native_languages, location_data
            )
            preferred_language = preferred_language_code
            logger.debug(
                f"{LogEmoji.VALIDATION} Multiple native languages, preferred: {preferred_language}"
            )
    else:
        logger.debug(f"{LogEmoji.WARNING} No native/bilingual languages found")

    # Create Lead model
    lead = Lead(
        linkedin_url=linkedin_url,
        full_name=full_name,
        first_name=first_name,
        last_name=last_name,
        headline=headline,
        current_title=current_title,
        current_company=current_company,
        location=location,
        languages=preferred_language,
    )

    logger.info(
        f"{LogEmoji.SUCCESS} Lead model created: {lead.full_name} - {lead.current_title}"
    )

    return lead


def transform_profile_raw_to_experiences(
    raw_data: List[Dict[str, Any]],
) -> List[Experience]:
    """
    Transform raw LinkedIn JSON data to list of Experience models

    Args:
        raw_data: List containing the raw LinkedIn profile data

    Returns:
        List of Experience model instances
    """
    logger.info(
        f"{LogEmoji.TRANSFORM} Transforming raw LinkedIn data to Experience list"
    )

    # Extract first item from list
    if not raw_data or not isinstance(raw_data, list) or len(raw_data) == 0:
        logger.warning(
            f"{LogEmoji.WARNING} Empty or invalid raw data, returning empty list"
        )
        return []

    profile_data = raw_data[0]
    experiences_data = profile_data.get("experience", [])

    if not experiences_data:
        logger.info(f"{LogEmoji.INFO} No experiences found in raw data")
        return []

    experiences_list = []
    for exp_data in experiences_data:
        # Extract skills and concatenate with commas
        skills_list = exp_data.get("skills", [])
        skills_str = None
        if skills_list and isinstance(skills_list, list):
            skills_str = ", ".join(skills_list)

        # Create Experience instance
        experience = Experience(
            title=exp_data.get("title"),
            company=exp_data.get("company"),
            location=exp_data.get("location"),
            duration=exp_data.get("duration"),
            description=exp_data.get("description"),
            employment_type=exp_data.get("employment_type"),
            location_type=exp_data.get("location_type"),
            skills=skills_str,
            is_current=exp_data.get("is_current"),
        )

        experiences_list.append(experience)
        logger.debug(
            f"{LogEmoji.INFO} Added experience: {experience.title} at {experience.company}"
        )

    logger.info(
        f"{LogEmoji.SUCCESS} Created {len(experiences_list)} Experience entries"
    )
    return experiences_list


def transform_profile_raw_to_educations(
    raw_data: List[Dict[str, Any]],
) -> List[Education]:
    """
    Transform raw LinkedIn JSON data to list of Education models

    Args:
        raw_data: List containing the raw LinkedIn profile data

    Returns:
        List of Education model instances
    """
    logger.info(
        f"{LogEmoji.TRANSFORM} Transforming raw LinkedIn data to Education list"
    )

    # Extract first item from list
    if not raw_data or not isinstance(raw_data, list) or len(raw_data) == 0:
        logger.warning(
            f"{LogEmoji.WARNING} Empty or invalid raw data, returning empty list"
        )
        return []

    profile_data = raw_data[0]
    education_data = profile_data.get("education", [])

    if not education_data:
        logger.info(f"{LogEmoji.INFO} No education found in raw data")
        return []

    educations_list = []
    for edu_data in education_data:
        # Create Education instance
        education = Education(
            school=edu_data.get("school"),
            degree=edu_data.get("degree"),
            degree_name=edu_data.get("degree_name"),
            field_of_study=edu_data.get("field_of_study"),
            duration=edu_data.get("duration"),
            description=edu_data.get("description"),
        )

        educations_list.append(education)
        logger.debug(
            f"{LogEmoji.INFO} Added education: {education.degree_name} at {education.school}"
        )

    logger.info(f"{LogEmoji.SUCCESS} Created {len(educations_list)} Education entries")
    return educations_list


def transform_profile_raw_to_certifications(
    raw_data: List[Dict[str, Any]],
) -> List[Certification]:
    """
    Transform raw LinkedIn JSON data to list of Certification models

    Args:
        raw_data: List containing the raw LinkedIn profile data

    Returns:
        List of Certification model instances
    """
    logger.info(
        f"{LogEmoji.TRANSFORM} Transforming raw LinkedIn data to Certification list"
    )

    # Extract first item from list
    if not raw_data or not isinstance(raw_data, list) or len(raw_data) == 0:
        logger.warning(
            f"{LogEmoji.WARNING} Empty or invalid raw data, returning empty list"
        )
        return []

    profile_data = raw_data[0]
    certifications_data = profile_data.get("certifications", [])

    if not certifications_data:
        logger.info(f"{LogEmoji.INFO} No certifications found in raw data")
        return []

    certifications_list = []
    for cert_data in certifications_data:
        # Create Certification instance
        certification = Certification(
            name=cert_data.get("name"),
            issuer=cert_data.get("issuer"),
            issued_date=cert_data.get("issued_date"),
        )

        certifications_list.append(certification)
        logger.debug(
            f"{LogEmoji.INFO} Added certification: {certification.name} from {certification.issuer}"
        )

    logger.info(
        f"{LogEmoji.SUCCESS} Created {len(certifications_list)} Certification entries"
    )
    return certifications_list


def transform_posts_raw_to_posts(raw_data: List[Dict[str, Any]]) -> List[Post]:
    """
    Transform raw LinkedIn JSON data to list of Post models

    Args:
        raw_data: List containing the raw LinkedIn posts data

    Returns:
        List of Post model instances
    """
    logger.info(f"{LogEmoji.TRANSFORM} Transforming raw LinkedIn data to Post list")

    # Validate input
    if not raw_data or not isinstance(raw_data, list):
        logger.warning(
            f"{LogEmoji.WARNING} Empty or invalid raw data, returning empty list"
        )
        return []

    posts_list = []
    for idx, post_data in enumerate(raw_data, start=1):
        try:
            # Generate simplified sequential post ID (post_id_001, post_id_002, etc.)
            post_id = f"post_id_{idx:03d}"

            # Extract URL
            url = post_data.get("url")

            # Extract posted_at and convert to ISO-8601 UTC
            posted_at = None
            if post_data.get("posted_at"):
                posted_at_data = post_data["posted_at"]
                # Try to use timestamp (milliseconds) to create ISO-8601
                if posted_at_data.get("timestamp"):
                    try:
                        from datetime import datetime

                        timestamp_ms = posted_at_data["timestamp"]
                        dt = datetime.fromtimestamp(timestamp_ms / 1000.0)
                        posted_at = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
                    except Exception as e:
                        logger.debug(
                            f"{LogEmoji.WARNING} Failed to parse timestamp: {e}"
                        )
                        # Fall back to date string if available
                        posted_at = posted_at_data.get("date")
                else:
                    # Use date string as fallback
                    posted_at = posted_at_data.get("date")

            # Extract post_type
            post_type = post_data.get("post_type", "regular")

            # Extract author information
            author = None
            if post_data.get("author"):
                author_data = post_data["author"]
                author = PostAuthor(
                    first_name=author_data.get("first_name"),
                    last_name=author_data.get("last_name"),
                    headline=author_data.get("headline"),
                )

            # Extract text
            text = post_data.get("text")

            # Extract stats and format as dict
            stats = ""
            if post_data.get("stats"):
                stats_data = str(post_data["stats"])
                stats = stats_data

            # Create Post instance
            post = Post(
                id=post_id,
                url=url,
                posted_at=posted_at,
                post_type=post_type,
                author=author,
                text=text,
                stats=stats,
            )

            posts_list.append(post)
            logger.debug(
                f"{LogEmoji.INFO} Added post: {post_id} by {author.first_name if author else 'Unknown'} {author.last_name if author else ''}"
            )

        except Exception as e:
            logger.warning(f"{LogEmoji.WARNING} Failed to parse post, skipping: {e}")
            continue

    logger.info(f"{LogEmoji.SUCCESS} Created {len(posts_list)} Post entries")
    return posts_list


def transform_reactions_raw_to_reactions(
    raw_data: List[Dict[str, Any]],
) -> List[Reaction]:
    """
    Transform raw LinkedIn JSON data to list of Reaction models

    Args:
        raw_data: List containing the raw LinkedIn reactions data

    Returns:
        List of Reaction model instances
    """
    logger.info(f"{LogEmoji.TRANSFORM} Transforming raw LinkedIn data to Reaction list")

    # Validate input
    if not raw_data or not isinstance(raw_data, list):
        logger.warning(
            f"{LogEmoji.WARNING} Empty or invalid raw data, returning empty list"
        )
        return []

    reactions_list = []
    for idx, reaction_data in enumerate(raw_data, start=1):
        try:
            # Generate simplified sequential reaction ID (reaction_id_001, reaction_id_002, etc.)
            reaction_id = f"reaction_id_{idx:03d}"

            # Extract action
            reaction_action = reaction_data.get("action", "")

            # Extract reacted_at and convert to ISO-8601 UTC
            reacted_at = None
            if reaction_data.get("timestamps"):
                timestamps_data = reaction_data["timestamps"]
                # Try to use timestamp (milliseconds) to create ISO-8601
                if timestamps_data.get("timestamp"):
                    try:
                        from datetime import datetime

                        timestamp_ms = timestamps_data["timestamp"]
                        dt = datetime.fromtimestamp(timestamp_ms / 1000.0)
                        reacted_at = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
                    except Exception as e:
                        logger.debug(
                            f"{LogEmoji.WARNING} Failed to parse timestamp: {e}"
                        )
                        # Fall back to date string if available
                        reacted_at = timestamps_data.get("date")
                else:
                    # Use date string as fallback
                    reacted_at = timestamps_data.get("date")

            # Extract post text
            post_text = reaction_data.get("text")

            # Extract post author information
            post_author = None
            if reaction_data.get("author"):
                author_data = reaction_data["author"]
                post_author = PostAuthor(
                    first_name=author_data.get("firstName"),
                    last_name=author_data.get("lastName"),
                    headline=author_data.get("headline"),
                )

            # Extract post URL
            post_url = reaction_data.get("post_url")

            # Create Reaction instance
            reaction = Reaction(
                id=reaction_id,
                action=reaction_action,
                reacted_at=reacted_at,
                post_text=post_text,
                post_author=post_author,
                post_url=post_url,
            )

            reactions_list.append(reaction)
            logger.debug(
                f"{LogEmoji.INFO} Added reaction: {reaction_id} - {reaction_action} on post by {post_author.first_name if post_author else 'Unknown'} {post_author.last_name if post_author else ''}"
            )

        except Exception as e:
            logger.warning(
                f"{LogEmoji.WARNING} Failed to parse reaction, skipping: {e}"
            )
            continue

    logger.info(f"{LogEmoji.SUCCESS} Created {len(reactions_list)} Reaction entries")
    return reactions_list
