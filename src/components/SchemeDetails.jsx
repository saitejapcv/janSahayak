import React, { useEffect } from 'react';
import { 
  X, 
  ExternalLink, 
  CheckCircle2, 
  FileText, 
  Award, 
  UserCheck, 
  ArrowUpRight, 
  Calendar, 
  Compass, 
  ShieldCheck,
  Building
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

export default function SchemeDetails({ scheme, onClose }) {
  // Listen for Escape key to close
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  if (!scheme) return null;

  const {
    id,
    name,
    category,
    level,
    state,
    description,
    benefits = [],
    eligibility = [],
    required_documents = [],
    application_process,
    official_url,
    source_url,
    last_verified
  } = scheme;

  return (
    <AnimatePresence>
      <div 
        className="drawer-backdrop" 
        onClick={onClose}
        role="dialog"
        aria-modal="true"
        aria-labelledby="drawer-title"
      >
        <motion.div
          className="drawer-panel"
          onClick={(e) => e.stopPropagation()} // Prevent backdrop click when clicking inside panel
          initial={{ x: '100%' }}
          animate={{ x: 0 }}
          exit={{ x: '100%' }}
          transition={{ type: 'spring', damping: 28, stiffness: 280 }}
        >
          {/* Drawer Header */}
          <div className="drawer-header">
            <div className="scheme-badges">
              {category && <span className="badge badge-category">{category}</span>}
              {level && <span className="badge badge-level">{level}</span>}
              {state && <span className="badge badge-state">{state}</span>}
            </div>
            <button
              type="button"
              className="drawer-close-btn"
              onClick={onClose}
              aria-label="Close details"
            >
              <X size={20} />
            </button>
          </div>

          {/* Drawer Scrollable Content */}
          <div className="drawer-body">
            <div>
              {id && <span className="scheme-id">{id}</span>}
              <h2 id="drawer-title" className="drawer-scheme-title">
                {name}
              </h2>
            </div>

            {/* Official Action CTA if official_url is present */}
            {official_url && (
              <div className="drawer-actions" style={{ border: 'none', paddingTop: 0 }}>
                <a
                  href={official_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="apply-btn"
                >
                  <span>Apply / Visit Official Portal</span>
                  <ArrowUpRight size={18} />
                </a>
              </div>
            )}

            {/* 1. About this scheme */}
            {description && (
              <div className="drawer-section">
                <h3 className="drawer-section-title">
                  <Building size={18} />
                  <span>About this scheme</span>
                </h3>
                <p style={{ fontSize: '0.95rem', lineHeight: '1.6', color: 'var(--text-body)' }}>
                  {description}
                </p>
              </div>
            )}

            {/* 2. Benefits */}
            {benefits && benefits.length > 0 && (
              <div className="drawer-section">
                <h3 className="drawer-section-title">
                  <Award size={18} />
                  <span>Benefits & Assistance</span>
                </h3>
                <ul className="drawer-list">
                  {benefits.map((benefit, idx) => (
                    <li key={idx} className="drawer-list-item">
                      <CheckCircle2 size={18} className="icon-check" />
                      <span>{benefit}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* 3. Eligibility */}
            {eligibility && eligibility.length > 0 && (
              <div className="drawer-section">
                <h3 className="drawer-section-title">
                  <UserCheck size={18} />
                  <span>Eligibility Requirements</span>
                </h3>
                <ul className="drawer-list">
                  {eligibility.map((crit, idx) => (
                    <li key={idx} className="drawer-list-item">
                      <CheckCircle2 size={18} className="icon-check" />
                      <span>{crit}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* 4. Required Documents */}
            {required_documents && required_documents.length > 0 && (
              <div className="drawer-section">
                <h3 className="drawer-section-title">
                  <FileText size={18} />
                  <span>Required Documents</span>
                </h3>
                <ul className="drawer-list">
                  {required_documents.map((doc, idx) => (
                    <li key={idx} className="drawer-list-item">
                      <span className="icon-bullet" style={{ fontWeight: 700, fontSize: '1rem' }}>•</span>
                      <span>{doc}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* 5. Application Process */}
            {application_process && (
              <div className="drawer-section">
                <h3 className="drawer-section-title">
                  <Compass size={18} />
                  <span>Application Process</span>
                </h3>
                <div className="drawer-process-box">
                  {application_process}
                </div>
              </div>
            )}

            {/* 6. Footer Links & Verification */}
            <div className="drawer-actions">
              {official_url && (
                <a
                  href={official_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="apply-btn"
                >
                  <span>Apply / Visit Official Portal</span>
                  <ArrowUpRight size={18} />
                </a>
              )}

              {source_url && (
                <a
                  href={source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="source-link-btn"
                >
                  <span>View scheme source on myScheme</span>
                  <ExternalLink size={14} />
                </a>
              )}

              {last_verified && (
                <div style={{ textAlign: 'center', fontSize: '0.8rem', color: 'var(--text-subtle)', marginTop: '0.5rem' }}>
                  <Calendar size={13} style={{ display: 'inline', verticalAlign: 'middle', marginRight: '4px' }} />
                  Data verified as of {last_verified}
                </div>
              )}
            </div>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
