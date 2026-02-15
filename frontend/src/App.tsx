// ABOUTME: Main app component with routing
// ABOUTME: Sets up React Router for navigation between pages

import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import { ConversationList } from './pages/ConversationList';
import { ConversationDetail } from './pages/ConversationDetail';
import { ConversationForm } from './pages/ConversationForm';
import { AskQuestions } from './pages/AskQuestions';

function Navigation() {
  const location = useLocation();

  const isActive = (path: string) => {
    return location.pathname === path || location.pathname.startsWith(path);
  };

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex space-x-8">
            <Link
              to="/"
              className="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
              style={{
                borderBottomColor: isActive('/') && !location.pathname.includes('conversation') ? '#3b82f6' : 'transparent',
                color: isActive('/') && !location.pathname.includes('conversation') ? '#3b82f6' : '#6b7280',
              }}
            >
              Conversations
            </Link>
            <Link
              to="/ask"
              className="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
              style={{
                borderBottomColor: isActive('/ask') ? '#3b82f6' : 'transparent',
                color: isActive('/ask') ? '#3b82f6' : '#6b7280',
              }}
            >
              Ask Questions
            </Link>
          </div>
          <div className="flex items-center">
            <Link
              to="/conversations/new"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
            >
              New Conversation
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}

export function App() {
  return (
    <BrowserRouter>
      <div style={{ minHeight: '100vh', background: '#f3f4f6' }}>
        <Navigation />
        <Routes>
          <Route path="/" element={<ConversationList />} />
          <Route path="/conversations/new" element={<ConversationForm />} />
          <Route path="/conversations/:id" element={<ConversationDetail />} />
          <Route path="/conversations/:id/edit" element={<ConversationForm />} />
          <Route path="/ask" element={<AskQuestions />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
