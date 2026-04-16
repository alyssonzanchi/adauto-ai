"""
Base prompt template class.
"""
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, select_autoescape


class BasePromptTemplate(ABC):
    """
    Base class for prompt templates using Jinja2.

    Provides:
    - Jinja2 template rendering
    - Few-shot examples support
    - Chain-of-thought prompting
    - JSON output formatting
    """

    def __init__(self, template_dir: str = None):
        """
        Initialize prompt template.

        Args:
            template_dir: Directory containing template files
        """
        if template_dir is None:
            # Default to templates subdirectory
            template_dir = Path(__file__).parent / "templates"

        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get system prompt.

        Returns:
            System prompt string
        """
        pass

    @abstractmethod
    def get_template_name(self) -> str:
        """
        Get template filename.

        Returns:
            Template filename
        """
        pass

    def render(self, context: Dict[str, Any]) -> str:
        """
        Render prompt template with context.

        Args:
            context: Variables for template rendering

        Returns:
            Rendered prompt string
        """
        template = self.env.get_template(self.get_template_name())
        return template.render(**context)

    def render_with_few_shot(
        self,
        context: Dict[str, Any],
        examples: list[Dict[str, Any]]
    ) -> str:
        """
        Render prompt with few-shot examples.

        Args:
            context: Variables for template rendering
            examples: List of few-shot examples

        Returns:
            Rendered prompt with examples
        """
        # Add examples to context
        context_with_examples = {**context, "examples": examples}
        return self.render(context_with_examples)

    def format_response(self, response: str) -> Dict[str, Any]:
        """
        Format LLM response as JSON dict.

        Args:
            response: Raw LLM response string

        Returns:
            Parsed JSON dict

        Raises:
            ValueError: If response is not valid JSON
        """
        try:
            # Try to parse as JSON
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            # (in case model added extra text)
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1

            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)

            raise ValueError(f"Response is not valid JSON: {response[:200]}...")

    def add_chain_of_thought(
        self,
        prompt: str,
        task: str,
        steps: list[str]
    ) -> str:
        """
        Add chain-of-thought reasoning to prompt.

        Args:
            prompt: Original prompt
            task: Task description
            steps: Reasoning steps

        Returns:
            Prompt with chain-of-thought
        """
        cot_prompt = f"{prompt}\n\n"
        cot_prompt += f"Task: {task}\n\n"
        cot_prompt += "Let's think through this step by step:\n"

        for i, step in enumerate(steps, 1):
            cot_prompt += f"{i}. {step}\n"

        cot_prompt += "\nBased on this reasoning, provide your answer in JSON format."

        return cot_prompt
