from typing import Dict, Any, Set, Optional
from jinja2 import Environment, Template, TemplateError, StrictUndefined
from jinja2.exceptions import SecurityError, UndefinedError
import re

from ..core.exceptions import ToolExecutionError


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
            escaped_value = str(value).replace("'", "''")
            return f"'{escaped_value}'"
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
            escaped_value = str(value).replace('%', '\\%').replace('_', '\\_')
            return f"'{escaped_value}'"
        self.env.filters['sql_like'] = sql_like
    
    def compile_template(self, template_string: str) -> Template:
        """Compile a Jinja template string."""
        try:
            return self.env.from_string(template_string)
        except TemplateError as e:
            raise ToolExecutionError(None, f"Template compilation error: {str(e)}")
    
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
            
        except UndefinedError as e:
            # Handle undefined variables
            missing_vars = self._extract_missing_variables(str(e))
            if missing_vars:
                missing_var_names = list(missing_vars.keys())
                raise ToolExecutionError(
                    None, 
                    f"Missing required template variables: {', '.join(missing_var_names)}"
                )
            else:
                raise ToolExecutionError(None, f"Template compilation error: {str(e)}")
                
        except TemplateError as e:
            raise ToolExecutionError(None, f"Template compilation error: {str(e)}")
            
        except Exception as e:
            raise ToolExecutionError(None, f"Template processing error: {str(e)}")
    
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
            raise ToolExecutionError(None, f"Template validation error: {str(e)}")
    
    def get_template_variables(self, template_string: str) -> set:
        """Extract all variable names used in a template."""
        try:
            template = self.compile_template(template_string)
            return set(template.module.__code__.co_names)
        except Exception:
            return set()
    
    def process_sql_template(self, sql: str, parameters: Dict[str, Any]) -> str:
        """
        Process SQL template with Jinja2 and parameters.
        
        Args:
            sql: SQL string that may contain Jinja2 template syntax
            parameters: Dictionary of parameters to substitute
            
        Returns:
            Processed SQL string with parameters substituted
            
        Raises:
            ToolExecutionError: If template processing fails
        """
        try:
            # Check if the SQL contains Jinja template syntax
            if not self._has_template_syntax(sql):
                return sql
            
            # Create template and render with parameters
            template = self.env.from_string(sql)
            rendered_sql = template.render(**parameters)
            
            return rendered_sql
            
        except UndefinedError as e:
            # Handle undefined variables
            missing_vars = self._extract_missing_variables(str(e))
            if missing_vars:
                missing_var_names = list(missing_vars.keys())
                raise ToolExecutionError(
                    None, 
                    f"Missing required template variables: {', '.join(missing_var_names)}"
                )
            else:
                raise ToolExecutionError(None, f"Template compilation error: {str(e)}")
                
        except TemplateError as e:
            raise ToolExecutionError(None, f"Template compilation error: {str(e)}")
            
        except Exception as e:
            raise ToolExecutionError(None, f"Template processing error: {str(e)}")
    
    def _has_template_syntax(self, sql: str) -> bool:
        """Check if SQL contains Jinja template syntax."""
        template_indicators = ['{{', '{%', '{#']
        return any(indicator in sql for indicator in template_indicators)
    
    def _extract_missing_variables(self, error_message: str) -> Dict[str, Any]:
        """
        Extract missing variable names from Jinja2 error messages.
        
        Args:
            error_message: Error message from Jinja2
            
        Returns:
            Dictionary of missing variable names
        """
        missing_vars = {}
        
        # Common patterns in Jinja2 error messages
        if "'" in error_message and "is undefined" in error_message:
            # Extract variable name between quotes
            start = error_message.find("'") + 1
            end = error_message.find("'", start)
            if start > 0 and end > start:
                var_name = error_message[start:end]
                missing_vars[var_name] = None
        
        return missing_vars
    
    def validate_template(self, sql: str, required_variables: Optional[Set[str]] = None) -> Dict[str, Any]:
        """
        Validate SQL template without executing it.
        
        Args:
            sql: SQL string that may contain Jinja2 template syntax
            required_variables: Set of required variable names
            
        Returns:
            Dictionary with validation results
            
        Raises:
            ToolExecutionError: If template validation fails
        """
        try:
            if not self._has_template_syntax(sql):
                return {
                    "is_template": False,
                    "variables": set(),
                    "required_variables": required_variables or set(),
                    "missing_variables": set()
                }
            
            # Parse template to extract variables
            template = self.env.from_string(sql)
            template_variables = self._extract_template_variables(template)
            
            # Check for missing required variables
            missing_vars = set()
            if required_variables:
                missing_vars = required_variables - template_variables
            
            return {
                "is_template": True,
                "variables": template_variables,
                "required_variables": required_variables or set(),
                "missing_variables": missing_vars
            }
            
        except Exception as e:
            raise ToolExecutionError(None, f"Template validation error: {str(e)}")
    
    def _extract_template_variables(self, template) -> Set[str]:
        """
        Extract variable names from a Jinja2 template.
        
        Args:
            template: Jinja2 template object
            
        Returns:
            Set of variable names used in the template
        """
        variables = set()
        
        try:
            # Get the AST (Abstract Syntax Tree) of the template
            ast = template.environment.parse(template.source)
            
            # Extract variable names from the AST
            for node in ast.find_all(self.env.variable_start_string):
                if hasattr(node, 'name'):
                    variables.add(node.name)
                    
        except Exception:
            # Fallback: try to extract variables using regex
            import re
            var_pattern = r'\{\{\s*(\w+)\s*\}\}'
            matches = re.findall(var_pattern, template.source)
            variables.update(matches)
        
        return variables
    
    def get_template_info(self, sql: str) -> Dict[str, Any]:
        """
        Get information about a SQL template.
        
        Args:
            sql: SQL string that may contain Jinja2 template syntax
            
        Returns:
            Dictionary with template information
        """
        try:
            if not self._has_template_syntax(sql):
                return {
                    "is_template": False,
                    "variables": set(),
                    "template_syntax": None
                }
            
            template = self.env.from_string(sql)
            variables = self._extract_template_variables(template)
            
            return {
                "is_template": True,
                "variables": variables,
                "template_syntax": "jinja2"
            }
            
        except Exception as e:
            raise ToolExecutionError(None, f"Template validation error: {str(e)}") 