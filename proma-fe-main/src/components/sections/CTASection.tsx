import React from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';

interface CTASectionProps {
  variant?: 'simple' | 'final' | 'testimonial';
}

export const CTASection: React.FC<CTASectionProps> = ({ variant = 'simple' }) => {
  if (variant === 'simple') {
    return (
      <section className="py-20 bg-gradient-to-br from-indigo-50 to-purple-50 fade-in-section">
        <div className="container mx-auto px-6 text-center max-w-4xl">
          <h2 className="text-4xl font-bold text-gray-800 mb-4">Ready to experience AI power?</h2>
          <p className="text-lg text-gray-600 mb-8">Join thousands of businesses that trust AI Project Manager for their success</p>
          <Link href="/login">
            <Button variant="primary" size="lg" className="shadow-lg hover:shadow-xl">
              Start 14-day free trial
            </Button>
          </Link>
        </div>
      </section>
    );
  }

  if (variant === 'testimonial') {
    return (
      <section id="reviews" className="py-20 bg-gray-50 fade-in-section">
        <div className="container mx-auto px-6 max-w-4xl text-center">
          <h2 className="text-4xl font-bold text-gray-800 mb-12">Trusted by Teams Worldwide</h2>
          <div className="bg-white p-10 rounded-2xl shadow-lg relative">
            <img
              src="https://placehold.co/100x100/764ba2/ffffff?text=User"
              alt="Customer Avatar"
              className="w-24 h-24 rounded-full mx-auto -mt-24 mb-6 border-4 border-white shadow-md"
            />
            <p className="text-xl md:text-2xl font-medium text-gray-700 italic">
              "Proma has completely transformed the way we work. It helps us save 30% of management time and
              reduce risks remarkably."
            </p>
            <cite className="block mt-6 not-italic">
              <span className="font-bold text-gray-900">Jane Doe</span><br />
              <span className="text-gray-500">Project Manager, TechCorp</span>
            </cite>
          </div>
        </div>
      </section>
    );
  }

  if (variant === 'final') {
    const features = [
      '14-day free trial',
      'No credit card required',
      '24/7 support',
      'Integration with 100+ tools',
      'Free team training',
      'Enterprise-grade security'
    ];

    return (
      <>
        {/* Final CTA Section */}
        <section className="py-20 bg-gradient-to-r from-indigo-600 to-purple-600 text-white">
          <div className="container mx-auto px-6 text-center max-w-4xl">
            <div className="mb-8">
              <div className="inline-flex items-center bg-white/20 text-white px-4 py-2 rounded-full text-sm font-medium mb-6">
                <i className="fas fa-rocket mr-2"></i>
                Special Offer - This Month Only
              </div>
              <h2 className="text-4xl md:text-5xl font-bold mb-4">
                Ready to revolutionize<br />
                <span className="text-yellow-300">your project management?</span>
              </h2>
              <p className="text-lg text-gray-200 mb-8">
                Join thousands of smart businesses that have chosen AI Project Manager to boost efficiency and
                achieve outstanding success
              </p>
            </div>

            {/* Features List */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8 text-left max-w-2xl mx-auto">
              {features.map((feature, index) => (
                <div key={index} className="flex items-center gap-3">
                  <i className="fas fa-check-circle text-green-400"></i>
                  <span>{feature}</span>
                </div>
              ))}
            </div>

            <div className="flex flex-col sm:flex-row justify-center items-center gap-4 mb-8">
              <Link href="/login">
                <Button variant="secondary" size="lg" className="w-full sm:w-auto bg-white text-purple-600 hover:bg-gray-100 shadow-lg hover:shadow-xl">
                  Start Free Trial Now
                </Button>
              </Link>
              <Button variant="outline" size="lg" className="w-full sm:w-auto bg-transparent border-2 border-white text-white hover:bg-white hover:text-purple-600">
                Schedule Personal Demo
              </Button>
            </div>

            <div className="text-center">
              <p className="text-sm text-gray-300 mb-4">Trusted by 50,000+ users worldwide</p>
              <div className="flex justify-center items-center gap-2">
                <div className="flex text-yellow-400">
                  <i className="fas fa-star"></i>
                  <i className="fas fa-star"></i>
                  <i className="fas fa-star"></i>
                  <i className="fas fa-star"></i>
                  <i className="fas fa-star"></i>
                </div>
                <span className="text-sm text-gray-300">4.95/5 from 2,500+ reviews</span>
              </div>
            </div>

            <div className="mt-12 bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
              <div className="flex items-center justify-center gap-2 mb-4">
                <i className="fas fa-gift text-yellow-400 text-xl"></i>
                <span className="text-xl font-bold text-yellow-300">Special Offer This Month</span>
              </div>
              <p className="text-white mb-4">Sign up today to get our Premium Plan free for 3 days with our experts</p>
              <div className="flex items-center justify-center gap-2">
                <i className="fas fa-clock text-yellow-400"></i>
                <span className="font-bold text-yellow-300">Only 15 days left - Don't miss out!</span>
              </div>
            </div>
          </div>
        </section>

        {/* Final Simple CTA Section */}
        <section id="cta" className="main-gradient text-white py-20 fade-in-section">
          <div className="container mx-auto px-6 text-center max-w-3xl">
            <h2 className="text-4xl font-bold mb-4">Ready to Supercharge Your Projects with AI?</h2>
            <Link href="/login">
              <Button variant="secondary" size="lg" className="bg-white text-purple-600 font-bold mt-8">
                Start Free Trial
              </Button>
            </Link>
            <p className="mt-4 text-gray-200">No credit card required – start now.</p>
          </div>
        </section>
      </>
    );
  }

  return null;
};
