import React from 'react';
import { SearchX, RotateCcw, ArrowRight } from 'lucide-react';
import { motion } from 'motion/react';

const SUGGESTIONS = [
  "Scholarship for undergraduate students",
  "Financial assistance for farmers",
  "Healthcare support",
  "Employment scheme",
  "Postgraduate technical education grant"
];

export default function EmptyState({ onSelectSuggestion, onResetSearch }) {
  return (
    <motion.div 
      className="state-container"
      initial={{ opacity: 0, scale: 0.96 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4 }}
    >
      <div className="state-icon-circle state-icon-empty">
        <SearchX size={32} />
      </div>

      <h3 className="state-title">No matching schemes found</h3>

      <p className="state-desc">
        Try describing your need differently or adjust your profile filters.
      </p>

      <div className="state-suggestions">
        <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)' }}>
          Try one of these searches:
        </span>
        {SUGGESTIONS.map((s, idx) => (
          <button
            key={idx}
            type="button"
            className="state-suggestion-pill"
            onClick={() => onSelectSuggestion(s)}
          >
            {s} →
          </button>
        ))}
      </div>

      <button
        type="button"
        className="state-action-btn"
        onClick={onResetSearch}
      >
        <RotateCcw size={16} />
        <span>Try another search</span>
      </button>
    </motion.div>
  );
}
