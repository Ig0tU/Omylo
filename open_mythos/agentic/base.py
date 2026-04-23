from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import torch
from ..main import OpenMythos
from ..tokenizer import MythosTokenizer

class Agent(ABC):
    """
    Abstract base class for all agents in the OpenMythos ecosystem.
    """
    def __init__(self, name: str, role: str, system_prompt: str):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt

    @abstractmethod
    def run(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Runs the agent on a given task with optional context.
        """
        pass

class MythosAgent(Agent):
    """
    An agent powered by the OpenMythos local model.
    """
    def __init__(self, name: str, role: str, system_prompt: str, model: OpenMythos, tokenizer: MythosTokenizer):
        super().__init__(name, role, system_prompt)
        self.model = model
        self.tokenizer = tokenizer

    def run(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Runs the local OpenMythos model to generate a response.
        """
        full_prompt = f"System: {self.system_prompt}\n"
        if context:
            full_prompt += f"Context: {context}\n"
        full_prompt += f"User: {task}\nAssistant:"

        input_ids = torch.tensor([self.tokenizer.encode(full_prompt)])
        # Use default generation params, or make them configurable
        output_ids = self.model.generate(
            input_ids,
            max_new_tokens=512,
            n_loops=self.model.cfg.max_loop_iters
        )

        response = self.tokenizer.decode(output_ids[0].tolist())
        # Strip the prompt from the response
        if "Assistant:" in response:
            response = response.split("Assistant:")[-1].strip()

        return response
