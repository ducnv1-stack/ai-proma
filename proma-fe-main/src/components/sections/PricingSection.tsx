import React from 'react';
import { PricingPlan } from '@/types';

export const PricingSection: React.FC = () => {
  const plans: PricingPlan[] = [
    {
      name: 'Starter',
      description: 'Basic, for individuals & small teams.',
      price: 'Free',
      features: ['3 Projects', '10 Team Members', 'Basic Analytics'],
      buttonText: 'Get Started',
      buttonClass: 'bg-white border-2 border-gray-300 text-gray-800 hover:bg-gray-100',
      cardClass: 'bg-gray-50 p-6 rounded-xl border-2 border-gray-200 h-full'
    },
    {
      name: 'Pro',
      description: 'For growing teams, advanced features.',
      price: '$49',
      priceUnit: '/month',
      features: ['Unlimited Projects', 'Unlimited Members', 'AI Analytics & Automation', 'Priority Support'],
      buttonText: 'Choose Pro',
      buttonClass: 'bg-white text-purple-600',
      cardClass: 'main-gradient text-white p-6 rounded-2xl shadow-2xl relative h-full transform lg:scale-105',
      popular: true
    },
    {
      name: 'Enterprise',
      description: 'For large companies, custom AI and security.',
      price: 'Custom',
      features: ['Everything in Pro', 'Custom AI Models', 'Dedicated Account Manager'],
      buttonText: 'Contact Sales',
      buttonClass: 'bg-white border-2 border-gray-300 text-gray-800 hover:bg-gray-100',
      cardClass: 'bg-gray-50 p-6 rounded-xl border-2 border-gray-200 h-full'
    }
  ];

  return (
    <section id="pricing" className="py-20 bg-white fade-in-section">
      <div className="container mx-auto px-6 max-w-7xl">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-800">Flexible Pricing for Every Team</h2>
          <p className="mt-4 text-lg text-gray-600">Start free, upgrade as you grow.</p>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-center max-w-5xl mx-auto">
          {plans.map((plan, index) => (
            <div key={index} className={plan.cardClass}>
              {plan.popular && (
                <span className="absolute top-0 -translate-y-1/2 left-1/2 -translate-x-1/2 bg-teal-500 text-white text-xs font-bold px-3 py-1 rounded-full uppercase">
                  Most Popular
                </span>
              )}
              <h3 className="text-xl font-bold">{plan.name}</h3>
              <p className={`mt-2 text-sm ${plan.popular ? 'text-gray-200' : 'text-gray-500'}`}>
                {plan.description}
              </p>
              <p className="text-4xl font-extrabold my-5">
                {plan.price}
                {plan.priceUnit && <span className="text-lg font-medium">{plan.priceUnit}</span>}
              </p>
              <ul className={`space-y-2 mb-6 text-sm ${plan.popular ? 'text-gray-100' : 'text-gray-600'}`}>
                {plan.features.map((feature, featureIndex) => (
                  <li key={featureIndex} className="flex items-center">
                    <svg className={`w-5 h-5 mr-2 ${plan.popular ? 'text-white' : 'text-green-500'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                    </svg>
                    {feature}
                  </li>
                ))}
              </ul>
              <button className={`w-full text-center font-semibold py-2.5 px-5 rounded-full text-sm transition-all duration-300 ${plan.buttonClass}`}>
                {plan.buttonText}
              </button>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
