# DMCP Frontend

A simple, responsive web interface for managing data source datasources in the DMCP system.

## Features

### Datasource Management
- **Datasource Listing**: View all datasources in an elegant card-based layout
- **Create/Edit Datasources**: Comprehensive form for managing datasource details
- **Test Connections**: Test data source connections directly from the UI
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Real-time Notifications**: Success/error feedback for all operations

### Tools Management
- **Tools Listing**: View all operation tools with type indicators (Query/HTTP/Code)
- **Create/Edit Tools**: Full-featured tool builder with SQL editor
- **Parameter Management**: Define typed parameters for dynamic operations
- **Execute Tools**: Test and run tools directly from the interface
- **Operation Templates**: Use parameter placeholders in SQL operations

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
   - **Data Source Type**: Choose from PostgreSQL, MySQL, SQLite, or Databricks
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