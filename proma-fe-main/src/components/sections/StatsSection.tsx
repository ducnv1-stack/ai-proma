import React from 'react';
import { StatItem } from '@/types';

export const StatsSection: React.FC = () => {
  const stats: StatItem[] = [
    { icon: 'fas fa-users', value: '50,000+', label: 'Trusted Users', subtitle: 'Worldwide' },
    { icon: 'fas fa-chart-line', value: '40%', label: 'Efficiency Boost', subtitle: 'Average per project' },
    { icon: 'fas fa-clock', value: '8.5h', label: 'Time Saved', subtitle: 'Per week per PM' },
    { icon: 'fas fa-shield-check', value: '99.9%', label: 'Reliability', subtitle: 'Uptime guaranteed' }
  ];

  const companies = ['Microsoft', 'Google', 'Amazon', 'Meta', 'Apple'];

  return (
    <section className="py-20 bg-gradient-to-r from-indigo-600 to-purple-600 text-white">
      <div className="container mx-auto px-6 max-w-6xl">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold mb-4">Impressive Numbers</h2>
          <p className="text-lg text-gray-200">Real results from customers who have used AI Project Manager</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
          {stats.map((stat, index) => (
            <div key={index} className="text-center bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20">
              <div className="text-white/80 mb-4">
                <i className={`${stat.icon} text-3xl`}></i>
              </div>
              <div className="text-4xl font-black text-white mb-2">{stat.value}</div>
              <div className="text-white/80 font-medium">{stat.label}</div>
              <div className="text-white/60 text-sm">{stat.subtitle}</div>
            </div>
          ))}
        </div>

        {/* Trusted by leading enterprises */}
        <div className="text-center">
          <div className="bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20 inline-block">
            <h3 className="text-xl font-bold text-white mb-6">Trusted by leading enterprises</h3>
            <div className="flex flex-wrap justify-center items-center gap-8 text-white/60">
              {companies.map((company, index) => (
                <span key={index} className="text-lg font-medium">{company}</span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
