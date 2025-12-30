# TrainerHub - Trainer Application

React-based trainer dashboard for managing clients, bookings, and packages.

## Tech Stack

- **Vite** - Fast build tool and dev server
- **React 18** - UI library
- **TypeScript** - Type safety
- **React Router** - Client-side routing
- **Zustand** - State management
- **Axios** - HTTP client
- **TailwindCSS** - Styling
- **shadcn/ui** - UI components
- **Lucide React** - Icons

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Django backend running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at `http://localhost:3000`

### Build for Production

```bash
# Create production build
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
src/
├── api/              # API client and service functions
│   ├── client.ts     # Axios client configuration
│   ├── auth.ts       # Authentication API
│   ├── clients.ts    # Clients API
│   ├── bookings.ts   # Bookings API
│   └── packages.ts   # Packages API
├── components/
│   └── ui/           # shadcn/ui components
├── layouts/          # Layout components
│   └── DashboardLayout.tsx
├── pages/            # Page components
│   ├── LoginPage.tsx
│   ├── RegisterPage.tsx
│   ├── DashboardPage.tsx
│   ├── ClientsPage.tsx
│   ├── BookingsPage.tsx
│   ├── PackagesPage.tsx
│   └── SettingsPage.tsx
├── store/            # Zustand stores
│   ├── authStore.ts
│   └── subscriptionStore.ts
├── types/            # TypeScript type definitions
│   └── index.ts
├── lib/              # Utility functions
│   └── utils.ts
├── App.tsx           # Main app component with routing
└── main.tsx          # Entry point
```

## Features

### Authentication (Epic 1.2) ✅
- Login with email/password
- Registration for new trainers
- Token-based authentication
- Persistent auth state with Zustand
- Protected routes

### Dashboard Layout ✅
- Sidebar navigation
- User info display
- Logout functionality
- Responsive design

### Pages (Placeholders)
- Dashboard overview
- Clients management
- Bookings calendar
- Packages management
- Settings

## Environment Variables

Create a `.env` file in the root directory:

```env
VITE_API_URL=http://localhost:8000/api
```

## API Integration

The app communicates with the Django backend via REST API:

- **Base URL**: `http://localhost:8000/api`
- **Authentication**: Token-based (stored in localStorage)
- **Endpoints**:
  - `/users/login/` - Login
  - `/users/register/` - Registration
  - `/users/me/` - Get current user
  - `/clients/` - Client management
  - `/bookings/` - Booking management
  - `/packages/` - Package management

## Development

### Adding New Components

Use shadcn/ui CLI or manually create components in `src/components/ui/`:

```bash
# Example: Add a new component
# Create the file manually or use shadcn CLI when available
```

### State Management

Use Zustand for global state:

```typescript
import { useAuthStore } from '@/store/authStore';

function MyComponent() {
  const { user, login, logout } = useAuthStore();
  // ...
}
```

### API Calls

Use the API client:

```typescript
import { clientsApi } from '@/api';

const clients = await clientsApi.list();
const client = await clientsApi.get(id);
```

## Next Steps

- [ ] Implement full client management (CRUD)
- [ ] Add booking calendar view
- [ ] Create package management interface
- [ ] Add subscription management
- [ ] Implement page builder
- [ ] Add white-label settings
- [ ] Custom domain configuration

## License

Proprietary - TrainerHub Platform
