import React from 'react';
import { Search, ArrowRight, Sparkles } from 'lucide-react';
import { motion } from 'motion/react';

const SUGGESTIONS = [
  "I need a scholarship for my BTech",
  "Higher education fellowship",
  "Scholarship for undergraduate students",
  "Agriculture and farmer assistance",
];

export default function SearchForm({ query, setQuery, onSearch, isLoading }) {
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!query.trim() && !isLoading) return;
    onSearch();
  };

  const handleChipClick = (text) => {
    setQuery(text);
  };

  return (
    <motion.div 
      className="search-card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
    >
      <form onSubmit={handleSubmit} role="search">
        <div className="search-input-wrapper">
          <Search size={22} className="text-muted" style={{ color: 'var(--text-muted)' }} />
          <input
            id="scheme-search-input"
            type="text"
            className="search-input"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g. I need a scholarship for my BTech..."
            disabled={isLoading}
            aria-label="Describe what government scheme or benefit you need"
          />
          <motion.button
            id="find-schemes-btn"
            type="submit"
            className="search-btn"
            disabled={isLoading}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            {isLoading ? (
              <>
                <Sparkles size={18} className="animate-spin" />
                <span>Searching...</span>
              </>
            ) : (
              <>
                <span>Find Schemes</span>
                <ArrowRight size={18} />
              </>
            )}
          </motion.button>
        </div>

        {/* Quick Suggestion Chips */}
        <div className="quick-prompts">
          <span className="quick-prompt-label">Quick suggestions:</span>
          {SUGGESTIONS.map((suggestion, idx) => (
            <button
              key={idx}
              type="button"
              className="quick-chip"
              onClick={() => handleChipClick(suggestion)}
              disabled={isLoading}
            >
              {suggestion}
            </button>
          ))}
        </div>
      </form>
    </motion.div>
  );
}
