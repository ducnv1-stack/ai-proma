import React, { useState } from 'react';

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
              Smart Project Management<br/>
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600">
                Powered by AI
              </span>
            </h1>
            <p className="text-lg text-gray-600 mb-6 leading-relaxed max-w-lg">
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
            <div className="relative bg-white rounded-3xl shadow-2xl overflow-hidden border border-gray-100">
              <img src="image-index/banner-index-proma.avif" alt="Proma AI Dashboard" className="w-full h-auto rounded-lg" />
            </div>

            {/* Floating Stats Cards */}
            <div className="absolute -top-3 -left-3 bg-white rounded-xl shadow-lg p-3 border border-gray-100 animate-bounce" style={{animationDelay: '0s', animationDuration: '6s'}}>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-xs font-medium text-gray-600">Projects Completed</span>
              </div>
              <div className="text-xl font-black text-gray-900 mt-1">94%</div>
            </div>

            <div className="absolute top-6 -right-3 bg-white rounded-xl shadow-lg p-3 border border-gray-100 animate-bounce" style={{animationDelay: '-2s', animationDuration: '6s'}}>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                <span className="text-xs font-medium text-gray-600">AI Insights</span>
              </div>
              <div className="text-lg font-black text-blue-600 mt-1">Real-time</div>
            </div>

            <div className="absolute bottom-6 -right-3 bg-white rounded-xl shadow-lg p-3 border border-gray-100 animate-bounce" style={{animationDelay: '-4s', animationDuration: '6s'}}>
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
    <section id="features" className="py-20 bg-gray-50">
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
            <div key={index} className="bg-white p-8 rounded-2xl shadow-md transition-all duration-300 hover:-translate-y-2 hover:shadow-xl">
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
    <section className="py-20 bg-gradient-to-br from-indigo-50 to-purple-50">
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
    'Integration with 100+ tools'
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
            Ready to revolutionize<br/>
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

        <Button variant="secondary" size="lg" className="bg-white text-indigo-600 hover:bg-gray-50 shadow-lg hover:shadow-xl">
          Start Your Free Trial Now
        </Button>
      </div>
    </section>
  );
};

// Main App Component
function App() {
  return (
    <div className="min-h-screen bg-white">
      {/* Include Font Awesome */}
      <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet" />
      
      <Header />
      <main>
        <HeroSection />
        <FeaturesSection />
        <SimpleCTASection />
        <StatsSection />
        <TestimonialsSection />
        <FinalCTASection />
      </main>
    </div>
  );
}

export default App;
