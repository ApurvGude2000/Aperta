import React from 'react';
import { Navigation } from '../components/design-system/Navigation';
import { Card } from '../components/design-system/Card';

export function Settings() {
  return (
    <div className="min-h-screen bg-[#F5F7FA]">
      <Navigation isAuthenticated={true} />

      <main className="max-w-7xl mx-auto p-8">
          <h1 className="font-display text-3xl font-bold text-[#121417] mb-2">Settings</h1>
          <p className="text-[#6B7280] mb-8">Manage your account and preferences</p>

          <div className="space-y-6">
            <Card>
              <h2 className="font-bold text-lg text-[#121417] mb-4">Account Settings</h2>
              <p className="text-[#6B7280]">Account settings coming soon...</p>
            </Card>

            <Card>
              <h2 className="font-bold text-lg text-[#121417] mb-4">Preferences</h2>
              <p className="text-[#6B7280]">Preferences coming soon...</p>
            </Card>

            <Card>
              <h2 className="font-bold text-lg text-[#121417] mb-4">Integrations</h2>
              <p className="text-[#6B7280]">Integrations coming soon...</p>
            </Card>
          </div>
      </main>
    </div>
  );
}
