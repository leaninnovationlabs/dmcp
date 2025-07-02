import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.jinja_template_service import JinjaTemplateService
from app.services.tool_execution_service import ToolExecutionService
from app.core.exceptions import ToolExecutionError
from app.models.database import Datasource


class TestJinjaTemplateService:
    """Test cases for Jinja template service."""
    
    def setup_method(self):
        self.template_service = JinjaTemplateService()
    
    def test_simple_variable_substitution(self):
        """Test simple variable substitution in SQL."""
        template = "SELECT * FROM users WHERE id = {{ user_id }}"
        parameters = {"user_id": 123}
        
        result = self.template_service.render_template(template, parameters)
        expected = "SELECT * FROM users WHERE id = 123;"
        
        assert result == expected
    
    def test_string_variable_substitution(self):
        """Test string variable substitution with proper quoting."""
        template = "SELECT * FROM users WHERE name = {{ name }}"
        parameters = {"name": "John Doe"}
        
        result = self.template_service.render_template(template, parameters)
        expected = "SELECT * FROM users WHERE name = 'John Doe';"
        
        assert result == expected
    
    def test_conditional_logic(self):
        """Test conditional logic in SQL templates."""
        template = """
        SELECT * FROM users 
        WHERE 1=1
        {% if user_id %}
        AND id = {{ user_id }}
        {% endif %}
        {% if name %}
        AND name = {{ name }}
        {% endif %}
        """
        parameters = {"user_id": 123, "name": "John"}
        
        result = self.template_service.render_template(template, parameters)
        expected = "SELECT * FROM users WHERE 1=1 AND id = 123 AND name = 'John';"
        
        assert result == expected
    
    def test_list_in_clause(self):
        """Test using the custom sql_in filter for IN clauses."""
        template = "SELECT * FROM users WHERE id IN {{ user_ids | sql_in }}"
        parameters = {"user_ids": [1, 2, 3, 4]}
        
        result = self.template_service.render_template(template, parameters)
        expected = "SELECT * FROM users WHERE id IN (1, 2, 3, 4);"
        
        assert result == expected
    
    def test_like_pattern_escaping(self):
        """Test LIKE pattern escaping."""
        template = "SELECT * FROM users WHERE name LIKE {{ pattern | sql_like }}"
        parameters = {"pattern": "John%"}
        
        result = self.template_service.render_template(template, parameters)
        expected = "SELECT * FROM users WHERE name LIKE 'John\\%';"
        
        assert result == expected
    
    def test_missing_variable_error(self):
        """Test error handling for missing variables."""
        template = "SELECT * FROM users WHERE id = {{ user_id }}"
        parameters = {}
        
        with pytest.raises(ToolExecutionError) as exc_info:
            self.template_service.render_template(template, parameters)
        
        assert "Template rendering error" in str(exc_info.value)
    
    def test_security_validation(self):
        """Test security validation against dangerous constructs."""
        dangerous_template = "SELECT * FROM users WHERE id = {{ config.DATABASE_URL }}"
        parameters = {"config": {"DATABASE_URL": "test"}}
        
        with pytest.raises(ToolExecutionError) as exc_info:
            self.template_service.render_template(dangerous_template, parameters)
        
        assert "Template processing error" in str(exc_info.value)
    
    def test_get_template_variables(self):
        """Test extracting template variables."""
        template = "SELECT * FROM users WHERE id = {{ user_id }} AND name = {{ name }}"
        variables = self.template_service.get_template_variables(template)
        
        assert "user_id" in variables
        assert "name" in variables


class MockDatasource:
    def __init__(self, database_type="postgresql"):
        self.database_type = database_type
        self.id = 1
        self.name = "test_datasource"


class MockConnection:
    def __init__(self):
        self.execute = AsyncMock()
    
    async def execute(self, sql, parameters=None):
        # Mock successful execution
        return [{"id": 1, "name": "test"}]


class MockConnectionManager:
    def __init__(self):
        self.get_connection = AsyncMock()
    
    async def get_connection(self, datasource):
        return MockConnection()


class TestToolExecutionServiceWithTemplates:
    """Test cases for tool execution service with Jinja templates."""
    
    @pytest.fixture
    def mock_db(self):
        return AsyncMock()
    
    @pytest.fixture
    def mock_connection_manager(self):
        return MockConnectionManager()
    
    @pytest.fixture
    def service(self, mock_db):
        return ToolExecutionService(mock_db)
    
    @pytest.mark.asyncio
    async def test_execute_query_with_jinja_template(self, service):
        """Test executing a query with Jinja template."""
        datasource = MockDatasource()
        sql = "SELECT * FROM users WHERE name = '{{ name }}'"
        parameters = {"name": "John"}
        
        # Mock the connection manager
        service.connection_manager = MockConnectionManager()
        
        result = await service._execute_query(datasource, sql, parameters)
        
        assert result.success is True
        assert result.data == [{"id": 1, "name": "test"}]
        assert result.row_count == 1
    
    @pytest.mark.asyncio
    async def test_execute_query_without_jinja_template(self, service):
        """Test executing a query without Jinja template."""
        datasource = MockDatasource()
        sql = "SELECT * FROM users WHERE name = 'John'"
        parameters = {}
        
        # Mock the connection manager
        service.connection_manager = MockConnectionManager()
        
        result = await service._execute_query(datasource, sql, parameters)
        
        # Verify the query was executed as-is
        assert result.success is True
        assert result.data == [{"id": 1, "name": "test"}]
    
    @pytest.mark.asyncio
    async def test_execute_query_with_missing_template_variables(self, service):
        """Test executing a query with missing template variables."""
        datasource = MockDatasource()
        sql = "SELECT * FROM users WHERE name = '{{ name }}' AND age = {{ age }}"
        parameters = {"name": "John"}  # Missing 'age' parameter
        
        # Mock the connection manager
        service.connection_manager = MockConnectionManager()
        
        with pytest.raises(ToolExecutionError) as exc_info:
            await service._execute_query(datasource, sql, parameters)
        
        assert "Missing required template variables" in str(exc_info.value)
        assert "age" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_execute_query_with_invalid_template_syntax(self, service):
        """Test executing a query with invalid template syntax."""
        datasource = MockDatasource()
        sql = "SELECT * FROM users WHERE name = '{{ name }'  # Missing closing brace"
        parameters = {"name": "John"}
        
        # Mock the connection manager
        service.connection_manager = MockConnectionManager()
        
        with pytest.raises(ToolExecutionError) as exc_info:
            await service._execute_query(datasource, sql, parameters)
        
        assert "Template compilation error" in str(exc_info.value)


if __name__ == "__main__":
    # Example usage
    template_service = JinjaTemplateService()
    
    # Example 1: Simple variable substitution
    sql1 = "SELECT * FROM users WHERE id = {{ user_id }}"
    params1 = {"user_id": 123}
    result1 = template_service.render_template(sql1, params1)
    print(f"Example 1: {result1}")
    
    # Example 2: Conditional logic
    sql2 = """
    SELECT * FROM users 
    WHERE 1=1
    {% if user_id %}
    AND id = {{ user_id }}
    {% endif %}
    {% if name %}
    AND name = {{ name }}
    {% endif %}
    """
    params2 = {"user_id": 123, "name": "John"}
    result2 = template_service.render_template(sql2, params2)
    print(f"Example 2: {result2}")
    
    # Example 3: IN clause with list
    sql3 = "SELECT * FROM users WHERE id IN {{ user_ids | sql_in }}"
    params3 = {"user_ids": [1, 2, 3, 4]}
    result3 = template_service.render_template(sql3, params3)
    print(f"Example 3: {result3}")
    
    # Example 4: LIKE pattern
    sql4 = "SELECT * FROM users WHERE name LIKE {{ pattern | sql_like }}"
    params4 = {"pattern": "John%"}
    result4 = template_service.render_template(sql4, params4)
    print(f"Example 4: {result4}") 

    # Example 5: Pagination
    sql5 = "SELECT * FROM users LIMIT {{ limit }} OFFSET {{ offset }}"
    params5 = {"limit": 10, "offset": 0}
    result5 = template_service.render_template(sql5, params5)
    print(f"Example 5: {result5}") 

    # Example 6: String interpolation
    sql6 = "SELECT * FROM users WHERE name = {{ name | sql_string }}"
    params6 = {"name": "John"}
    result6 = template_service.render_template(sql6, params6)
    print(f"Example 6: {result6}") 

    # Example 7: String interpolation with Jinja2
    sql7 = "SELECT * FROM users WHERE 1=1 {% if class is defined %} and classification = {{class | sql_quote}}  {% endif %}"
    params7 = {"class": "John"}
    result7 = template_service.render_template(sql7, params7)
    print(f"Example 7: {result7}") 