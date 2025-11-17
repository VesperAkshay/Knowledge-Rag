# Frontend Architecture

## 📁 Directory Structure

```
frontend/
├── app/
│   ├── page.tsx           # Main application entry point
│   ├── layout.tsx         # Root layout with metadata
│   └── globals.css        # Global styles and Tailwind
├── components/
│   ├── Header.tsx         # Animated header with stats
│   ├── chat/
│   │   ├── ChatContainer.tsx    # Message list with animations
│   │   ├── ChatMessage.tsx      # Individual message bubble
│   │   └── ChatInput.tsx        # Input field with auto-resize
│   ├── upload/
│   │   ├── UploadPanel.tsx      # Upload container
│   │   ├── FileUpload.tsx       # Drag & drop file upload
│   │   └── URLUpload.tsx        # URL scraping input
│   ├── workflow/
│   │   └── WorkflowVisualization.tsx  # React Flow diagram
│   └── ui/                # shadcn/ui components
│       ├── button.tsx
│       ├── card.tsx
│       ├── input.tsx
│       ├── textarea.tsx
│       ├── scroll-area.tsx
│       ├── badge.tsx
│       ├── tabs.tsx
│       └── skeleton.tsx
├── lib/
│   ├── hooks/
│   │   ├── useChat.ts           # Chat state management
│   │   ├── useKnowledgeBase.ts  # KB info fetching
│   │   └── index.ts             # Hook exports
│   ├── types/
│   │   └── index.ts             # TypeScript interfaces
│   └── utils.ts                 # Utility functions
└── package.json
```

## 🎨 Key Features

### Animation & Interactions
- **Framer Motion**: Smooth page transitions and micro-interactions
- **Animated Messages**: Staggered entry animations for chat messages
- **Loading States**: Pulsing dots, rotating spinners, scale effects
- **Hover Effects**: Interactive buttons and cards
- **Status Indicators**: Success/error animations with color transitions

### Components

#### Chat System
- `ChatContainer`: Empty state with welcome animation, message list with auto-scroll
- `ChatMessage`: Markdown rendering, copy button, timestamps, user/bot avatars
- `ChatInput`: Auto-resize textarea, character count, keyboard shortcuts

#### Upload System
- `FileUpload`: Drag & drop with status animations, file type validation
- `URLUpload`: URL validation, scraping progress, success feedback
- `UploadPanel`: Collapsible panel with smooth height transitions

#### Workflow
- `WorkflowVisualization`: Interactive React Flow diagram showing agent logic
- Nodes: User query → Orchestrator → KB Search / Web Search → Response
- Animated edges showing data flow

### Custom Hooks

#### `useChat`
```typescript
const { messages, loading, sendMessage, clearMessages } = useChat();
```
- Manages chat state and API communication
- Handles errors gracefully
- Provides loading states

#### `useKnowledgeBase`
```typescript
const { info, loading, refresh } = useKnowledgeBase();
```
- Fetches KB statistics
- Auto-refreshes every 30 seconds
- Manual refresh on upload

### Type System

All TypeScript interfaces in `lib/types/index.ts`:
- `Message`: Chat message with metadata
- `KnowledgeBaseInfo`: Document count and timestamps
- `UploadProgress`: File upload tracking
- `WorkflowStep`: Agent step visualization

## 🎯 Design Patterns

### Component Composition
```tsx
<Header>
  <UploadPanel>
    <FileUpload />
    <URLUpload />
  </UploadPanel>
</Header>

<Tabs>
  <ChatContainer>
    <ChatMessage />
  </ChatContainer>
  <ChatInput />
  
  <WorkflowVisualization />
</Tabs>
```

### State Management
- Local state with React hooks
- Custom hooks for reusable logic
- No global state (kept simple)

### Animation Strategy
1. **Enter animations**: Fade in + slide up
2. **Exit animations**: Fade out + slide down
3. **Loading states**: Continuous motion (rotate, pulse, scale)
4. **Success/Error**: Quick spring animations

## 🚀 Performance

- Code splitting with Next.js App Router
- Lazy loading for React Flow
- Optimized re-renders with `useCallback`
- Debounced auto-resize for textarea
- Virtualized scroll for long message lists (future)

## 🎨 Styling

### Tailwind Classes
- `bg-linear-to-*`: Gradients (Tailwind v4)
- `backdrop-blur-sm`: Frosted glass effects
- `shrink-0`: Flex item sizing
- Responsive: `sm:`, `md:`, `lg:` prefixes

### Theme System
- CSS variables for colors
- Dark mode support
- Primary/secondary color scheme
- Muted text hierarchy

## 📦 Dependencies

### Core
- `next@16`: React framework
- `react@19`: UI library
- `typescript`: Type safety

### UI & Animation
- `framer-motion`: Animations
- `@xyflow/react`: Flow diagrams
- `lucide-react`: Icons
- `tailwindcss@4`: Styling

### Content
- `react-markdown`: MD rendering
- `remark-gfm`: GitHub Flavored Markdown

### Components
- `@radix-ui/*`: Accessible primitives (via shadcn)

## 🔧 Development

```bash
# Run dev server
npm run dev

# Build for production
npm run build

# Type check
npm run type-check

# Lint
npm run lint
```

## 📝 Adding New Features

### New Component
1. Create in appropriate folder (`components/chat/`, `components/upload/`)
2. Add animations with Framer Motion
3. Use TypeScript interfaces from `lib/types`
4. Style with Tailwind + shadcn/ui

### New Hook
1. Create in `lib/hooks/`
2. Export from `lib/hooks/index.ts`
3. Add proper TypeScript types
4. Include error handling

### New API Integration
1. Add types to `lib/types/index.ts`
2. Create hook or API utility
3. Handle loading/error states
4. Add success animations

## 🎨 Animation Guidelines

- **Duration**: 0.2-0.5s for UI, 1-2s for loaders
- **Easing**: `ease-in-out` for smooth feel
- **Delay**: Stagger by 0.1s for lists
- **Scale**: 0.95-1.05 for emphasis
- **Opacity**: 0-1 for fades

## 🔐 Best Practices

✅ **Do**:
- Use TypeScript for all components
- Add loading states for async operations
- Provide user feedback (animations, toasts)
- Handle errors gracefully
- Keep components small and focused

❌ **Don't**:
- Inline large components
- Skip error handling
- Forget accessibility (aria labels)
- Over-animate (keep it subtle)
- Mutate state directly
