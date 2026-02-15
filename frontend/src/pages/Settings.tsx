import React, { useState } from 'react';
import { Navigation } from '../components/design-system/Navigation';
import { Sidebar } from '../components/design-system/Sidebar';
import { Button } from '../components/design-system/Button';

export function Settings() {
  const [activeTab, setActiveTab] = useState('account');
  const [toggles, setToggles] = useState({
    emailNotifications: true,
    smsNotifications: false,
    weeklyDigest: true,
    dataSharing: false,
  });

  const tabs = [
    { id: 'account', label: 'Account', icon: '👤' },
    { id: 'privacy', label: 'Privacy', icon: '🔒' },
    { id: 'integrations', label: 'Integrations', icon: '🔗' },
    { id: 'notifications', label: 'Notifications', icon: '🔔' },
    { id: 'billing', label: 'Billing', icon: '💳' },
  ];

  const handleToggle = (key: keyof typeof toggles) => {
    setToggles(prev => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Animated background elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-72 h-72 bg-cyan-500/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-40 right-10 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse" style={{animationDelay: '1s'}}></div>
      </div>

      <Navigation isAuthenticated={true} />

      <div className="flex relative z-10">
        <Sidebar isOpen={true} />

        <main className="flex-1 p-8">
          {/* Header */}
          <div className="mb-8 sticky-section">
            <h1 className="font-display text-5xl font-bold text-white mb-2">Settings</h1>
            <p className="text-slate-800 text-lg">Manage your account and preferences</p>
          </div>

          {/* Settings Container */}
          <div className="grid lg:grid-cols-4 gap-8">
            {/* Tab Navigation */}
            <div className="lg:col-span-1">
              <div className="space-y-2">
                {tabs.map((tab, idx) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full text-left px-4 py-3 rounded-lg transition-all flex items-center gap-3 font-medium ${
                      activeTab === tab.id
                        ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/50'
                        : 'text-black hover:bg-slate-800/50 border border-transparent'
                    }`}
                    style={{animation: `slide-in-left 0.5s ease-out ${idx * 0.05}s both`}}
                  >
                    <span>{tab.icon}</span>
                    {tab.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Settings Content */}
            <div className="lg:col-span-3">
              {/* Account Settings */}
              {activeTab === 'account' && (
                <div className="space-y-6">
                  <div className="premium-card rounded-2xl p-8 border-2 border-cyan-500/20">
                    <h2 className="font-display text-2xl font-bold text-white mb-6">Account Information</h2>

                    <div className="space-y-6">
                      <div>
                        <label className="block text-sm font-medium text-black mb-2">Full Name</label>
                        <input
                          type="text"
                          defaultValue="John Doe"
                          className="w-full px-4 py-3 rounded-lg bg-slate-800/50 border border-cyan-500/30 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-black mb-2">Email Address</label>
                        <input
                          type="email"
                          defaultValue="john@example.com"
                          className="w-full px-4 py-3 rounded-lg bg-slate-800/50 border border-cyan-500/30 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-black mb-2">Phone Number</label>
                        <input
                          type="tel"
                          defaultValue="+1 (555) 123-4567"
                          className="w-full px-4 py-3 rounded-lg bg-slate-800/50 border border-cyan-500/30 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-black mb-2">Company</label>
                        <input
                          type="text"
                          defaultValue="Tech Innovations Inc."
                          className="w-full px-4 py-3 rounded-lg bg-slate-800/50 border border-cyan-500/30 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                        />
                      </div>

                      <div className="flex gap-4">
                        <Button className="bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-600 hover:to-purple-700 text-white font-bold shadow-lg shadow-cyan-500/50">
                          Save Changes
                        </Button>
                        <Button variant="secondary" className="border-2 border-gray-600 text-black hover:bg-slate-700/50">
                          Cancel
                        </Button>
                      </div>
                    </div>
                  </div>

                  <div className="premium-card rounded-2xl p-8 border-2 border-red-500/20">
                    <h2 className="font-display text-2xl font-bold text-white mb-6">Danger Zone</h2>
                    <p className="text-slate-800 mb-4">Permanently delete your account and all associated data.</p>
                    <Button className="bg-red-500/20 hover:bg-red-500/30 text-red-300 border border-red-500/50 font-bold">
                      Delete Account
                    </Button>
                  </div>
                </div>
              )}

              {/* Privacy Settings */}
              {activeTab === 'privacy' && (
                <div className="premium-card rounded-2xl p-8 border-2 border-cyan-500/20">
                  <h2 className="font-display text-2xl font-bold text-white mb-6">Privacy & Security</h2>

                  <div className="space-y-6">
                    <div className="p-4 rounded-lg bg-slate-800/30 border border-cyan-500/10">
                      <div className="flex items-center justify-between mb-2">
                        <div>
                          <p className="font-semibold text-white">PII Redaction</p>
                          <p className="text-sm text-slate-800">Automatically redact sensitive information</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            defaultChecked
                            className="sr-only peer"
                          />
                          <div className="w-11 h-6 bg-cyan-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-cyan-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all"></div>
                        </label>
                      </div>
                    </div>

                    <div className="p-4 rounded-lg bg-slate-800/30 border border-cyan-500/10">
                      <div className="flex items-center justify-between mb-2">
                        <div>
                          <p className="font-semibold text-white">Two-Factor Authentication</p>
                          <p className="text-sm text-slate-800">Add an extra layer of security</p>
                        </div>
                        <Button className="bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 text-sm font-bold py-2">
                          Enable
                        </Button>
                      </div>
                    </div>

                    <div className="p-4 rounded-lg bg-slate-800/30 border border-cyan-500/10">
                      <div className="flex items-center justify-between mb-2">
                        <div>
                          <p className="font-semibold text-white">Audio Storage</p>
                          <p className="text-sm text-slate-800">Raw audio files are deleted after processing</p>
                        </div>
                        <span className="text-xs px-3 py-1 rounded-full bg-green-500/20 text-green-300">
                          ✓ Enabled
                        </span>
                      </div>
                    </div>

                    <div className="p-4 rounded-lg bg-slate-800/30 border border-cyan-500/10">
                      <h3 className="font-semibold text-white mb-3">Login Sessions</h3>
                      <div className="space-y-2">
                        <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded">
                          <div>
                            <p className="text-sm text-black">Chrome on macOS</p>
                            <p className="text-xs text-slate-800">Last active: 5 minutes ago</p>
                          </div>
                          <span className="text-xs px-2 py-1 rounded bg-green-500/20 text-green-300">Current</span>
                        </div>
                        <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded">
                          <div>
                            <p className="text-sm text-black">Safari on iPhone</p>
                            <p className="text-xs text-slate-800">Last active: 2 hours ago</p>
                          </div>
                          <button className="text-xs px-2 py-1 rounded hover:bg-red-500/20 text-red-400">Sign out</button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Integrations Settings */}
              {activeTab === 'integrations' && (
                <div className="premium-card rounded-2xl p-8 border-2 border-cyan-500/20">
                  <h2 className="font-display text-2xl font-bold text-white mb-6">Connected Integrations</h2>

                  <div className="space-y-4">
                    {[
                      { name: 'LinkedIn', connected: true, icon: '💼' },
                      { name: 'Google Calendar', connected: true, icon: '📅' },
                      { name: 'Slack', connected: false, icon: '💬' },
                      { name: 'HubSpot', connected: false, icon: '🎯' },
                    ].map((integration, idx) => (
                      <div
                        key={idx}
                        className="p-4 rounded-lg bg-slate-800/30 border border-cyan-500/10 flex items-center justify-between"
                        style={{animation: `slide-in-left 0.5s ease-out ${idx * 0.05}s both`}}
                      >
                        <div className="flex items-center gap-3">
                          <span className="text-2xl">{integration.icon}</span>
                          <p className="font-medium text-white">{integration.name}</p>
                        </div>
                        <Button className={integration.connected
                          ? 'bg-red-500/20 hover:bg-red-500/30 text-red-300 text-sm font-bold py-2'
                          : 'bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 text-sm font-bold py-2'
                        }>
                          {integration.connected ? 'Disconnect' : 'Connect'}
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Notifications Settings */}
              {activeTab === 'notifications' && (
                <div className="premium-card rounded-2xl p-8 border-2 border-cyan-500/20">
                  <h2 className="font-display text-2xl font-bold text-white mb-6">Notification Preferences</h2>

                  <div className="space-y-4">
                    <div className="p-4 rounded-lg bg-slate-800/30 border border-cyan-500/10 flex items-center justify-between">
                      <div>
                        <p className="font-semibold text-white">Email Notifications</p>
                        <p className="text-sm text-slate-800">Receive updates via email</p>
                      </div>
                      <button
                        onClick={() => handleToggle('emailNotifications')}
                        className={`relative inline-flex items-center cursor-pointer w-11 h-6 rounded-full transition-colors ${
                          toggles.emailNotifications ? 'bg-cyan-600' : 'bg-gray-600'
                        }`}
                      >
                        <span
                          className={`inline-block w-5 h-5 transform rounded-full bg-white transition-transform ${
                            toggles.emailNotifications ? 'translate-x-5' : 'translate-x-1'
                          }`}
                        ></span>
                      </button>
                    </div>

                    <div className="p-4 rounded-lg bg-slate-800/30 border border-cyan-500/10 flex items-center justify-between">
                      <div>
                        <p className="font-semibold text-white">SMS Notifications</p>
                        <p className="text-sm text-slate-800">Receive urgent alerts via SMS</p>
                      </div>
                      <button
                        onClick={() => handleToggle('smsNotifications')}
                        className={`relative inline-flex items-center cursor-pointer w-11 h-6 rounded-full transition-colors ${
                          toggles.smsNotifications ? 'bg-cyan-600' : 'bg-gray-600'
                        }`}
                      >
                        <span
                          className={`inline-block w-5 h-5 transform rounded-full bg-white transition-transform ${
                            toggles.smsNotifications ? 'translate-x-5' : 'translate-x-1'
                          }`}
                        ></span>
                      </button>
                    </div>

                    <div className="p-4 rounded-lg bg-slate-800/30 border border-cyan-500/10 flex items-center justify-between">
                      <div>
                        <p className="font-semibold text-white">Weekly Digest</p>
                        <p className="text-sm text-slate-800">Get a summary of your week</p>
                      </div>
                      <button
                        onClick={() => handleToggle('weeklyDigest')}
                        className={`relative inline-flex items-center cursor-pointer w-11 h-6 rounded-full transition-colors ${
                          toggles.weeklyDigest ? 'bg-cyan-600' : 'bg-gray-600'
                        }`}
                      >
                        <span
                          className={`inline-block w-5 h-5 transform rounded-full bg-white transition-transform ${
                            toggles.weeklyDigest ? 'translate-x-5' : 'translate-x-1'
                          }`}
                        ></span>
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* Billing Settings */}
              {activeTab === 'billing' && (
                <div className="space-y-6">
                  <div className="premium-card rounded-2xl p-8 border-2 border-cyan-500/20">
                    <h2 className="font-display text-2xl font-bold text-white mb-6">Billing & Plans</h2>

                    <div className="p-4 rounded-lg bg-slate-800/30 border border-cyan-500/10 mb-6">
                      <div className="flex items-center justify-between mb-3">
                        <p className="font-semibold text-white">Current Plan</p>
                        <span className="text-sm px-3 py-1 rounded-full bg-cyan-500/20 text-cyan-300 font-bold">Pro</span>
                      </div>
                      <p className="text-sm text-slate-800">$29/month • Renews on March 15, 2025</p>
                    </div>

                    <div className="grid md:grid-cols-3 gap-4 mb-6">
                      <div className="p-3 rounded-lg bg-slate-800/50 border border-cyan-500/10">
                        <p className="text-xs text-slate-800 mb-1">Conversations Used</p>
                        <p className="text-lg font-bold text-cyan-400">342 / 1000</p>
                      </div>
                      <div className="p-3 rounded-lg bg-slate-800/50 border border-cyan-500/10">
                        <p className="text-xs text-slate-800 mb-1">Storage Used</p>
                        <p className="text-lg font-bold text-cyan-400">2.3 GB / 100 GB</p>
                      </div>
                      <div className="p-3 rounded-lg bg-slate-800/50 border border-cyan-500/10">
                        <p className="text-xs text-slate-800 mb-1">Team Members</p>
                        <p className="text-lg font-bold text-cyan-400">1 / 5</p>
                      </div>
                    </div>

                    <div className="flex gap-4">
                      <Button className="bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-600 hover:to-purple-700 text-white font-bold shadow-lg shadow-cyan-500/50">
                        Upgrade Plan
                      </Button>
                      <Button variant="secondary" className="border-2 border-gray-600 text-black hover:bg-slate-700/50">
                        Manage Payment Method
                      </Button>
                    </div>
                  </div>

                  <div className="premium-card rounded-2xl p-8 border-2 border-cyan-500/20">
                    <h2 className="font-display text-2xl font-bold text-white mb-4">Billing History</h2>
                    <div className="space-y-2">
                      {[
                        { date: 'Feb 15, 2025', amount: '$29.00', status: 'Paid' },
                        { date: 'Jan 15, 2025', amount: '$29.00', status: 'Paid' },
                        { date: 'Dec 15, 2024', amount: '$29.00', status: 'Paid' },
                      ].map((invoice, idx) => (
                        <div
                          key={idx}
                          className="flex items-center justify-between p-3 bg-slate-800/30 rounded-lg"
                          style={{animation: `slide-in-left 0.5s ease-out ${idx * 0.05}s both`}}
                        >
                          <div>
                            <p className="text-sm text-black">{invoice.date}</p>
                          </div>
                          <div className="flex items-center gap-4">
                            <p className="font-semibold text-white">{invoice.amount}</p>
                            <span className="text-xs px-2 py-1 rounded bg-green-500/20 text-green-300">{invoice.status}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
