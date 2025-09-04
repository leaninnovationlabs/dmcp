# DataSources Component

This component converts the original HTML-based datasource page to a React component with full functionality.

## Features

- **List Data Sources**: Displays all configured data sources in a responsive grid layout
- **Test Connections**: Test database connections with visual feedback
- **Add New Data Source**: Button to navigate to the data source creation page
- **Error Handling**: Proper error states and loading states
- **Authentication**: Integrated with the existing authentication system
- **Responsive Design**: Works on desktop and mobile devices

## Component Structure

```
src/modules/data-sources/
├── DataSources.tsx    # Main component
├── index.ts          # Export file
└── README.md         # This file
```

## API Integration

The component uses the centralized API service (`src/services/api.ts`) for:
- Fetching data sources list
- Testing database connections
- Authentication management

## Styling

Uses Tailwind CSS classes for consistent styling with the rest of the application. The design matches the original HTML page with modern React patterns.

## Usage

The component is automatically integrated into the main application through the Layout component. Users can access it by clicking "Data Sources" in the sidebar navigation.

## State Management

- `datasources`: Array of data source objects
- `loading`: Boolean for loading state
- `error`: Error message string
- `notifications`: Array of notification objects
- `testingConnection`: ID of the data source being tested

## Database Types Supported

- PostgreSQL
- MySQL
- SQLite
- Databricks

Each database type is displayed with appropriate styling and icons.
