import React, { useState } from 'react';
import { Landmark, HelpCircle, Info, Menu, X, Sparkles } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

export default function Header({ onOpenHowItWorks, onOpenAbout, onResetSearch }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="site-header">
      <div className="container header-inner">
        {/* Brand Logo & Tagline */}
        <a 
          href="#" 
          className="brand-wrapper"
          onClick={(e) => {
            e.preventDefault();
            onResetSearch?.();
          }}
          aria-label="JanSahayak Home"
        >
          <div className="brand-logo-badge">
            <Landmark size={22} strokeWidth={2.2} />
          </div>
          <div className="brand-text">
            <div className="brand-name">
              Jan<span>Sahayak</span>
            </div>
            <span className="brand-tagline">Government Benefits, Simplified.</span>
          </div>
        </a>

        {/* Desktop Navigation */}
        <nav className="nav-desktop" aria-label="Main Navigation">
          <button 
            type="button" 
            className="nav-link"
            onClick={onResetSearch}
          >
            Home
          </button>
          <button 
            type="button" 
            className="nav-link"
            onClick={onOpenHowItWorks}
          >
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem' }}>
              <HelpCircle size={16} />
              How it works
            </span>
          </button>
          <button 
            type="button" 
            className="nav-link"
            onClick={onOpenAbout}
          >
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem' }}>
              <Info size={16} />
              About
            </span>
          </button>
        </nav>

        {/* Mobile menu trigger */}
        <button
          type="button"
          className="mobile-menu-btn"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-label="Toggle navigation menu"
        >
          {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Mobile Drawer */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div 
            className="mobile-nav-panel"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            style={{
              position: 'absolute',
              top: '70px',
              left: 0,
              right: 0,
              background: '#ffffff',
              borderBottom: '1px solid var(--border)',
              padding: '1.25rem',
              display: 'flex',
              flexDirection: 'column',
              gap: '0.75rem',
              boxShadow: 'var(--shadow-lg)'
            }}
          >
            <button 
              type="button" 
              className="nav-link"
              style={{ textAlign: 'left', width: '100%' }}
              onClick={() => {
                setMobileMenuOpen(false);
                onResetSearch?.();
              }}
            >
              Home
            </button>
            <button 
              type="button" 
              className="nav-link"
              style={{ textAlign: 'left', width: '100%' }}
              onClick={() => {
                setMobileMenuOpen(false);
                onOpenHowItWorks();
              }}
            >
              How it works
            </button>
            <button 
              type="button" 
              className="nav-link"
              style={{ textAlign: 'left', width: '100%' }}
              onClick={() => {
                setMobileMenuOpen(false);
                onOpenAbout();
              }}
            >
              About
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}
