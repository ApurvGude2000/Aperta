import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/design-system/Button';
import { Card, FeatureCard } from '../components/design-system/Card';

export function Landing() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    // Check if user is logged in (check for token in localStorage)
    const token = localStorage.getItem('auth_token') || localStorage.getItem('token');
    setIsLoggedIn(!!token);
  }, []);
  const features = [
    {
      icon: '⚡',
      title: 'Real-time Transcription',
      description: 'Capture conversations automatically with AI-powered speech-to-text',
    },
    {
      icon: '🕸️',
      title: 'Knowledge Graph',
      description: 'Visualize connections between people, topics, and organizations',
    },
    {
      icon: '🧠',
      title: 'AI Agents',
      description: 'Privacy Guardian, Context Understanding, Follow-Up suggestions, and more',
    },
    {
      icon: '📈',
      title: 'Analytics',
      description: 'Track networking effectiveness and conversation insights',
    },
    {
      icon: '🔒',
      title: 'Privacy First',
      description: 'Automatic PII redaction and enterprise-grade data protection',
    },
    {
      icon: '💬',
      title: 'Smart Follow-ups',
      description: 'Auto-generate personalized follow-up messages and reminders',
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-[#F5F7FA]">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 bg-white/80 backdrop-blur border-b border-[#E5E7EB]">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3 font-display font-bold text-2xl">
              <img
                src="/TH_logo.png"
                alt="Aperta Logo"
                className="w-10 h-10 rounded-full object-cover"
              />
              <span className="text-[#121417]">Aperta</span>
            </div>

            <div className="hidden md:flex items-center gap-8">
              <a href="#features" className="text-sm font-medium text-[#6B7280] hover:text-[#1F3C88] transition-colors">
                Features
              </a>
              <a href="#how-it-works" className="text-sm font-medium text-[#6B7280] hover:text-[#1F3C88] transition-colors">
                How It Works
              </a>
              <a href="#privacy" className="text-sm font-medium text-[#6B7280] hover:text-[#1F3C88] transition-colors">
                Privacy
              </a>
            </div>

            <div className="flex items-center gap-4">
              <Link to="/login" className="text-sm font-medium text-[#1F3C88] hover:text-[#00C2FF]">
                Login
              </Link>
              <Link
                to="/dashboard"
                className="px-4 py-2 bg-gradient-to-r from-[#1F3C88] to-[#00C2FF] text-white text-sm font-medium rounded-lg hover:shadow-lg transition-all"
              >
                Dashboard
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-6 py-24 lg:py-32 flex items-center">
        <div className="flex-1">
          <h1 className="font-display text-5xl lg:text-6xl font-bold text-[#121417] mb-6">
            Turn <span className="bg-gradient-to-r from-[#1F3C88] to-[#00C2FF] bg-clip-text text-transparent">Conversations</span> into <span className="bg-gradient-to-r from-[#1F3C88] to-[#00C2FF] bg-clip-text text-transparent">Connections</span>
          </h1>
          <p className="text-lg text-[#6B7280] mb-8 max-w-2xl">
            AI-powered networking assistant that captures conversations, builds knowledge graphs, and automates follow-ups—all while keeping your data private.
          </p>
          <div className="flex gap-4">
            <Link to={isLoggedIn ? "/dashboard" : "/login"}>
              <Button size="lg">{isLoggedIn ? "Get Started" : "Login"} →</Button>
            </Link>
            <a href="#how-it-works">
              <Button variant="secondary" size="lg">
                Learn More
              </Button>
            </a>
          </div>
        </div>
        <div className="hidden lg:flex flex-1 justify-end">
          <div className="w-full max-w-2xl h-[500px] rounded-2xl overflow-hidden">
            <img
              src="/necklace.jpeg"
              alt="Network Visualization"
              className="w-full h-full object-cover"
            />
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="bg-white py-24">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="font-display text-4xl font-bold text-[#121417] mb-4">Powerful Features</h2>
            <p className="text-lg text-[#6B7280]">Everything you need for intelligent networking</p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, idx) => (
              <FeatureCard key={idx} {...feature} />
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-24">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="font-display text-4xl font-bold text-[#121417] mb-4">How It Works</h2>
          </div>
          <div className="grid md:grid-cols-4 gap-8">
            {[
              { step: 1, title: 'Record', desc: 'Start recording your conversations' },
              { step: 2, title: 'Process', desc: 'AI processes and transcribes instantly' },
              { step: 3, title: 'Connect', desc: 'Identify people and topics automatically' },
              { step: 4, title: 'Follow Up', desc: 'Generate smart follow-up actions' },
            ].map((item) => (
              <Card key={item.step} className="text-center">
                <div className="w-12 h-12 rounded-full bg-gradient-to-r from-[#1F3C88] to-[#00C2FF] text-white flex items-center justify-center font-display font-bold text-lg mx-auto mb-4">
                  {item.step}
                </div>
                <h3 className="font-bold text-[#121417] mb-2">{item.title}</h3>
                <p className="text-sm text-[#6B7280]">{item.desc}</p>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Privacy Assurance */}
      <section id="privacy" className="bg-gradient-to-r from-[#1F3C88] to-[#00C2FF] py-24 text-white">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="font-display text-4xl font-bold mb-4">Your Privacy, Our Priority</h2>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { title: 'On-Device Processing', desc: 'Audio processed locally on your device' },
              { title: 'Zero Audio Storage', desc: 'We never store your recordings' },
              { title: 'Enterprise Security', desc: 'Bank-level encryption and compliance' },
            ].map((item, idx) => (
              <div key={idx} className="text-center">
                <h3 className="font-bold text-lg mb-2">{item.title}</h3>
                <p className="text-white/80">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-[#121417] text-[#6B7280] py-12">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid md:grid-cols-4 gap-12 mb-12">
            <div>
              <h4 className="font-bold text-white mb-4">Company</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-white">About</a></li>
                <li><a href="#" className="hover:text-white">Contact</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-white mb-4">Product</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-white">Features</a></li>
                <li><a href="#" className="hover:text-white">Pricing</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-white mb-4">Legal</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-white">Privacy</a></li>
                <li><a href="#" className="hover:text-white">Terms</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-white mb-4">Connect</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-white">GitHub</a></li>
                <li><a href="#" className="hover:text-white">LinkedIn</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-[#6B7280] pt-8 text-center text-sm">
            © 2024 Aperta | Made with privacy in mind
          </div>
        </div>
      </footer>
    </div>
  );
}
