# Distributed Task System (DTS)

## Overview

The Distributed Task System (DTS) is a full-stack web application that manages distributed computing across multiple nodes. It features a React frontend with shadcn/ui components and an Express.js backend with PostgreSQL database integration via Drizzle ORM. The system enables peer discovery, task distribution, load balancing, and real-time monitoring of distributed computing resources.

## System Architecture

### Frontend Architecture
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite with custom configuration
- **UI Library**: shadcn/ui components built on Radix UI primitives
- **Styling**: Tailwind CSS with custom dark theme
- **State Management**: TanStack Query for server state management
- **Routing**: Wouter for lightweight client-side routing
- **Real-time Updates**: WebSocket connection for live system monitoring

### Backend Architecture
- **Runtime**: Node.js with Express.js framework
- **Database**: PostgreSQL with Drizzle ORM
- **Real-time Communication**: WebSocket Server for live updates
- **Task Execution**: Custom task executor with built-in operations
- **Peer Discovery**: Bonjour/mDNS-based service discovery
- **Security**: Custom security manager with encryption and digital signatures

### Key Components

#### Database Schema
- **Nodes Table**: Stores information about connected computing nodes (id, name, ip, port, status, load, capabilities)
- **Tasks Table**: Manages distributed tasks (id, name, status, nodeId, complexity, duration, result, error)
- **System Metrics Table**: Tracks performance metrics (nodeId, cpuUsage, memoryUsage, timestamp)
- **System Logs Table**: Centralized logging (level, message, source, nodeId, timestamp)

#### Services
- **OffloadSystem**: Orchestrates task distribution and peer management
- **PeerDiscovery**: Uses Bonjour protocol for automatic node discovery on the network
- **TaskExecutor**: Handles built-in tasks like matrix multiplication, prime calculation, and data processing
- **SecurityManager**: Manages payload encryption, digital signatures, and secure communication
- **SystemMonitor**: Tracks system performance and resource utilization

#### Frontend Components
- **Dashboard**: Main interface showing system overview and metrics
- **MetricsGrid**: Real-time system performance visualization
- **NodesTable**: Connected nodes management interface
- **TaskActivity**: Task execution monitoring and status tracking
- **SecurityPanel**: Security status indicators
- **SystemLogs**: Centralized log viewing interface

## Data Flow

1. **Node Registration**: Nodes automatically discover and register with the system via mDNS
2. **Task Submission**: Tasks are submitted through the web interface or API
3. **Load Balancing**: System evaluates node capacity and distributes tasks accordingly
4. **Task Execution**: Tasks are executed on selected nodes with real-time status updates
5. **Result Collection**: Results are collected and stored in the database
6. **Real-time Updates**: WebSocket connections push updates to connected clients

## External Dependencies

### Production Dependencies
- **Database**: @neondatabase/serverless for PostgreSQL connection
- **ORM**: drizzle-orm and drizzle-zod for database operations
- **UI Components**: @radix-ui/* packages for accessible UI primitives
- **Networking**: bonjour-service for peer discovery
- **Real-time**: ws (WebSocket) for live updates
- **Query Management**: @tanstack/react-query for server state
- **Session Management**: connect-pg-simple for session storage

### Development Dependencies
- **Build Tools**: Vite, esbuild for production builds
- **Type Safety**: TypeScript with strict configuration
- **Code Quality**: ESLint integration (implied by tsconfig)
- **Development Experience**: @replit/vite-plugin-runtime-error-modal and cartographer

## Deployment Strategy

### Development Mode
- Frontend served via Vite dev server with HMR
- Backend runs with tsx for TypeScript execution
- Database migrations handled via drizzle-kit push
- Automatic service discovery in local network

### Production Build
1. Frontend built with Vite to `dist/public`
2. Backend compiled with esbuild to `dist/index.js`
3. Single Node.js process serves both static files and API
4. PostgreSQL database connection via environment variables
5. WebSocket server integrated with HTTP server

### Environment Configuration
- `DATABASE_URL`: PostgreSQL connection string (required)
- `NODE_ENV`: Environment mode (development/production)
- `NODE_NAME`: Custom node identifier
- `SHARED_SECRET`: Security encryption key

## Changelog
- June 29, 2025. Initial setup
- June 29, 2025. Added broadcast messaging capability to send messages to all connected devices from the index page
  - Created broadcast_messages table in PostgreSQL database
  - Implemented API endpoints for sending and retrieving broadcast messages  
  - Added real-time WebSocket broadcasting to all connected clients
  - Created bilingual UI components with Arabic interface
  - Added navigation link in sidebar for easy access
  - Integrated with existing authentication and security systems

## User Preferences

Preferred communication style: Simple, everyday language.