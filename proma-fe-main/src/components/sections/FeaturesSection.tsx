import React from 'react';
import { FeatureItem } from '@/types';

export const FeaturesSection: React.FC = () => {
  const features: FeatureItem[] = [
    {
      icon: 'fas fa-brain',
      title: 'Smart AI',
      description: 'Artificial intelligence learns from project data to provide optimal suggestions and accurate risk predictions.',
      bgColor: 'bg-purple-100',
      textColor: 'text-purple-600'
    },
    {
      icon: 'fas fa-chart-bar',
      title: 'Data Analytics',
      description: 'Visual dashboard with real-time charts, detailed reports and actionable insights for better decisions.',
      bgColor: 'bg-blue-100',
      textColor: 'text-blue-600',
      titleGradient: true
    },
    {
      icon: 'fas fa-cogs',
      title: 'Automation',
      description: 'Automatically assign tasks, send notifications and update progress based on intelligent rules.',
      bgColor: 'bg-orange-100',
      textColor: 'text-orange-600'
    },
    {
      icon: 'fas fa-users',
      title: 'Team Collaboration',
      description: 'Shared workspace with integrated chat, file sharing and flexible access management.',
      bgColor: 'bg-green-100',
      textColor: 'text-green-600',
      titleGradient: true
    }
  ];

  return (
    <section id="features" className="py-20 bg-gray-50 fade-in-section">
      <div className="container mx-auto px-6 max-w-7xl">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-800">
            Powerful <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600">Features</span>
          </h2>
          <p className="mt-4 text-lg text-gray-600 max-w-2xl mx-auto">
            Discover powerful features that help you manage projects more effectively than ever before
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((feature, index) => (
            <div key={index} className="bg-white p-8 rounded-2xl shadow-md transition-all duration-300 feature-card">
              <div className={`${feature.bgColor} ${feature.textColor} rounded-xl w-14 h-14 flex items-center justify-center mb-6`}>
                <i className={`${feature.icon} text-2xl`}></i>
              </div>
              <h3 className={`text-xl font-bold mb-3 ${feature.titleGradient ? 'text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600' : 'text-gray-900'}`}>
                {feature.title}
              </h3>
              <p className="text-gray-600">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
