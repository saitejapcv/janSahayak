import React, { useEffect } from 'react';
import { X, ShieldCheck, HeartHandshake, Database } from 'lucide-react';
import { motion } from 'motion/react';

export default function AboutModal({ isOpen, onClose }) {
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
          <h3 className="modal-title">About JanSahayak</h3>
          <button type="button" className="drawer-close-btn" onClick={onClose} aria-label="Close modal">
            <X size={20} />
          </button>
        </div>

        <div className="modal-body">
          <p>
            <strong>JanSahayak</strong> (जन सहायक - "Citizen's Helper") is an open civic-tech platform designed to simplify access to Indian government welfare schemes and public services.
          </p>

          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
            <Database size={20} style={{ color: 'var(--primary)', flexShrink: 0, marginTop: '2px' }} />
            <div>
              <h4 style={{ fontSize: '0.9375rem', fontWeight: 600, color: 'var(--text-main)' }}>Official Sources</h4>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                Data is sourced from verified national repositories including myScheme.gov.in, National Scholarship Portal (NSP), and official central & state department records.
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
            <ShieldCheck size={20} style={{ color: 'var(--success)', flexShrink: 0, marginTop: '2px' }} />
            <div>
              <h4 style={{ fontSize: '0.9375rem', fontWeight: 600, color: 'var(--text-main)' }}>Citizen Privacy First</h4>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                JanSahayak does not collect Aadhaar numbers, passwords, or personal banking credentials. All eligibility matching happens on the fly without storing citizen profiles.
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
            <HeartHandshake size={20} style={{ color: 'var(--accent)', flexShrink: 0, marginTop: '2px' }} />
            <div>
              <h4 style={{ fontSize: '0.9375rem', fontWeight: 600, color: 'var(--text-main)' }}>Direct Portal Applications</h4>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                You apply directly on the government's official portals—ensuring safe, direct benefit transfers (DBT) into your Aadhaar-linked account.
              </p>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
