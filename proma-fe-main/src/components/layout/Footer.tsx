import React from 'react';

export const Footer: React.FC = () => {
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
