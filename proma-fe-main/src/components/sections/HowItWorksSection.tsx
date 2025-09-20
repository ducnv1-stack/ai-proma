import React from 'react';
import { StepItem } from '@/types';

export const HowItWorksSection: React.FC = () => {
  const steps: StepItem[] = [
    {
      number: '01',
      title: 'Connect Your Project',
      description: 'Easily import data or integrate with the tools you\'re already using.',
      color: 'text-indigo-600'
    },
    {
      number: '02',
      title: 'AI Analyzes & Optimizes',
      description: 'Our AI will analyze and provide suggestions to optimize your project.',
      color: 'text-purple-600'
    },
    {
      number: '03',
      title: 'Track & Report',
      description: 'Monitor progress visually and receive intelligent automated reports.',
      color: 'text-teal-500'
    }
  ];

  return (
    <section id="how-it-works" className="py-20 bg-white fade-in-section">
      <div className="container mx-auto px-6 max-w-5xl">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-800">How It Works in 3 Steps</h2>
        </div>
        <div className="flex flex-col md:flex-row justify-between items-center gap-12">
          {steps.map((step, index) => (
            <div key={index} className="text-center max-w-xs">
              <div className={`text-6xl font-extrabold ${step.color} mb-4`}>{step.number}</div>
              <h3 className="text-2xl font-bold mb-2">{step.title}</h3>
              <p className="text-gray-600">{step.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
