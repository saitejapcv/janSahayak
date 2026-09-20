import React, { useEffect } from 'react';
import { X, Search, UserCheck, Award, ArrowRight } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

export default function HowItWorksModal({ isOpen, onClose }) {
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose} role="dialog" aria-modal="true">
      <motion.div 
        className="modal-content"
        onClick={(e) => e.stopPropagation()}
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
      >
        <div className="modal-header">
          <h3 className="modal-title">How JanSahayak Works</h3>
          <button type="button" className="drawer-close-btn" onClick={onClose} aria-label="Close modal">
            <X size={20} />
          </button>
        </div>

        <div className="modal-body">
          <div className="step-item">
            <div className="step-number">1</div>
            <div className="step-content">
              <h4>Describe What You Need</h4>
              <p>Type in plain language what assistance you are looking for—whether it's college scholarships, farmer assistance, or health support.</p>
            </div>
          </div>

          <div className="step-item">
            <div className="step-number">2</div>
            <div className="step-content">
              <h4>Refine With Your Profile (Optional)</h4>
              <p>Provide basic details like your age, state, education level, or income. This instantly filters out schemes you aren't eligible for.</p>
            </div>
          </div>

          <div className="step-item">
            <div className="step-number">3</div>
            <div className="step-content">
              <h4>Review Schemes & Apply Directly</h4>
              <p>Explore concise summaries of benefits and checklist items, then click directly through to official government portals like the National Scholarship Portal (NSP) or state websites to apply.</p>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
