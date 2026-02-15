// ABOUTME: Main app component with routing
// ABOUTME: Sets up React Router for navigation between pages

import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ConversationList } from './pages/ConversationList';
import { ConversationDetail } from './pages/ConversationDetail';

export function App() {
  return (
    <BrowserRouter>
      <div style={{ minHeight: '100vh', background: '#f3f4f6' }}>
        <Routes>
          <Route path="/" element={<ConversationList />} />
          <Route path="/conversations/:id" element={<ConversationDetail />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
