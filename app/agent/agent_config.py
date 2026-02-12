# Empty agent config
from typing import Optional

from pydantic import BaseModel


class SimpleAgentConfig(BaseModel):
    exemple: Optional[str]


simple_agent_config = SimpleAgentConfig(exemple="test")
