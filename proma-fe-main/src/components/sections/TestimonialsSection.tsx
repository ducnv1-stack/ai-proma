import React from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { TestimonialItem } from '@/types';

export const TestimonialsSection: React.FC = () => {
  const testimonials: TestimonialItem[] = [
    {
      name: 'Sarah Johnson',
      position: 'Project Manager at TechFlow Solutions',
      content: 'Proma Project Manager has completely transformed how we manage projects. The real-time dashboard and workflow efficiency is truly remarkable. Highly recommend for any team.',
      avatar: 'SJ',
      avatarColor: 'bg-indigo-500'
    },
    {
      name: 'Michael Chen',
      position: 'CTO at Digital Innovations Hub',
      content: 'Since using AI Project Manager, our team productivity has increased by 40% on all projects. The visual dashboard and insights are truly game-changing.',
      avatar: 'MC',
      avatarColor: 'bg-purple-500'
    },
    {
      name: 'Emily Rodriguez',
      position: 'Operations Lead at StartupFlow',
      content: 'The team collaboration and AI planning features are amazing. Our remote team now works as efficiently as when sitting together in the same office.',
      avatar: 'ER',
      avatarColor: 'bg-teal-500'
    },
    {
      name: 'David Thompson',
      position: 'Principal Lead at CloudTech Pro',
      content: 'User-friendly interface, easy integration with existing tools. AI suggestions help me identify bottlenecks early and optimize workflow effectively.',
      avatar: 'DT',
      avatarColor: 'bg-orange-500'
    },
    {
      name: 'Lisa Wang',
      position: 'Senior Manager at E-Commerce Plus',
      content: 'Automated reporting and real-time monitoring give me a comprehensive view of all projects. 24/7 customer support is very professional and responsive.',
      avatar: 'LW',
      avatarColor: 'bg-green-500'
    },
    {
      name: 'James Wilson',
      position: 'Agile Coach at DevFlow Solutions',
      content: 'Perfect for Agile methodology. Sprint planning with AI suggestions and auto-scheduling team charts help the team focus on development instead of admin tasks.',
      avatar: 'JW',
      avatarColor: 'bg-blue-500'
    }
  ];

  return (
    <section className="py-20 bg-white">
      <div className="container mx-auto px-6 max-w-7xl">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-800">
            What Our <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600">Customers Say</span>
          </h2>
          <p className="text-lg text-gray-600 mt-4">Thousands of businesses have trusted and achieved excellent results with AI Project Manager</p>
        </div>

        {/* Testimonials Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
          {testimonials.map((testimonial, index) => (
            <div key={index} className="bg-white p-6 rounded-2xl shadow-lg border border-gray-100">
              <div className="flex items-center mb-4">
                <div className="flex text-yellow-400">
                  {[...Array(5)].map((_, i) => (
                    <i key={i} className="fas fa-star"></i>
                  ))}
                </div>
              </div>
              <p className="text-gray-700 mb-4 italic">"{testimonial.content}"</p>
              <div className="flex items-center">
                <div className={`w-10 h-10 ${testimonial.avatarColor} rounded-full mr-3 flex items-center justify-center text-white font-semibold text-sm`}>
                  {testimonial.avatar}
                </div>
                <div>
                  <div className="font-semibold text-gray-900">{testimonial.name}</div>
                  <div className="text-sm text-gray-500">{testimonial.position}</div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Average Rating & CTA */}
        <div className="text-center max-w-md mx-auto">
          <div className="flex items-center justify-center gap-2 bg-purple-50 border border-purple-200 rounded-full px-6 py-3 mb-6 w-full">
            <i className="fas fa-star text-yellow-400 text-sm"></i>
            <span className="text-sm font-medium text-purple-700">Average rating 4.9/5 from 2,500+ customers</span>
          </div>
          <Link href="/login">
            <Button variant="primary" size="lg" className="w-full shadow-lg hover:shadow-xl">
              Join our satisfied customer community
            </Button>
          </Link>
        </div>
      </div>
    </section>
  );
};
