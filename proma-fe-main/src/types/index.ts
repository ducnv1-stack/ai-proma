// TypeScript interfaces for components
import { ReactNode } from 'react';

export interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  children: ReactNode;
  onClick?: () => void;
  className?: string;
}

export interface FeatureItem {
  icon: string;
  title: string;
  description: string;
  bgColor: string;
  textColor: string;
  titleGradient?: boolean;
}

export interface TestimonialItem {
  name: string;
  position: string;
  content: string;
  avatar: string;
  avatarColor: string;
}

export interface StatItem {
  icon: string;
  value: string;
  label: string;
  subtitle: string;
}

export interface StepItem {
  number: string;
  title: string;
  description: string;
  color: string;
}

export interface PricingPlan {
  name: string;
  description: string;
  price: string;
  priceUnit?: string;
  features: string[];
  buttonText: string;
  buttonClass: string;
  cardClass: string;
  popular?: boolean;
}
