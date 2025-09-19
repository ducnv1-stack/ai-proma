'use client';

import React, { useState, useEffect } from 'react';

// Button Component
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
  onClick?: () => void;
  className?: string;
}

const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  children,
  onClick,
  className = ''
}) => {
  const baseClasses = 'inline-flex items-center justify-center font-semibold rounded-lg transition-all duration-300 focus:outline-none';

  const variants = {
    primary: 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:from-indigo-700 hover:to-purple-700 shadow-lg hover:shadow-xl transform hover:-translate-y-1',
    secondary: 'bg-white border-2 border-indigo-200 text-indigo-600 hover:bg-indigo-50 hover:border-indigo-300',
    outline: 'border-2 border-current text-current hover:bg-current hover:text-white'
  };

  const sizes = {
    sm: 'px-4 py-2 text-sm',
    md: 'px-6 py-3 text-sm',
    lg: 'px-8 py-4 text-base'
  };

  return (
    <button
      className={`${baseClasses} ${variants[variant]} ${sizes[size]} ${className}`}
      onClick={onClick}
    >
      {children}
    </button>
  );
};

// Header Component
const Header: React.FC = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <header className="bg-white/80 backdrop-blur-lg fixed top-0 left-0 right-0 z-50 shadow-sm">
      <div className="container mx-auto px-6 py-4 flex justify-between items-center max-w-7xl">
        {/* Logo */}
        <a href="#" className="flex items-center space-x-3">
          <div className="relative">
            <div className="w-10 h-10 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg transform rotate-3">
              <svg className="h-6 w-6 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div className="absolute -top-1 -right-1 w-4 h-4 bg-gradient-to-r from-green-400 to-emerald-500 rounded-full flex items-center justify-center shadow-sm">
              <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
            </div>
          </div>
          <div className="flex items-baseline">
            <span className="text-2xl font-black text-gray-900">Proma</span>
            <span className="text-lg font-bold text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600 ml-1">AI</span>
          </div>
        </a>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center space-x-8">
          <a href="#features" className="text-gray-600 hover:text-indigo-600 transition">Features</a>
          <a href="#pricing" className="text-gray-600 hover:text-indigo-600 transition">Pricing</a>
          <a href="#reviews" className="text-gray-600 hover:text-indigo-600 transition">Reviews</a>
          <a href="#contact" className="text-gray-600 hover:text-indigo-600 transition">Contact</a>
        </nav>

        {/* Desktop CTA Buttons */}
        <div className="hidden md:flex items-center space-x-4">
          <button className="text-gray-600 hover:text-indigo-600 font-medium transition">Sign In</button>
          <Button variant="primary" size="md">Try Free</Button>
        </div>

        {/* Mobile Menu Button */}
        <button
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          className="md:hidden"
        >
          <svg className="w-6 h-6 text-gray-800" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16m-7 6h7" />
          </svg>
        </button>
      </div>

      {/* Mobile Menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden px-6 pb-4">
          <a href="#features" className="block py-2 text-gray-600 hover:text-indigo-600">Features</a>
          <a href="#pricing" className="block py-2 text-gray-600 hover:text-indigo-600">Pricing</a>
          <a href="#reviews" className="block py-2 text-gray-600 hover:text-indigo-600">Reviews</a>
          <a href="#contact" className="block py-2 text-gray-600 hover:text-indigo-600">Contact</a>
          <button className="block py-2 text-gray-600 hover:text-indigo-600 font-medium">Sign In</button>
          <Button variant="primary" size="md" className="mt-4 w-full">Try Free</Button>
        </div>
      )}
    </header>
  );
};

// Hero Section Component
const HeroSection: React.FC = () => {
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
            <div className="absolute -top-3 -left-3 bg-white rounded-xl shadow-lg p-3 border border-gray-100 floating-card" style={{ "--rotation": "-2deg" }}>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-xs font-medium text-gray-600">Projects Completed</span>
              </div>
              <div className="text-xl font-black text-gray-900 mt-1">94%</div>
            </div>

            <div className="absolute top-6 -right-3 bg-white rounded-xl shadow-lg p-3 border border-gray-100 floating-card" style={{ "--rotation": "2deg" }}>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                <span className="text-xs font-medium text-gray-600">AI Insights</span>
              </div>
              <div className="text-lg font-black text-blue-600 mt-1">Real-time</div>
            </div>

            <div className="absolute bottom-6 -right-3 bg-white rounded-xl shadow-lg p-3 border border-gray-100 floating-card" style={{ "--rotation": "1deg" }}>
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

// Features Section Component
const FeaturesSection: React.FC = () => {
  const features = [
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

// Simple CTA Section
const SimpleCTASection: React.FC = () => {
  return (
    <section className="py-20 bg-gradient-to-br from-indigo-50 to-purple-50 fade-in-section">
      <div className="container mx-auto px-6 text-center max-w-4xl">
        <h2 className="text-4xl font-bold text-gray-800 mb-4">Ready to experience AI power?</h2>
        <p className="text-lg text-gray-600 mb-8">Join thousands of businesses that trust AI Project Manager for their success</p>
        <Button variant="primary" size="lg" className="shadow-lg hover:shadow-xl">
          Start 14-day free trial
        </Button>
      </div>
    </section>
  );
};

// Stats Section Component
const StatsSection: React.FC = () => {
  const stats = [
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

// Testimonials Section Component
const TestimonialsSection: React.FC = () => {
  const testimonials = [
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
          <Button variant="primary" size="lg" className="w-full shadow-lg hover:shadow-xl">
            Join our satisfied customer community
          </Button>
        </div>
      </div>
    </section>
  );
};

// Final CTA Section Component
const FinalCTASection: React.FC = () => {
  const features = [
    '14-day free trial',
    'No credit card required',
    '24/7 support',
    'Integration with 100+ tools',
    'Free team training',
    'Enterprise-grade security'
  ];

  return (
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
          <Button variant="secondary" size="lg" className="w-full sm:w-auto bg-white text-purple-600 hover:bg-gray-100 shadow-lg hover:shadow-xl">
            Start Free Trial Now
          </Button>
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
  );
};

// How It Works Section Component
const HowItWorksSection: React.FC = () => {
  const steps = [
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

// Single Testimonial Section Component
const SingleTestimonialSection: React.FC = () => {
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
};

// Pricing Plans Section Component
const PricingSection: React.FC = () => {
  const plans = [
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

// Final Simple CTA Section
const FinalSimpleCTASection: React.FC = () => {
  return (
    <section id="cta" className="main-gradient text-white py-20 fade-in-section">
      <div className="container mx-auto px-6 text-center max-w-3xl">
        <h2 className="text-4xl font-bold mb-4">Ready to Supercharge Your Projects with AI?</h2>
        <Button variant="secondary" size="lg" className="bg-white text-purple-600 font-bold mt-8">
          Start Free Trial
        </Button>
        <p className="mt-4 text-gray-200">No credit card required – start now.</p>
      </div>
    </section>
  );
};

// Footer Component
const Footer: React.FC = () => {
  return (
    <footer id="contact" className="bg-slate-800 text-white">
      <div className="container mx-auto px-6 py-12 max-w-7xl">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {/* AI Project Manager */}
          <div>
            <div className="flex items-center space-x-2 mb-4">
              <div className="bg-indigo-600 rounded-lg p-2">
                <svg className="h-6 w-6 text-white" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z" />
                  <path d="m9 12 2 2 4-4" />
                </svg>
              </div>
              <span className="text-lg font-bold">AI Project Manager</span>
            </div>
            <p className="text-gray-300 text-sm leading-relaxed mb-6">
              Intelligent project management solution powered by artificial intelligence, helping businesses
              optimize performance and achieve success.
            </p>
            <div className="flex space-x-4">
              <a href="#" className="text-gray-400 hover:text-white transition">
                <i className="fab fa-facebook text-lg"></i>
              </a>
              <a href="#" className="text-gray-400 hover:text-white transition">
                <i className="fab fa-twitter text-lg"></i>
              </a>
              <a href="#" className="text-gray-400 hover:text-white transition">
                <i className="fab fa-linkedin text-lg"></i>
              </a>
              <a href="#" className="text-gray-400 hover:text-white transition">
                <i className="fab fa-youtube text-lg"></i>
              </a>
            </div>
          </div>

          {/* Product */}
          <div>
            <h4 className="text-lg font-semibold mb-4">Product</h4>
            <ul className="space-y-3">
              <li><a href="#features" className="text-gray-300 hover:text-white transition text-sm">Features</a></li>
              <li><a href="#pricing" className="text-gray-300 hover:text-white transition text-sm">Pricing</a></li>
              <li><a href="#" className="text-gray-300 hover:text-white transition text-sm">Integrations</a></li>
              <li><a href="#" className="text-gray-300 hover:text-white transition text-sm">API</a></li>
              <li><a href="#" className="text-gray-300 hover:text-white transition text-sm">Security</a></li>
            </ul>
          </div>

          {/* Support */}
          <div>
            <h4 className="text-lg font-semibold mb-4">Support</h4>
            <ul className="space-y-3">
              <li><a href="#" className="text-gray-300 hover:text-white transition text-sm">Help Center</a></li>
              <li><a href="#" className="text-gray-300 hover:text-white transition text-sm">User Guide</a></li>
              <li><a href="#" className="text-gray-300 hover:text-white transition text-sm">Video Tutorials</a></li>
              <li><a href="#" className="text-gray-300 hover:text-white transition text-sm">Community</a></li>
              <li><a href="#" className="text-gray-300 hover:text-white transition text-sm">Contact Support</a></li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h4 className="text-lg font-semibold mb-4">Contact</h4>
            <div className="space-y-4">
              <div className="flex items-start space-x-3">
                <i className="fas fa-envelope text-gray-400 mt-1"></i>
                <div>
                  <p className="text-gray-300 text-sm">support@aiprojectmanager.com</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <i className="fas fa-phone text-gray-400 mt-1"></i>
                <div>
                  <p className="text-gray-300 text-sm">+1 (555) 123-4567 (24/7)</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <i className="fas fa-map-marker-alt text-gray-400 mt-1"></i>
                <div>
                  <p className="text-gray-300 text-sm">123 Innovation Drive<br />Suite 100<br />San Francisco, CA 94107</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-gray-600 mt-12 pt-6 flex flex-col md:flex-row justify-between items-center">
          <div className="text-gray-400 text-sm mb-4 md:mb-0">
            <p>&copy; 2024 AI Project Manager. All rights reserved.</p>
          </div>
          <div className="flex space-x-6 text-sm">
            <a href="#" className="text-gray-400 hover:text-white transition">Privacy Policy</a>
            <a href="#" className="text-gray-400 hover:text-white transition">Terms of Service</a>
            <a href="#" className="text-gray-400 hover:text-white transition">Cookie Policy</a>
          </div>
        </div>
      </div>
    </footer>
  );
};

// Main App Component
export default function LandingPage() {
  useEffect(() => {
    // Intersection Observer for fade-in animations
    const sections = document.querySelectorAll('.fade-in-section');
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.1
    });

    sections.forEach(section => {
      observer.observe(section);
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href') || '');
        if (target) {
          target.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          });
        }
      });
    });

    return () => {
      observer.disconnect();
    };
  }, []);

  return (
    <div className="min-h-screen bg-white">
      {/* Include Tailwind CSS from CDN */}
      <script src="https://cdn.tailwindcss.com"></script>
      {/* Include Font Awesome */}
      <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet" />
      {/* Include Google Fonts */}
      <link rel="preconnect" href="https://fonts.googleapis.com" />
      <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      <link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;500;600;700&family=Roboto:wght@400;500;700;900&display=swap" rel="stylesheet" />

      {/* Custom Styles */}
      <style dangerouslySetInnerHTML={{
        __html: `
          body {
            font-family: 'Open Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            background-color: #ffffff;
          }

          h1, h2, h3, h4, h5, h6 {
            font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
          }

          .main-gradient {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          }

          .secondary-gradient {
            background: linear-gradient(135deg, #f5f7fa 0%, #e8ebf1 100%);
          }

          .cta-button {
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
          }

          .cta-button:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
            filter: brightness(1.1);
          }

          .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
          }

          .floating-card {
            animation: float 6s ease-in-out infinite;
          }

          .floating-card:nth-child(2) {
            animation-delay: -2s;
          }

          .floating-card:nth-child(3) {
            animation-delay: -4s;
          }

          @keyframes float {
            0%, 100% {
              transform: translateY(0px) rotate(var(--rotation, 0deg));
            }
            50% {
              transform: translateY(-10px) rotate(var(--rotation, 0deg));
            }
          }

          .gradient-text {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
          }

          .dashboard-container {
            perspective: 1000px;
          }

          .dashboard-image {
            transform-style: preserve-3d;
            transition: transform 0.3s ease;
          }

          .dashboard-image:hover {
            transform: rotateY(5deg) rotateX(5deg);
          }

          .fade-in-section {
            opacity: 0;
            transform: translateY(30px);
            transition: opacity 0.8s ease-out, transform 0.8s ease-out;
          }

          .fade-in-section.is-visible {
            opacity: 1;
            transform: translateY(0);
          }

          .stats-badge {
            backdrop-filter: blur(10px);
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid rgba(255, 255, 255, 0.2);
          }

          .hero-bg {
            background-image:
              radial-gradient(circle at 20% 50%, rgba(120, 119, 198, 0.1) 0%, transparent 50%),
              radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.1) 0%, transparent 50%),
              radial-gradient(circle at 40% 80%, rgba(120, 200, 255, 0.1) 0%, transparent 50%);
          }
        `
      }} />

      <Header />
      <main>
        <HeroSection />
        <FeaturesSection />
        <SimpleCTASection />
        <StatsSection />
        <TestimonialsSection />
        <FinalCTASection />
        <HowItWorksSection />
        <SingleTestimonialSection />
        <PricingSection />
        <FinalSimpleCTASection />
      </main>
      <Footer />
    </div>
  );
}
