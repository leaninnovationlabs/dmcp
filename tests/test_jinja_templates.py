import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.jinja_template_service import JinjaTemplateService
from app.services.query_execution_service import QueryExecutionService
from app.core.exceptions import QueryExecutionError


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
        
        with pytest.raises(QueryExecutionError) as exc_info:
            self.template_service.render_template(template, parameters)
        
        assert "Template rendering error" in str(exc_info.value)
    
    def test_security_validation(self):
        """Test security validation against dangerous constructs."""
        dangerous_template = "SELECT * FROM users WHERE id = {{ config.DATABASE_URL }}"
        parameters = {"config": {"DATABASE_URL": "test"}}
        
        with pytest.raises(QueryExecutionError) as exc_info:
            self.template_service.render_template(dangerous_template, parameters)
        
        assert "Template processing error" in str(exc_info.value)
    
    def test_get_template_variables(self):
        """Test extracting template variables."""
        template = "SELECT * FROM users WHERE id = {{ user_id }} AND name = {{ name }}"
        variables = self.template_service.get_template_variables(template)
        
        assert "user_id" in variables
        assert "name" in variables


class TestQueryExecutionServiceWithTemplates:
    """Test cases for query execution service with Jinja templates."""
    
    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)
    
    @pytest.fixture
    def mock_connection(self):
        connection = AsyncMock()
        result = AsyncMock()
        result.returns_rows = True
        result.keys = ["id", "name", "email"]
        result.fetchall.return_value = [(1, "John", "john@example.com")]
        connection.execute.return_value = result
        return connection
    
    @pytest.fixture
    def service(self, mock_db):
        service = QueryExecutionService(mock_db)
        # Mock the connection manager
        service.connection_manager.get_connection = AsyncMock()
        return service
    
    async def test_execute_with_template(self, service, mock_connection):
        """Test executing a query with Jinja template."""
        service.connection_manager.get_connection.return_value = mock_connection
        
        sql = "SELECT * FROM users WHERE id = {{ user_id }}"
        parameters = {"user_id": 123}
        
        # Mock the datasource
        datasource = MagicMock()
        
        result = await service._execute_query(datasource, sql, parameters)
        
        # Verify the template was processed
        assert result.success is True
        assert result.data == [{"id": 1, "name": "John", "email": "john@example.com"}]
        
        # Verify the connection was called with processed SQL
        mock_connection.execute.assert_called_once()
        call_args = mock_connection.execute.call_args[0]
        assert "SELECT * FROM users WHERE id = 123" in call_args[0]
    
    async def test_execute_without_template(self, service, mock_connection):
        """Test executing a query without Jinja template."""
        service.connection_manager.get_connection.return_value = mock_connection
        
        sql = "SELECT * FROM users WHERE id = 123"
        parameters = {}
        
        # Mock the datasource
        datasource = MagicMock()
        
        result = await service._execute_query(datasource, sql, parameters)
        
        # Verify the query was executed as-is
        assert result.success is True
        
        # Verify the connection was called with original SQL
        mock_connection.execute.assert_called_once()
        call_args = mock_connection.execute.call_args[0]
        assert call_args[0] == sql
    
    def test_contains_jinja_syntax(self, service):
        """Test detection of Jinja syntax in SQL."""
        # Test with variable syntax
        assert service._contains_jinja_syntax("SELECT * FROM {{ table }}") is True
        
        # Test with control structure
        assert service._contains_jinja_syntax("{% if condition %}SELECT *{% endif %}") is True
        
        # Test with comment
        assert service._contains_jinja_syntax("{# comment #}SELECT *") is True
        
        # Test without Jinja syntax
        assert service._contains_jinja_syntax("SELECT * FROM users") is False
    
    async def test_missing_template_variables(self, service):
        """Test error handling for missing template variables."""
        sql = "SELECT * FROM users WHERE id = {{ user_id }}"
        parameters = {}  # Missing user_id
        
        # Mock the datasource
        datasource = MagicMock()
        
        with pytest.raises(QueryExecutionError) as exc_info:
            await service._execute_query(datasource, sql, parameters)
        
        assert "Missing required template variables" in str(exc_info.value)


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