# 🚀 Quick Start - View Agent-Echo Prototypes

## 5-Minute Setup

### Step 1: Navigate to Frontend
```bash
cd /Users/harshimsaluja/Documents/GitHub/Aperta/frontend
```

### Step 2: Install Dependencies (if not already done)
```bash
npm install
```

### Step 3: Update App.tsx
Replace the entire Routes section in `frontend/src/App.tsx` with this:

```tsx
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Landing } from './pages/Landing';
import { Dashboard } from './pages/Dashboard';
import { Events } from './pages/Events';
import { EventDetail } from './pages/EventDetail';
import { KnowledgeGraph } from './pages/KnowledgeGraph';
import { ConversationList } from './pages/ConversationList';
import { ConversationDetail } from './pages/ConversationDetail';
import { ConversationForm } from './pages/ConversationForm';
import { AskQuestions } from './pages/AskQuestions';

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* New UI/UX Prototypes */}
        <Route path="/" element={<Landing />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/events" element={<Events />} />
        <Route path="/events/:id" element={<EventDetail />} />
        <Route path="/knowledge-graph" element={<KnowledgeGraph />} />

        {/* Existing Features */}
        <Route path="/old" element={<ConversationList />} />
        <Route path="/conversations/new" element={<ConversationForm />} />
        <Route path="/conversations/:id" element={<ConversationDetail />} />
        <Route path="/conversations/:id/edit" element={<ConversationForm />} />
        <Route path="/ask" element={<AskQuestions />} />
      </Routes>
    </BrowserRouter>
  );
}
```

### Step 4: Start Dev Server
```bash
npm run dev
```

### Step 5: Open in Browser
```
http://localhost:5173/
```

---

## 📖 What You'll See

### Landing Page
**URL**: `http://localhost:5173/`
- Hero section with brand gradient
- 6 feature cards
- How It Works timeline
- Privacy section
- Navigation with login/dashboard buttons

### Dashboard
**URL**: `http://localhost:5173/dashboard`
- Top navigation bar
- Left sidebar with menu
- 4 metric cards (People Met, Conversations, etc.)
- Activity feed
- AI Assistant sidebar on right
- All interactive and responsive

### Events
**URL**: `http://localhost:5173/events`
- Search bar
- View mode toggles (list/grid)
- Event list with metadata
- Click-to-view cards
- Fully responsive grid

### Event Detail
**URL**: `http://localhost:5173/events/1`
- 6 tabs: People • Conversations • LinkedIn • Insights • Graph • Analytics
- Each tab has fully populated demo content
- Person cards with details
- Conversation items
- LinkedIn suggestions
- AI insights section
- Analytics placeholder

### Knowledge Graph
**URL**: `http://localhost:5173/knowledge-graph`
- Left sidebar with filters
- Center graph canvas (dark background)
- Right sidebar with node details
- Interactive filter checkboxes
- Search functionality

---

## 🎨 Design System in Action

All prototypes use:
- **Brand Colors**: Blue (#1F3C88) + Cyan (#00C2FF)
- **Typography**: DM Sans (headings), Inter (body), JetBrains Mono (code)
- **Spacing**: Consistent 8px grid system
- **Shadows**: Multi-level elevation system
- **Animations**: Smooth transitions and hover effects

---

## 🔍 Key Things to Look For

✅ **Visual Consistency**
- Same color scheme across all pages
- Consistent spacing and typography
- Unified button and card styles

✅ **Responsive Design**
- Resize browser window
- Sidebar collapses on mobile
- Cards stack vertically
- Navigation adapts

✅ **Interactive Elements**
- Hover effects on cards
- Tab switching (Event Detail)
- Dropdown selects
- Filter checkboxes

✅ **Information Architecture**
- Clear navigation hierarchy
- Logical content grouping
- Smart use of space
- Emphasis on important info

---

## 🛠️ Troubleshooting

### Port already in use?
```bash
# Kill process on port 5173
lsof -ti:5173 | xargs kill -9
npm run dev
```

### Styles not loading?
```bash
# Clear cache and rebuild
rm -rf node_modules/.vite
npm run dev
```

### TypeScript errors?
Just ignore them - they won't affect the dev server. We'll fix any type issues before production build.

---

## 📝 File Reference

**Prototypes Location:**
```
frontend/src/pages/
├── Landing.tsx       ← Landing page
├── Dashboard.tsx     ← Dashboard home
├── Events.tsx        ← Events list
├── EventDetail.tsx   ← Event detail with tabs
└── KnowledgeGraph.tsx ← Knowledge graph
```

**Design System:**
```
frontend/src/
├── components/design-system/
│   ├── Button.tsx
│   ├── Card.tsx
│   ├── Navigation.tsx
│   └── Sidebar.tsx
└── index.css         ← Design tokens & colors
```

---

## 💬 Next Steps

After viewing:

1. **Give Feedback On:**
   - Layout and information architecture
   - Colors and visual hierarchy
   - Component sizing
   - Navigation flows
   - Responsive behavior

2. **Then We'll:**
   - Refine any elements you want adjusted
   - Add interactive graph visualization
   - Create remaining pages (Transcripts, Analytics, Settings, Auth)
   - Implement real API integration
   - Add animations and micro-interactions

---

## ⚡ Quick Navigation

Once running, here's the URL pattern:
- `/` → Landing
- `/dashboard` → Dashboard home
- `/events` → Events list
- `/events/1` → Event detail
- `/knowledge-graph` → Knowledge graph

---

## ✨ Enjoy!

The prototypes are fully functional and ready to explore. Click around, test responsiveness, and let me know what you'd like to adjust before we move to full implementation!

**Happy reviewing!** 🎉
