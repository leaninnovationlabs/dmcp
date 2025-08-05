import asyncio
from typing import Dict, Any, List, Tuple
import logging
from databricks import sql
from databricks.sql import connect

from .base import DatabaseConnection
from ..models.database import Datasource

logger = logging.getLogger(__name__)


class DatabricksConnection(DatabaseConnection):
    
    def _convert_databricks_types(self, value):
        """Convert Databricks-specific types to JSON-serializable formats."""
        # Handle any Databricks-specific types that might not be JSON serializable
        if hasattr(value, '__class__') and hasattr(value, '__module__'):
            module = getattr(value, '__module__', '')
            if 'databricks' in module:
                # Convert any Databricks-specific types to string
                return str(value)
        
        return value
    
    def _convert_parameters(self, sql: str, parameters: Dict[str, Any]) -> Tuple[str, List[Any]]:
        """Convert named parameters to Databricks positional parameters."""
        if not parameters:
            return sql, []
        
        # Replace named parameters with positional parameters
        param_keys = list(parameters.keys())
        for i, key in enumerate(param_keys):
            sql = sql.replace(f":{key}", "?")
        
        return sql, list(parameters.values())
    
    async def _execute_query(self, sql: str, param_values: List[Any]) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Execute Databricks query and return results with column names."""
        # Since databricks-sql-connector is synchronous, we need to run it in a thread pool
        loop = asyncio.get_event_loop()
        
        def execute_sync():
            cursor = self.connection.cursor()
            cursor.execute(sql, param_values)
            result = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            cursor.close()
            return result, columns
        
        raw_result, columns = await loop.run_in_executor(None, execute_sync)
        
        # Convert results to list of dictionaries
        if raw_result and columns:
            data = []
            for row in raw_result:
                row_dict = {}
                for i, value in enumerate(row):
                    row_dict[columns[i]] = self._convert_databricks_types(value)
                data.append(row_dict)
        else:
            data = []
        
        return data, columns
    
    def _process_results(self, raw_result: List[Dict[str, Any]], columns: List[str]) -> List[Dict[str, Any]]:
        """Databricks results are already processed by _execute_query."""
        return raw_result
    
    async def close(self):
        """Close the Databricks connection."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.connection.close)

    @classmethod
    async def create(cls, datasource: Datasource) -> 'DatabricksConnection':
        """Create a new Databricks connection."""
        try:
            # Build connection parameters
            connection_params = {
                'server_hostname': datasource.host,
                'http_path': datasource.additional_params.get('http_path', '/sql/1.0/warehouses/default'),
                'access_token': datasource.decrypted_password,
            }
            
            # Add catalog and schema if specified
            if datasource.additional_params.get('catalog'):
                connection_params['catalog'] = datasource.additional_params['catalog']
            if datasource.additional_params.get('schema'):
                connection_params['schema'] = datasource.additional_params['schema']
            
            # Add additional parameters
            for key, value in datasource.additional_params.items():
                if key not in ['http_path', 'catalog', 'schema']:
                    connection_params[key] = value
            
            # Create connection in a thread pool since databricks-sql-connector is synchronous
            loop = asyncio.get_event_loop()
            
            def create_sync():
                return connect(**connection_params)
            
            connection = await loop.run_in_executor(None, create_sync)
            
            return cls(connection)
        except Exception as e:
            cls._handle_connection_error(datasource, e) 