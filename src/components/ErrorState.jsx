import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';
import { motion } from 'motion/react';

export default function ErrorState({ onRetry }) {
  return (
    <motion.div 
      className="state-container"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="state-icon-circle state-icon-error">
        <AlertCircle size={32} />
      </div>

      <h3 className="state-title">Something went wrong</h3>

      <p className="state-desc">
        JanSahayak couldn't reach the scheme service right now. Please check your internet connection or try again.
      </p>

      <button
        type="button"
        className="state-action-btn"
        onClick={onRetry}
      >
        <RefreshCw size={16} />
        <span>Try again</span>
      </button>
    </motion.div>
  );
}
