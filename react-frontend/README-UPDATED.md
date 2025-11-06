# Claims AI Frontend - Updated

This is the modernized version of the Claims AI frontend, updated with components and UX patterns from the medical-claims-dashboard.

## What's New

### Modern UI Framework
- **Tailwind CSS**: Modern utility-first CSS framework
- **shadcn/ui Components**: High-quality, accessible React components
- **Lucide React Icons**: Beautiful, customizable icons
- **React Router**: Client-side routing for navigation

### New Pages and Components
1. **Dashboard Page** (`/dashboard`) - Modern claims overview with stats cards and filtering
2. **New Claim Form** (`/claims/new`) - Clean, step-by-step claim submission form
3. **Claim Detail Page** (`/claims/:id`) - Comprehensive claim details with collapsible sections
4. **Document Upload** (`/document-upload`) - Updated AI document processing interface

### UI Components Library
- Button, Card, Input, Label, Select, Textarea
- Badge, Collapsible, Toast notifications
- Progress indicators and status badges

### Features
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark/Light Theme Support**: CSS variables for theming
- **Modern Navigation**: Breadcrumbs and contextual navigation
- **Search and Filtering**: Real-time claim search and status filtering
- **Interactive Timeline**: Visual claim processing status
- **Collapsible Sections**: Organized information display

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm start
   ```

3. The application will be available at `http://localhost:3000`

## Routes

- `/dashboard` - Main claims dashboard (default)
- `/claims/new` - Submit new claim form
- `/claims/:id` - View claim details
- `/document-upload` - AI document processing

## Backend Integration

The frontend connects to the Python Flask backend at `http://localhost:8000`. Make sure the backend is running for full functionality.

## Development Notes

- Uses mock data for demonstration purposes
- Real API integration maintained for document processing
- Tailwind CSS configured with custom design system
- Component-based architecture for maintainability