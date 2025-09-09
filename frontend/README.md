# Cloud Storage UI

A modern cloud storage interface built with React, Next.js, Tailwind CSS, and shadcn/ui, designed to mimic Dropbox's interface with a clean, professional design.

## Features

### 🎨 Modern Design
- Clean, professional interface with subtle shadows and rounded corners
- Blue folder icons for directories
- Responsive layout optimized for desktop
- Professional color scheme (whites, grays, blues)
- Clear visual hierarchy with proper spacing

### 🧭 Interactive Navigation
- **Top Header Bar**: Logo, navigation title, help/support, notifications, and company branding
- **Left Sidebar**: Main navigation (Home, Data Sources, Tools) with dynamic file categories
- **Storage Usage**: Real-time storage indicator with progress bar
- **Dynamic Content**: Main content area that updates based on navigation selection

### 🔔 Interactive Elements
- Hover states for all interactive elements
- Notification badges (showing "17" notifications)
- Active state indicators for navigation
- Breadcrumb navigation
- File and folder listings with metadata

### 📁 File Management Interface
- Create button with plus icon
- "Suggested for you" section with personalized recommendations
- Dynamic breadcrumbs based on current location
- File/folder listings with icons, names, sizes, and modification dates
- Blue folder icons for directories

## Technology Stack

- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4
- **UI Components**: shadcn/ui
- **Icons**: Lucide React
- **State Management**: React useState hooks

## Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd cloud-storage-ui
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
src/
├── app/
│   ├── globals.css          # Global styles and Tailwind config
│   ├── layout.tsx           # Root layout
│   └── page.tsx             # Main page component
├── components/
│   ├── ui/                  # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── badge.tsx
│   │   ├── progress.tsx
│   │   ├── separator.tsx
│   │   └── avatar.tsx
│   └── CloudStorageLayout.tsx # Main layout component
└── lib/
    └── utils.ts             # Utility functions
```

## Key Components

### CloudStorageLayout
The main layout component that includes:
- **Header**: Logo, navigation title, action buttons, notifications, company branding
- **Sidebar**: Main navigation, file categories, storage usage
- **Main Content**: Action buttons, suggestions, breadcrumbs, file listings

### Navigation System
- **Main Navigation**: Home, Data Sources, Tools
- **File Categories**: Dynamic categories that change based on main navigation
- **Breadcrumbs**: Dynamic path navigation
- **Active States**: Visual indicators for current selection

## Customization

### Colors
The interface uses a professional color scheme:
- Primary blue: `#2563eb` (blue-600)
- Background: `#f9fafb` (gray-50)
- Cards: `#ffffff` (white)
- Borders: `#e5e7eb` (gray-200)

### Adding New Navigation Items
To add new navigation items, modify the `navigationItems` array in `CloudStorageLayout.tsx`:

```typescript
const navigationItems = [
  { id: 'home', label: 'Home', icon: Home },
  { id: 'data-sources', label: 'Data Sources', icon: Database },
  { id: 'tools', label: 'Tools', icon: Wrench },
  // Add new items here
];
```

### File Types
The interface supports different file types:
- Folders: Blue folder icons
- Files: Generic file icons with metadata (size, modification date)

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

### Adding New shadcn/ui Components

```bash
npx shadcn@latest add <component-name>
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

This project is licensed under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Acknowledgments

- Design inspired by Dropbox's interface
- Built with shadcn/ui components
- Icons from Lucide React
