"""
Base template engine interface
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from src.core.models import TemplateError


class TemplateEngine(ABC):
    """Abstract base class for template engines"""
    
    @abstractmethod
    def render(self, template_name: str, variables: Dict[str, Any]) -> str:
        """
        Render a template with the given variables
        
        Args:
            template_name: Name of the template to render
            variables: Variables to substitute in the template
            
        Returns:
            str: Rendered template content
            
        Raises:
            TemplateError: If template rendering fails
        """
        pass
    
    @abstractmethod
    def load_template(self, template_name: str) -> str:
        """
        Load a template by name
        
        Args:
            template_name: Name of the template to load
            
        Returns:
            str: Template content
            
        Raises:
            TemplateError: If template loading fails
        """
        pass
    
    def validate_template(self, template_content: str) -> bool:
        """
        Validate if template content is valid
        
        Args:
            template_content: The template content to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        return bool(template_content and template_content.strip())
    
    def get_template_variables(self, template_name: str) -> list:
        """
        Get a list of variables used in the template
        
        Args:
            template_name: Name of the template
            
        Returns:
            list: List of variable names used in the template
        """
        # Default implementation - can be overridden by specific engines
        return []
