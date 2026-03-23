"""
Base Agent class for all travel planner agents
Provides common functionality and Gemini API integration
"""

from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
try:
    import google.genai as genai
except ImportError:
    import google.generativeai as genai
from config import get_settings
from travel_planner.utils.logger import logger


class BaseAgent(ABC):
    """Abstract base class for all agents"""
    
    def __init__(self, name: str, role: str, goal: str):
        """
        Initialize base agent
        
        Args:
            name: Agent name
            role: Agent's role description
            goal: Agent's primary goal
        """
        self.name = name
        self.role = role
        self.goal = goal
        self.settings = get_settings()
        
        # Initialize Gemini
        self._setup_gemini()
        
        logger.info(f"Initialized {self.name} agent")
    
    def _setup_gemini(self):
        """Setup Gemini API client"""
        try:
            # Try new google.genai API first
            try:
                import google.genai as genai_new
                self.client = genai_new.Client(api_key=self.settings.google_api_key)
                self.use_new_api = True
                self.model = None  # Model is specified per request in new API
                logger.debug(f"New Gemini API configured for {self.name}")
            except (ImportError, AttributeError):
                # Fallback to old API
                import google.generativeai as genai_old
                genai_old.configure(api_key=self.settings.google_api_key)
                self.model = genai_old.GenerativeModel(self.settings.gemini_model)
                self.use_new_api = False
                self.client = None
                logger.debug(f"Legacy Gemini API configured for {self.name}")
        except Exception as e:
            logger.error(f"Failed to setup Gemini API: {e}")
            raise
    
    def generate_response(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Generate response using Gemini
        
        Args:
            prompt: Input prompt
            context: Optional context dictionary
            temperature: Optional temperature override
            
        Returns:
            Generated text response
        """
        try:
            # Build full prompt with context
            full_prompt = self._build_prompt(prompt, context)
            
            temp = temperature or self.settings.temperature
            
            if self.use_new_api:
                # Use new google.genai API
                response = self.client.models.generate_content(
                    model=self.settings.gemini_model,
                    contents=full_prompt,
                    config={
                        "temperature": temp,
                        "max_output_tokens": self.settings.max_tokens,
                    }
                )
                return response.text
            else:
                # Use legacy google.generativeai API
                generation_config = {
                    "temperature": temp,
                    "max_output_tokens": self.settings.max_tokens,
                }
                
                response = self.model.generate_content(
                    full_prompt,
                    generation_config=generation_config
                )
                return response.text
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Error: {str(e)}"
    
    def _build_prompt(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Build full prompt with role, goal, and context
        
        Args:
            prompt: Base prompt
            context: Optional context data
            
        Returns:
            Complete prompt string
        """
        parts = [
            f"You are {self.name}, a {self.role}.",
            f"Your goal is to {self.goal}.",
            ""
        ]
        
        if context:
            parts.append("Context:")
            for key, value in context.items():
                parts.append(f"- {key}: {value}")
            parts.append("")
        
        parts.append(f"Task: {prompt}")
        
        return "\n".join(parts)
    
    @abstractmethod
    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute agent's main task
        
        Args:
            task: Task description
            context: Optional context dictionary
            
        Returns:
            Dictionary with execution results
        """
        pass
    
    def summarize_results(self, results: Dict[str, Any]) -> str:
        """
        Summarize results in human-readable format
        
        Args:
            results: Results dictionary
            
        Returns:
            Formatted summary string
        """
        prompt = f"Summarize the following results in a clear, concise manner:\n\n{results}"
        return self.generate_response(prompt)
    
    def __str__(self) -> str:
        return f"{self.name} ({self.role})"
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.name}>"


__all__ = ["BaseAgent"]
