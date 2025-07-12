"""
Jinja2 template engine implementation
"""

import os
import re
from typing import Dict, Any, List
from jinja2 import Environment, FileSystemLoader, Template, TemplateError as Jinja2TemplateError
from src.templates.base import TemplateEngine
from src.core.models import TemplateError


class Jinja2TemplateEngine(TemplateEngine):
    """Jinja2-based template engine"""
    
    def __init__(self, template_dir: str = "templates"):
        """
        Initialize the Jinja2 template engine
        
        Args:
            template_dir: Directory containing template files
        """
        self.template_dir = template_dir
        self._ensure_template_dir()
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def _ensure_template_dir(self):
        """Ensure the template directory exists"""
        if not os.path.exists(self.template_dir):
            os.makedirs(self.template_dir)
    
    def render(self, template_name: str, variables: Dict[str, Any]) -> str:
        """
        Render a Jinja2 template with the given variables
        
        Args:
            template_name: Name of the template file
            variables: Variables to substitute in the template
            
        Returns:
            str: Rendered template content
            
        Raises:
            TemplateError: If template rendering fails
        """
        try:
            template = self.env.get_template(template_name)
            return template.render(**variables)
        except Jinja2TemplateError as e:
            raise TemplateError(f"Failed to render template {template_name}: {str(e)}")
        except Exception as e:
            raise TemplateError(f"Unexpected error rendering template {template_name}: {str(e)}")
    
    def load_template(self, template_name: str) -> str:
        """
        Load a template by name
        
        Args:
            template_name: Name of the template file
            
        Returns:
            str: Template content
            
        Raises:
            TemplateError: If template loading fails
        """
        try:
            template_path = os.path.join(self.template_dir, template_name)
            if not os.path.exists(template_path):
                raise TemplateError(f"Template file not found: {template_path}")
            
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise TemplateError(f"Failed to load template {template_name}: {str(e)}")
    
    def validate_template(self, template_content: str) -> bool:
        """
        Validate if Jinja2 template content is valid
        
        Args:
            template_content: The template content to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            Template(template_content)
            return True
        except Jinja2TemplateError:
            return False
    
    def get_template_variables(self, template_name: str) -> List[str]:
        """
        Get a list of variables used in the Jinja2 template
        
        Args:
            template_name: Name of the template
            
        Returns:
            List[str]: List of variable names used in the template
        """
        try:
            template_content = self.load_template(template_name)
            
            # Use regex to find Jinja2 variables
            # This is a simplified implementation - for production use, 
            # you might want to use Jinja2's AST parsing
            variable_pattern = r'\{\{\s*([^}]+)\s*\}\}'
            variables = re.findall(variable_pattern, template_content)
            
            # Clean up variable names (remove filters, etc.)
            cleaned_variables = []
            for var in variables:
                # Split by pipes to get the base variable name
                base_var = var.split('|')[0].strip()
                # Split by dots to get the root variable
                root_var = base_var.split('.')[0].strip()
                if root_var not in cleaned_variables:
                    cleaned_variables.append(root_var)
            
            return cleaned_variables
        except Exception:
            return []
    
    def render_string(self, template_string: str, variables: Dict[str, Any]) -> str:
        """
        Render a template string directly
        
        Args:
            template_string: Template content as string
            variables: Variables to substitute in the template
            
        Returns:
            str: Rendered template content
            
        Raises:
            TemplateError: If template rendering fails
        """
        try:
            template = Template(template_string)
            return template.render(**variables)
        except Jinja2TemplateError as e:
            raise TemplateError(f"Failed to render template string: {str(e)}")
        except Exception as e:
            raise TemplateError(f"Unexpected error rendering template string: {str(e)}")
