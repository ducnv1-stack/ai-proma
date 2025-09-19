'use client';

import { useState, useEffect } from 'react';
import { ChevronDownIcon, SparklesIcon, CheckIcon } from '@heroicons/react/24/outline';
import { aiService, Agent } from '../services/AI.service';

interface AgentSelectorProps {
  selectedAgentId?: string;
  onAgentSelect: (agent: Agent) => void;
  className?: string;
}

export default function AgentSelector({ selectedAgentId, onAgentSelect, className = '' }: AgentSelectorProps) {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadAgents();
  }, []);

  useEffect(() => {
    if (selectedAgentId && agents.length > 0) {
      const agent = agents.find(a => a.id === selectedAgentId);
      if (agent) {
        setSelectedAgent(agent);
      }
    } else if (agents.length > 0 && !selectedAgent) {
      // Auto-select first agent if none selected
      const defaultAgent = agents[0];
      setSelectedAgent(defaultAgent);
      onAgentSelect(defaultAgent);
    }
  }, [selectedAgentId, agents, selectedAgent, onAgentSelect]);

  const loadAgents = async () => {
    try {
      setIsLoading(true);
      const response = await aiService.getAgents();
      setAgents(response.agents);
    } catch (error) {
      console.error('Failed to load agents:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAgentSelect = (agent: Agent) => {
    setSelectedAgent(agent);
    onAgentSelect(agent);
    setIsOpen(false);
  };

  if (isLoading) {
    return (
      <div className={`flex items-center space-x-2 p-3 bg-gray-100 rounded-lg animate-pulse ${className}`}>
        <div className="w-6 h-6 bg-gray-300 rounded"></div>
        <div className="flex-1 h-4 bg-gray-300 rounded"></div>
      </div>
    );
  }

  return (
    <div className={`relative ${className}`}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-3 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-blue-800 rounded-lg flex items-center justify-center">
            <SparklesIcon className="w-5 h-5 text-white" />
          </div>
          <div className="text-left">
            <p className="font-medium text-gray-900">
              {selectedAgent?.name || 'Select Agent'}
            </p>
            <p className="text-sm text-gray-500 truncate max-w-48">
              {selectedAgent?.description || 'Choose an AI agent to assist you'}
            </p>
          </div>
        </div>
        <ChevronDownIcon 
          className={`w-5 h-5 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} 
        />
      </button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div 
            className="fixed inset-0 z-10" 
            onClick={() => setIsOpen(false)}
          />
          
          {/* Dropdown */}
          <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-20 max-h-60 overflow-y-auto">
            {agents.length === 0 ? (
              <div className="p-4 text-center text-gray-500">
                No agents available
              </div>
            ) : (
              agents.map((agent) => (
                <button
                  key={agent.id}
                  onClick={() => handleAgentSelect(agent)}
                  className="w-full flex items-center space-x-3 p-3 hover:bg-gray-50 transition-colors text-left"
                >
                  <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-blue-800 rounded-lg flex items-center justify-center">
                    <SparklesIcon className="w-5 h-5 text-white" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-gray-900">{agent.name}</p>
                    <p className="text-sm text-gray-500 truncate">{agent.description}</p>
                  </div>
                  {selectedAgent?.id === agent.id && (
                    <CheckIcon className="w-5 h-5 text-blue-600" />
                  )}
                </button>
              ))
            )}
          </div>
        </>
      )}
    </div>
  );
}
