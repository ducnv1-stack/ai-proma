import React from 'react';
import { Button } from '@/components/ui/Button';

export const HeroSection: React.FC = () => {
  return (
    <section className="pt-32 pb-20 bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      <div className="container mx-auto px-6 max-w-7xl">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Text Content (Left Side) */}
          <div className="text-left">
            <div className="inline-flex items-center bg-indigo-100 text-indigo-600 px-3 py-1.5 rounded-full text-xs font-medium mb-5">
              <i className="fas fa-star mr-1.5 text-xs"></i>
              Advanced AI Technology 2025
            </div>
            <h1 className="text-3xl md:text-4xl lg:text-5xl font-black text-gray-900 leading-tight mb-5">
              Smart Project Management<br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600">
                Powered by AI
              </span>
            </h1>
            <p className="text-sm text-gray-600 mb-6 leading-relaxed max-w-sm text-center">
              Automate workflows, predict risks, and optimize project performance with the power of
              artificial intelligence
            </p>
            <div className="flex flex-col sm:flex-row gap-3 mb-6">
              <Button variant="primary" size="lg">
                <i className="fas fa-rocket mr-1.5 text-sm"></i>
                Start Free Trial
              </Button>
              <Button variant="secondary" size="lg">
                <i className="fas fa-play mr-1.5 text-sm"></i>
                Watch Demo
              </Button>
            </div>
            {/* Stats Row */}
            <div className="flex flex-wrap gap-4 text-xs text-gray-600">
              <div className="flex items-center gap-1.5">
                <i className="fas fa-clock text-indigo-500 text-xs"></i>
                <span className="font-medium">5 minute setup</span>
              </div>
              <div className="flex items-center gap-1.5">
                <i className="fas fa-chart-line text-purple-500 text-xs"></i>
                <span className="font-medium">40% efficiency boost</span>
              </div>
              <div className="flex items-center gap-1.5">
                <i className="fas fa-headset text-teal-500 text-xs"></i>
                <span className="font-medium">24/7 support</span>
              </div>
            </div>
          </div>

          {/* Dashboard Showcase (Right Side) */}
          <div className="relative">
            {/* Main Dashboard Image */}
            <div className="relative bg-white rounded-3xl shadow-2xl overflow-hidden border border-gray-100 dashboard-container">
              <div className="dashboard-image">
                <img src="/banner-index-proma.avif" alt="Proma AI Dashboard" className="w-full h-auto rounded-lg" />
              </div>
            </div>

            {/* Floating Stats Cards */}
            <div className="absolute -top-3 -left-3 bg-white rounded-xl shadow-lg p-3 border border-gray-100 floating-card" style={{ "--rotation": "-2deg" } as React.CSSProperties}>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-xs font-medium text-gray-600">Projects Completed</span>
              </div>
              <div className="text-xl font-black text-gray-900 mt-1">94%</div>
            </div>

            <div className="absolute top-6 -right-3 bg-white rounded-xl shadow-lg p-3 border border-gray-100 floating-card" style={{ "--rotation": "2deg" } as React.CSSProperties}>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                <span className="text-xs font-medium text-gray-600">AI Insights</span>
              </div>
              <div className="text-lg font-black text-blue-600 mt-1">Real-time</div>
            </div>

            <div className="absolute bottom-6 -right-3 bg-white rounded-xl shadow-lg p-3 border border-gray-100 floating-card" style={{ "--rotation": "1deg" } as React.CSSProperties}>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-teal-500 rounded-full"></div>
                <span className="text-xs font-medium text-gray-600">Time Saved</span>
              </div>
              <div className="text-xl font-black text-teal-600 mt-1">8.5h</div>
              <div className="text-xs text-gray-500">per week</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
