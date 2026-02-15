import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/design-system/Button';
import { Card, FeatureCard } from '../components/design-system/Card';

export function LandingEnhanced() {
  const features = [
    {
      icon: '⚡',
      title: 'Real-time Transcription',
      description: 'Capture conversations automatically with AI-powered speech-to-text',
      color: 'from-orange-400 to-pink-500',
    },
    {
      icon: '🕸️',
      title: 'Knowledge Graph',
      description: 'Visualize connections between people, topics, and organizations',
      color: 'from-cyan-400 to-blue-500',
    },
    {
      icon: '🧠',
      title: 'AI Agents',
      description: 'Privacy Guardian, Context Understanding, Follow-Up suggestions, and more',
      color: 'from-purple-400 to-pink-500',
    },
    {
      icon: '📈',
      title: 'Analytics',
      description: 'Track networking effectiveness and conversation insights',
      color: 'from-green-400 to-teal-500',
    },
    {
      icon: '🔒',
      title: 'Privacy First',
      description: 'Automatic PII redaction and enterprise-grade data protection',
      color: 'from-blue-400 to-cyan-500',
    },
    {
      icon: '💬',
      title: 'Smart Follow-ups',
      description: 'Auto-generate personalized follow-up messages and reminders',
      color: 'from-yellow-400 to-orange-500',
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 overflow-hidden">
      {/* Animated background elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-72 h-72 bg-cyan-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-40 right-10 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-pulse" style={{animationDelay: '1s'}}></div>
        <div className="absolute top-1/2 right-1/4 w-80 h-80 bg-pink-500/10 rounded-full blur-3xl animate-pulse" style={{animationDelay: '2s'}}></div>
      </div>

      {/* Navigation */}
      <nav className="sticky top-0 z-50 backdrop-blur-lg bg-slate-900/50 border-b border-cyan-500/20">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3 font-display font-bold text-2xl">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-400 to-purple-500 flex items-center justify-center text-white shadow-lg shadow-cyan-500/50 transform hover:scale-110 transition-transform">
                🤖
              </div>
              <span className="text-white neon-text">Agent-Echo</span>
            </div>

            <div className="hidden md:flex items-center gap-8">
              <a href="#features" className="text-sm font-medium text-gray-300 hover:text-cyan-400 transition-colors">
                Features
              </a>
              <a href="#how-it-works" className="text-sm font-medium text-gray-300 hover:text-cyan-400 transition-colors">
                How It Works
              </a>
              <a href="#privacy" className="text-sm font-medium text-gray-300 hover:text-cyan-400 transition-colors">
                Privacy
              </a>
            </div>

            <div className="flex items-center gap-4">
              <Link to="/login" className="text-sm font-medium text-gray-300 hover:text-cyan-400 transition-colors">
                Login
              </Link>
              <Link
                to="/dashboard"
                className="px-6 py-2 bg-gradient-to-r from-cyan-500 to-purple-600 text-white text-sm font-bold rounded-lg hover:shadow-lg hover:shadow-cyan-500/50 transition-all transform hover:scale-105"
              >
                Dashboard
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative max-w-7xl mx-auto px-6 py-32 flex items-center justify-between">
        <div className="flex-1 z-10">
          <h1 className="font-display text-6xl lg:text-7xl font-bold text-white mb-6 leading-tight" style={{animation: 'fadeInUp 0.8s ease-out'}}>
            Turn <span className="bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent animate-pulse">Conversations</span> into <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400 bg-clip-text text-transparent">Connections</span>
          </h1>
          <p className="text-xl text-gray-300 mb-8 max-w-2xl font-body leading-relaxed" style={{animation: 'fadeInUp 0.8s ease-out 0.2s both'}}>
            AI-powered networking assistant that captures conversations, builds knowledge graphs, and automates follow-ups—all while keeping your data private.
          </p>
          <div className="flex gap-4" style={{animation: 'fadeInUp 0.8s ease-out 0.4s both'}}>
            <Link to="/dashboard">
              <Button size="lg" className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white font-bold shadow-lg shadow-cyan-500/50 transform hover:scale-110">
                Get Started →
              </Button>
            </Link>
            <Button variant="secondary" size="lg" className="border-2 border-purple-400 text-purple-300 hover:bg-purple-500/10 font-bold">
              Learn More
            </Button>
          </div>
        </div>

        {/* Floating 3D Element */}
        <div className="hidden lg:flex flex-1 justify-end items-center">
          <div className="relative w-96 h-96">
            <div className="absolute inset-0 rounded-3xl bg-gradient-to-br from-cyan-500/20 to-purple-500/20 backdrop-blur-3xl border border-cyan-500/30 float-animate shadow-3d flex items-center justify-center">
              <div className="text-9xl opacity-80 animate-spin" style={{animationDuration: '15s'}}>🕸️</div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section with Grid */}
      <section id="features" className="relative max-w-7xl mx-auto px-6 py-32">
        <div className="text-center mb-20 sticky-section">
          <h2 className="font-display text-5xl font-bold text-white mb-4">Powerful Features</h2>
          <p className="text-xl text-gray-400">Everything you need for intelligent networking</p>
        </div>

        {/* Feature Grid with 3D Cards */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, idx) => (
            <div
              key={idx}
              className="group relative"
              style={{animation: `slide-in-left 0.8s ease-out ${idx * 0.1}s both`}}
            >
              <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/20 to-purple-500/20 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              <div className="relative premium-card rounded-2xl p-8 border-2 border-cyan-500/10 h-full">
                <div className={`w-16 h-16 rounded-full bg-gradient-to-br ${feature.color} flex items-center justify-center text-3xl mb-4 shadow-lg transform group-hover:scale-125 transition-transform`}>
                  {feature.icon}
                </div>
                <h3 className="text-2xl font-bold text-white mb-2">{feature.title}</h3>
                <p className="text-gray-400 leading-relaxed">{feature.description}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* How It Works - Timeline */}
      <section id="how-it-works" className="relative max-w-7xl mx-auto px-6 py-32">
        <div className="text-center mb-20">
          <h2 className="font-display text-5xl font-bold text-white mb-4">How It Works</h2>
        </div>

        <div className="grid md:grid-cols-4 gap-8 relative">
          {/* Connecting line */}
          <div className="hidden md:block absolute top-24 left-0 right-0 h-1 bg-gradient-to-r from-cyan-500 via-purple-500 to-pink-500 opacity-30"></div>

          {[
            { step: 1, title: 'Record', desc: 'Start recording your conversations', icon: '🎤' },
            { step: 2, title: 'Process', desc: 'AI processes and transcribes instantly', icon: '⚙️' },
            { step: 3, title: 'Connect', desc: 'Identify people and topics automatically', icon: '🔗' },
            { step: 4, title: 'Follow Up', desc: 'Generate smart follow-up actions', icon: '📧' },
          ].map((item, idx) => (
            <div
              key={item.step}
              className="relative"
              style={{animation: `bounce-in 0.8s ease-out ${idx * 0.15}s both`}}
            >
              <div className="text-center">
                <div className="w-24 h-24 rounded-full bg-gradient-to-br from-cyan-500 to-purple-600 text-white flex items-center justify-center font-display font-bold text-3xl mx-auto mb-4 shadow-lg shadow-cyan-500/50 transform hover:scale-110 transition-transform">
                  {item.icon}
                </div>
                <h3 className="font-bold text-2xl text-white mb-2">{item.title}</h3>
                <p className="text-gray-400">{item.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Privacy Assurance - Glass Morphism */}
      <section id="privacy" className="relative max-w-7xl mx-auto px-6 py-32">
        <div className="glass rounded-3xl overflow-hidden border border-cyan-500/30 shadow-3d">
          <div className="bg-gradient-to-br from-cyan-500/20 via-purple-500/10 to-pink-500/20 p-12 md:p-20">
            <div className="text-center mb-16">
              <h2 className="font-display text-5xl font-bold text-white mb-4">Your Privacy, Our Priority</h2>
              <p className="text-xl text-gray-300">Enterprise-grade security meets user convenience</p>
            </div>

            <div className="grid md:grid-cols-3 gap-8">
              {[
                { title: 'On-Device Processing', desc: 'Audio processed locally on your device', icon: '📱' },
                { title: 'Zero Audio Storage', desc: 'We never store your recordings', icon: '🔐' },
                { title: 'Enterprise Security', desc: 'Bank-level encryption and compliance', icon: '🏦' },
              ].map((item, idx) => (
                <div
                  key={idx}
                  className="text-center transform hover:scale-105 transition-transform"
                  style={{animation: `slide-in-right 0.8s ease-out ${idx * 0.1}s both`}}
                >
                  <div className="text-5xl mb-4">{item.icon}</div>
                  <h3 className="font-bold text-xl text-white mb-2">{item.title}</h3>
                  <p className="text-gray-300">{item.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-cyan-500/20 bg-slate-900/80 backdrop-blur py-12 mt-32">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid md:grid-cols-4 gap-12 mb-12">
            <div>
              <h4 className="font-bold text-white mb-4">Company</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#" className="hover:text-cyan-400 transition-colors">About</a></li>
                <li><a href="#" className="hover:text-cyan-400 transition-colors">Contact</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-white mb-4">Product</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#" className="hover:text-cyan-400 transition-colors">Features</a></li>
                <li><a href="#" className="hover:text-cyan-400 transition-colors">Pricing</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-white mb-4">Legal</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#" className="hover:text-cyan-400 transition-colors">Privacy</a></li>
                <li><a href="#" className="hover:text-cyan-400 transition-colors">Terms</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-white mb-4">Connect</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#" className="hover:text-cyan-400 transition-colors">GitHub</a></li>
                <li><a href="#" className="hover:text-cyan-400 transition-colors">LinkedIn</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-cyan-500/20 pt-8 text-center text-sm text-gray-400">
            © 2024 Agent-Echo | Made with ❤️ and advanced AI
          </div>
        </div>
      </footer>
    </div>
  );
}
