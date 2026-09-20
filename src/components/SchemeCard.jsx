import React from 'react';
import { CheckCircle2, ArrowRight, Calendar, ShieldCheck, Tag } from 'lucide-react';
import { motion } from 'motion/react';

export default function SchemeCard({ scheme, onViewDetails, index = 0 }) {
  const {
    id,
    name,
    category,
    level,
    state,
    description,
    benefits = [],
    eligibility = [],
    last_verified
  } = scheme;

  // Pick top 2 benefits and top 2 eligibility highlights for scannability
  const benefitHighlights = Array.isArray(benefits) ? benefits.slice(0, 2) : [];
  const eligibilityHighlights = Array.isArray(eligibility) ? eligibility.slice(0, 2) : [];

  return (
    <motion.article 
      className="scheme-card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.08 }}
      whileHover={{ y: -3 }}
      layout
    >
      <div className="scheme-card-top">
        <div className="scheme-badges">
          {category && (
            <span className="badge badge-category">{category}</span>
          )}
          {level && (
            <span className="badge badge-level">{level}</span>
          )}
          {state && state !== 'All India' && (
            <span className="badge badge-state">{state}</span>
          )}
        </div>
        {id && <span className="scheme-id">{id}</span>}
      </div>

      <h3 className="scheme-title">{name}</h3>

      <p className="scheme-description">
        {description}
      </p>

      {/* Scannable highlights */}
      {(benefitHighlights.length > 0 || eligibilityHighlights.length > 0) && (
        <div className="scheme-highlights">
          {benefitHighlights.map((benefit, i) => (
            <div key={`b-${i}`} className="highlight-item">
              <CheckCircle2 size={16} className="highlight-check" />
              <span><strong>Benefit:</strong> {benefit}</span>
            </div>
          ))}
          {eligibilityHighlights.map((crit, i) => (
            <div key={`e-${i}`} className="highlight-item">
              <CheckCircle2 size={16} className="highlight-check" />
              <span><strong>Requirement:</strong> {crit}</span>
            </div>
          ))}
        </div>
      )}

      <div className="scheme-card-footer">
        <div className="scheme-verified">
          <Calendar size={14} />
          <span>
            {last_verified ? `Verified ${last_verified}` : 'Official Government Scheme'}
          </span>
        </div>

        <button
          type="button"
          className="view-details-btn"
          onClick={() => onViewDetails(scheme)}
          aria-label={`View details for ${name}`}
        >
          <span>View details</span>
          <ArrowRight size={16} />
        </button>
      </div>
    </motion.article>
  );
}
