# DMCP Frontend

A simple, responsive web interface for managing database datasources in the DMCP system.

## Features

### Datasource Management
- **Datasource Listing**: View all datasources in an elegant card-based layout
- **Create/Edit Datasources**: Comprehensive form for managing datasource details
- **Test Connections**: Test database connections directly from the UI
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Real-time Notifications**: Success/error feedback for all operations

### Tools Management
- **Tools Listing**: View all SQL tools with type indicators (Query/HTTP/Code)
- **Create/Edit Tools**: Full-featured tool builder with SQL editor
- **Parameter Management**: Define typed parameters for dynamic queries
- **Execute Tools**: Test and run tools directly from the interface
- **Query Templates**: Use parameter placeholders in SQL queries

## Files Structure

```
frontend/
├── index.html              # Main datasource listing page
├── edit.html              # Create/edit datasource form
├── tools.html             # Tools listing page
├── tools-edit.html        # Create/edit tool form
├── script.js              # JavaScript for datasource listing
├── edit-script.js         # JavaScript for datasource editing
├── tools-script.js        # JavaScript for tools listing
├── tools-edit-script.js   # JavaScript for tools editing
├── README.md             # This file
└── tools-README.md       # Detailed tools documentation
```

## Setup

1. **Start the DMCP Server**: Make sure your DMCP server is running on `http://localhost:8000`

2. **Serve the Frontend**: You can serve the frontend files using any static file server:

   **Option A: Python HTTP Server**
   ```bash
   cd frontend
   python3 -m http.server 3000
   ```

   **Option B: Node.js http-server**
   ```bash
   npm install -g http-server
   cd frontend
   http-server -p 3000
   ```

   **Option C: PHP Development Server**
   ```bash
   cd frontend
   php -S localhost:3000
   ```

3. **Access the Application**: Open your browser and navigate to `http://localhost:3000`

## Usage

### Datasource Management

#### Listing Datasources

1. Open `index.html` in your browser
2. View all existing datasources in card format
3. Each card shows:
   - Datasource name and type
   - Connection details (host, database, username)
   - Creation date
   - Test connection button
4. Click on any card to edit the datasource
5. Use "View Tools →" to navigate to tools management

#### Creating a New Datasource

1. Click the "Add New Datasource" button
2. Fill in the required fields:
   - **Name**: Unique identifier for the datasource
   - **Database Type**: Choose from PostgreSQL, MySQL, or SQLite
   - **Database Name**: Name of the database
3. Optionally fill in connection details:
   - Host and Port
   - Username and Password
   - Connection String (overrides individual parameters)
   - SSL Mode
   - Additional Parameters (JSON format)
4. Click "Create Datasource" to save

#### Editing an Existing Datasource

1. Click on any datasource card from the main list
2. Modify the fields as needed
3. Use the "Test Connection" button to verify connectivity
4. Click "Save Datasource" to update
5. Use "Delete" to remove the datasource (with confirmation)

#### Testing Connections

- From the listing page: Click the connection test icon on any card
- From the edit page: Click the "Test Connection" button (only available for existing datasources)

### Tools Management

#### Viewing Tools

1. Navigate to `tools.html` or click "View Tools →" from datasources page
2. View all tools in card format with:
   - Tool name and type (Query 🔍, HTTP 🌐, Code ⚙️)
   - Description and datasource name
   - Parameter count and SQL preview
   - Quick execute button
3. Click cards to edit tools or use execute button to run them

#### Creating Tools

1. Click "+ Add New Tool" button
2. Fill in basic information (name, type, description, datasource)
3. Write SQL query with parameter placeholders: `{{ parameter_name }}`
4. Define parameters with types (string, integer, date, etc.)
5. Set required/optional status and default values
6. Save the tool

#### Managing Tool Parameters

- **Add Parameters**: Click "+ Add Parameter" button
- **Parameter Types**: string, integer, float, boolean, date, datetime, array, object
- **Parameter Usage**: Use `{{ param_name }}` in SQL queries
- **Validation**: Required parameters must be provided when executing
- **Examples**: `SELECT * FROM users WHERE created_date > {{ start_date }}`

For detailed tools documentation, see [tools-README.md](tools-README.md).

## API Integration

The frontend communicates with the DMCP API using these endpoints:

### Datasource APIs
- `GET /dmcp/datasources` - List all datasources
- `GET /dmcp/datasources/{id}` - Get specific datasource
- `POST /dmcp/datasources` - Create new datasource
- `PUT /dmcp/datasources/{id}` - Update existing datasource
- `DELETE /dmcp/datasources/{id}` - Delete datasource
- `POST /dmcp/datasources/{id}/test` - Test connection

### Tools APIs
- `GET /dmcp/tools` - List all tools
- `GET /dmcp/tools/{id}` - Get specific tool
- `POST /dmcp/tools` - Create new tool
- `PUT /dmcp/tools/{id}` - Update existing tool
- `DELETE /dmcp/tools/{id}` - Delete tool
- `POST /dmcp/execute/{tool_id}` - Execute tool with parameters

## Browser Compatibility

- Modern browsers with ES6+ support
- Chrome 60+
- Firefox 60+
- Safari 12+
- Edge 79+

## Dependencies

- **TailwindCSS**: Loaded via CDN for styling
- **jQuery**: Loaded via CDN for DOM manipulation and AJAX

## Customization

### Changing the API Base URL

If your DMCP server runs on a different URL, update the `API_BASE_URL` constant in both JavaScript files:

```javascript
const API_BASE_URL = 'http://your-server:port/dmcp';
```

### Styling

The UI uses TailwindCSS for styling. You can customize the appearance by:

1. Modifying the Tailwind classes in the HTML files
2. Adding custom CSS for additional styling needs

## Troubleshooting

### CORS Issues
If you encounter CORS errors, make sure your DMCP server allows requests from your frontend domain.

### Connection Refused
Ensure the DMCP server is running and accessible at the configured URL.

### Form Validation
Required fields are marked with a red asterisk (*). The form will highlight invalid fields in red.

## Contributing

Feel free to enhance the UI by:
- Adding more database type support
- Improving responsive design
- Adding data visualization features
- Implementing advanced filtering/search 