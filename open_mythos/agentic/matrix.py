from typing import List, Dict, Any, Optional
from .base import Agent, MythosAgent
from ..main import OpenMythos
from ..variants import mythos_1b
from ..tokenizer import MythosTokenizer
from .tools import ToolRegistry

class AgentMatrix:
    """
    Manages a matrix of specialized agents.
    """
    def __init__(self, model: Optional[OpenMythos] = None, tokenizer: Optional[MythosTokenizer] = None, tools: Optional[ToolRegistry] = None):
        self.agents: Dict[str, Agent] = {}
        self.model = model
        self.tokenizer = tokenizer
        self.tools = tools if tools else ToolRegistry()

        if self.tokenizer is None:
            self.tokenizer = MythosTokenizer()

        if self.model is None:
            # Default to 1B model for demonstration if not provided
            cfg = mythos_1b()
            cfg.vocab_size = self.tokenizer.vocab_size
            self.model = OpenMythos(cfg)

    def add_agent(self, agent: Agent):
        """
        Adds an agent to the matrix.
        """
        self.agents[agent.name] = agent

    def get_agent(self, name: str) -> Optional[Agent]:
        """
        Retrieves an agent by name.
        """
        return self.agents.get(name)

    def spawn_agent(self, name: str, role: str, system_prompt: str, agent_type: str = "mythos") -> Agent:
        """
        Spawns a new agent of a specified type.
        """
        if agent_type == "mythos":
            agent = MythosAgent(name, role, system_prompt, self.model, self.tokenizer, self.tools)
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")

        self.add_agent(agent)
        return agent

    def list_agents(self) -> List[str]:
        """
        Lists all agents currently in the matrix.
        """
        return list(self.agents.keys())
