from typing import Dict, Any, Optional
from jinja2 import Environment, Template, TemplateError, StrictUndefined
from jinja2.exceptions import SecurityError
import re

from ..core.exceptions import QueryExecutionError


class JinjaTemplateService:
    """Service for compiling and rendering Jinja templates for SQL queries."""
    
    def __init__(self):
        # Create a secure Jinja environment with strict undefined handling
        self.env = Environment(
            undefined=StrictUndefined,
            autoescape=False,  # SQL doesn't need HTML escaping
            trim_blocks=True,
            lstrip_blocks=True,
        )
        
        # Add custom filters for SQL operations
        self._add_custom_filters()
    
    def _add_custom_filters(self):
        """Add custom filters for SQL operations."""
        
        def sql_quote(value):
            """Quote a value for SQL (simple string escaping)."""
            if value is None:
                return "NULL"
            if isinstance(value, (int, float)):
                return str(value)
            return f"'{str(value).replace("'", "''")}'"
        self.env.filters['sql_quote'] = sql_quote
        
        def sql_in(values):
            """Convert a list to SQL IN clause format."""
            if not values:
                return "()"
            quoted_values = [sql_quote(v) for v in values]
            return f"({', '.join(quoted_values)})"
        self.env.filters['sql_in'] = sql_in
        
        def sql_like(value):
            """Escape LIKE patterns."""
            if value is None:
                return "NULL"
            return f"'{str(value).replace('%', '\\%').replace('_', '\\_')}'"
        self.env.filters['sql_like'] = sql_like
    
    def compile_template(self, template_string: str) -> Template:
        """Compile a Jinja template string."""
        try:
            return self.env.from_string(template_string)
        except TemplateError as e:
            raise QueryExecutionError(None, f"Template compilation error: {str(e)}")
    
    def render_template(
        self, 
        template_string: str, 
        parameters: Dict[str, Any],
        safe_mode: bool = True
    ) -> str:
        """
        Render a Jinja template with parameters.
        
        Args:
            template_string: The Jinja template string
            parameters: Parameters to substitute in the template
            safe_mode: If True, applies security restrictions
            
        Returns:
            Rendered SQL string
        """
        try:
            # Compile the template
            template = self.compile_template(template_string)
            
            # Apply security restrictions if in safe mode
            if safe_mode:
                self._validate_template_security(template_string, parameters)
            
            # Render the template
            rendered_sql = template.render(**parameters)
            
            # Post-process the rendered SQL
            rendered_sql = self._post_process_sql(rendered_sql)
            
            return rendered_sql
            
        except TemplateError as e:
            raise QueryExecutionError(None, f"Template rendering error: {str(e)}")
        except Exception as e:
            raise QueryExecutionError(None, f"Template processing error: {str(e)}")
    
    def _validate_template_security(self, template_string: str, parameters: Dict[str, Any]):
        """Validate template for security concerns."""
        # Check for potentially dangerous Jinja constructs
        dangerous_patterns = [
            r'{{\s*config\s*}}',
            r'{{\s*request\s*}}',
            r'{{\s*session\s*}}',
            r'{{\s*g\s*}}',
            r'{{\s*url_for\s*}}',
            r'{{\s*get_flashed_messages\s*}}',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, template_string, re.IGNORECASE):
                raise SecurityError(f"Potentially dangerous template construct detected: {pattern}")
        
        # Check for file system access attempts
        file_access_patterns = [
            r'open\s*\(',
            r'file\s*\(',
            r'__import__\s*\(',
            r'eval\s*\(',
            r'exec\s*\(',
        ]
        
        for pattern in file_access_patterns:
            if re.search(pattern, template_string, re.IGNORECASE):
                raise SecurityError(f"Potentially dangerous function call detected: {pattern}")
    
    def _post_process_sql(self, sql: str) -> str:
        """Post-process the rendered SQL for common issues."""
        # Remove extra whitespace
        sql = re.sub(r'\s+', ' ', sql).strip()
        
        # Ensure proper semicolon handling
        if sql and not sql.endswith(';'):
            sql += ';'
        
        return sql
    
    def validate_template_variables(self, template_string: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that all required template variables are provided.
        
        Returns:
            Dict of missing variables if any
        """
        try:
            template = self.compile_template(template_string)
            missing_vars = {}
            
            # Get all variable names from the template
            template_vars = template.module.__code__.co_names
            
            for var_name in template_vars:
                if var_name not in parameters and not var_name.startswith('_'):
                    missing_vars[var_name] = f"Required template variable '{var_name}' is missing"
            
            return missing_vars
            
        except Exception as e:
            raise QueryExecutionError(None, f"Template validation error: {str(e)}")
    
    def get_template_variables(self, template_string: str) -> set:
        """Extract all variable names used in a template."""
        try:
            template = self.compile_template(template_string)
            return set(template.module.__code__.co_names)
        except Exception:
            return set() 