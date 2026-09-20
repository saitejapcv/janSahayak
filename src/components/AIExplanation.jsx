import React from 'react';
import { Sparkles, Bot } from 'lucide-react';
import { motion } from 'motion/react';

export default function AIExplanation({ answer, bedrockAvailable }) {
  // If bedrock is not available or answer contains the fallback string, render the reassuring citizen copy
  const isAvailable = Boolean(bedrockAvailable);
  const isBedrockErrorString = typeof answer === 'string' && (
    answer.toLowerCase().includes('bedrock') || 
    answer.toLowerCase().includes('temporarily unavailable')
  );

  const displayMessage = isAvailable && !isBedrockErrorString
    ? answer
    : "Here are the verified government schemes tailored to your query and profile. Review the eligibility requirements below to proceed with your application.";

  return (
    <motion.div 
      className="ai-guidance-card"
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <div className="ai-guidance-header">
        <div className="ai-icon-badge">
          <Sparkles size={16} />
        </div>
        <h3 className="ai-guidance-title">JanSahayak's Guidance</h3>
      </div>
      <p className="ai-guidance-text">
        {displayMessage}
      </p>
    </motion.div>
  );
}
