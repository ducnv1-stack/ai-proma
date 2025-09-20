'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';

export const Header: React.FC = () => {
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

    return (
        <header className="bg-white/80 backdrop-blur-lg fixed top-0 left-0 right-0 z-50 shadow-sm">
            <div className="container mx-auto px-6 py-4 flex justify-between items-center max-w-7xl">
                {/* Logo */}
                <Link href="/" className="flex items-center space-x-3">
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
                </Link>

                {/* Desktop Navigation */}
                <nav className="hidden md:flex items-center space-x-8">
                    <a href="#features" className="text-gray-600 hover:text-indigo-600 transition">Features</a>
                    <a href="#pricing" className="text-gray-600 hover:text-indigo-600 transition">Pricing</a>
                    <a href="#reviews" className="text-gray-600 hover:text-indigo-600 transition">Reviews</a>
                    <a href="#contact" className="text-gray-600 hover:text-indigo-600 transition">Contact</a>
                </nav>

                {/* Desktop CTA Buttons */}
                <div className="hidden md:flex items-center space-x-4">
                    <Link href="/login" className="text-gray-600 hover:text-indigo-600 font-medium transition">
                        Sign In
                    </Link>
                    <Link href="/login">
                        <Button variant="primary" size="md">Try Free</Button>
                    </Link>
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
                    <Link href="/login" className="block py-2 text-gray-600 hover:text-indigo-600 font-medium">
                        Sign In
                    </Link>
                    <Link href="/login" className="block mt-4">
                        <Button variant="primary" size="md" className="w-full">Try Free</Button>
                    </Link>
                </div>
            )}
        </header>
    );
};
