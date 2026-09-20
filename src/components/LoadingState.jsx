import React, { useState, useEffect } from 'react';
import { Loader2, Sparkles, Search } from 'lucide-react';
import { motion } from 'motion/react';

export default function LoadingState() {
  const [msgIndex, setMsgIndex] = useState(0);
  const messages = [
    "Finding schemes for you...",
    "Checking eligibility requirements...",
    "Matching state and central benefits...",
    "Verifying required documents..."
  ];

  useEffect(() => {
    const timer = setInterval(() => {
      setMsgIndex((prev) => (prev + 1) % messages.length);
    }, 1400);
    return () => clearInterval(timer);
  }, [messages.length]);

  return (
    <div className="state-container">
      <motion.div 
        className="state-icon-circle state-icon-loading"
        animate={{ rotate: 360 }}
        transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }}
      >
        <Loader2 size={32} />
      </motion.div>

      <motion.h3 
        key={msgIndex}
        className="state-title"
        initial={{ opacity: 0, y: 5 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -5 }}
      >
        {messages[msgIndex]}
      </motion.h3>

      <p className="state-desc">
        We're querying verified Indian government welfare portals to find matching benefits.
      </p>

      {/* Skeleton preview cards */}
      <div style={{ width: '100%', maxWidth: '820px', marginTop: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {[1, 2].map((n) => (
          <div key={n} className="skeleton-card">
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <div className="skeleton-line" style={{ width: '80px', height: '22px' }}></div>
              <div className="skeleton-line" style={{ width: '60px', height: '22px' }}></div>
            </div>
            <div className="skeleton-line" style={{ width: '65%', height: '26px' }}></div>
            <div className="skeleton-line" style={{ width: '90%', height: '16px' }}></div>
            <div className="skeleton-line" style={{ width: '75%', height: '16px' }}></div>
          </div>
        ))}
      </div>
    </div>
  );
}
