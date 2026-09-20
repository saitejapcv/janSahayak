import React, { useState } from 'react';
import { UserCheck, ChevronDown, ChevronUp, Sparkles, RotateCcw } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

const INDIAN_STATES = [
  "All India",
  "Andhra Pradesh",
  "Arunachal Pradesh",
  "Assam",
  "Bihar",
  "Chhattisgarh",
  "Goa",
  "Gujarat",
  "Haryana",
  "Himachal Pradesh",
  "Jharkhand",
  "Karnataka",
  "Kerala",
  "Madhya Pradesh",
  "Maharashtra",
  "Manipur",
  "Meghalaya",
  "Mizoram",
  "Nagaland",
  "Odisha",
  "Punjab",
  "Rajasthan",
  "Sikkim",
  "Tamil Nadu",
  "Telangana",
  "Tripura",
  "Uttar Pradesh",
  "Uttarakhand",
  "West Bengal",
  "Andaman and Nicobar Islands",
  "Chandigarh",
  "Dadra and Nagar Haveli and Daman and Diu",
  "Delhi",
  "Jammu and Kashmir",
  "Ladakh",
  "Lakshadweep",
  "Puducherry"
];

const CATEGORIES = ["General", "OBC", "SC", "ST", "Other"];
const EDUCATION_LEVELS = [
  { value: "school", label: "School" },
  { value: "undergraduate", label: "Undergraduate" },
  { value: "postgraduate", label: "Postgraduate" },
  { value: "doctorate", label: "Doctorate / Ph.D." },
  { value: "diploma", label: "Diploma / Vocational" }
];

export default function ProfileForm({ profile, setProfile, onPreFillSample, onClearProfile }) {
  const [isOpen, setIsOpen] = useState(true);

  const handleChange = (field, value) => {
    setProfile(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const filledFieldsCount = Object.values(profile).filter(
    v => v !== '' && v !== undefined && v !== null
  ).length;

  return (
    <div className="profile-section">
      {/* Toggle header bar */}
      <button 
        type="button" 
        className="profile-toggle-bar"
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
      >
        <div className="profile-toggle-left">
          <div className="profile-toggle-icon">
            <UserCheck size={18} />
          </div>
          <div style={{ textAlign: 'left' }}>
            <div className="profile-toggle-title">
              Personal Eligibility Profile
            </div>
            <div className="profile-toggle-subtitle">
              Optional profile info helps find schemes you qualify for
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          {filledFieldsCount > 0 && (
            <span className="profile-badge">
              {filledFieldsCount} details filled
            </span>
          )}
          {isOpen ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
        </div>
      </button>

      {/* Accordion Body */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="profile-form-card"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
          >
            <div className="profile-header-actions">
              <span className="profile-helper-note">
                Fill in what you're comfortable sharing. All fields are optional.
              </span>
              <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                <button
                  type="button"
                  className="sample-fill-btn"
                  onClick={onPreFillSample}
                  title="Fill standard BTech undergraduate sample profile"
                >
                  <Sparkles size={14} />
                  <span>Demo Preset (BTech Student)</span>
                </button>

                {filledFieldsCount > 0 && (
                  <button
                    type="button"
                    className="clear-profile-btn"
                    onClick={onClearProfile}
                  >
                    Reset
                  </button>
                )}
              </div>
            </div>

            <div className="form-grid">
              {/* Age */}
              <div className="form-group">
                <label htmlFor="profile-age" className="form-label">
                  Age <span className="form-label-hint">Years</span>
                </label>
                <input
                  id="profile-age"
                  type="number"
                  min="1"
                  max="120"
                  className="form-input"
                  placeholder="e.g. 19"
                  value={profile.age ?? ''}
                  onChange={(e) => handleChange('age', e.target.value)}
                />
              </div>

              {/* Education Degree */}
              <div className="form-group">
                <label htmlFor="profile-education" className="form-label">
                  Degree / Education
                </label>
                <input
                  id="profile-education"
                  type="text"
                  className="form-input"
                  placeholder="e.g. BTech, 12th Pass, BSc"
                  value={profile.education ?? ''}
                  onChange={(e) => handleChange('education', e.target.value)}
                />
              </div>

              {/* Education Level */}
              <div className="form-group">
                <label htmlFor="profile-education-level" className="form-label">
                  Education Level
                </label>
                <select
                  id="profile-education-level"
                  className="form-select"
                  value={profile.education_level ?? ''}
                  onChange={(e) => handleChange('education_level', e.target.value)}
                >
                  <option value="">Select level (optional)</option>
                  {EDUCATION_LEVELS.map(lvl => (
                    <option key={lvl.value} value={lvl.value}>{lvl.label}</option>
                  ))}
                </select>
              </div>

              {/* Course / Discipline */}
              <div className="form-group">
                <label htmlFor="profile-course" className="form-label">
                  Course / Specialization
                </label>
                <input
                  id="profile-course"
                  type="text"
                  className="form-input"
                  placeholder="e.g. Computer Science, Agriculture"
                  value={profile.course ?? ''}
                  onChange={(e) => handleChange('course', e.target.value)}
                />
              </div>

              {/* Family Income */}
              <div className="form-group">
                <label htmlFor="profile-income" className="form-label">
                  Annual Family Income (₹)
                  {profile.family_income ? (
                    <span className="form-label-hint" style={{ color: 'var(--primary)', fontWeight: 600 }}>
                      ₹{Number(profile.family_income).toLocaleString('en-IN')}
                    </span>
                  ) : null}
                </label>
                <input
                  id="profile-income"
                  type="number"
                  min="0"
                  step="10000"
                  className="form-input"
                  placeholder="e.g. 300000"
                  value={profile.family_income ?? ''}
                  onChange={(e) => handleChange('family_income', e.target.value)}
                />
              </div>

              {/* State */}
              <div className="form-group">
                <label htmlFor="profile-state" className="form-label">
                  State / Union Territory
                </label>
                <select
                  id="profile-state"
                  className="form-select"
                  value={profile.state ?? ''}
                  onChange={(e) => handleChange('state', e.target.value)}
                >
                  <option value="">Select State (optional)</option>
                  {INDIAN_STATES.map(st => (
                    <option key={st} value={st}>{st}</option>
                  ))}
                </select>
              </div>

              {/* Category */}
              <div className="form-group">
                <label htmlFor="profile-category" className="form-label">
                  Social Category
                </label>
                <select
                  id="profile-category"
                  className="form-select"
                  value={profile.category ?? ''}
                  onChange={(e) => handleChange('category', e.target.value)}
                >
                  <option value="">Select Category (optional)</option>
                  {CATEGORIES.map(cat => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              </div>

              {/* Disability Status */}
              <div className="form-group">
                <label className="form-label">
                  Person with Disability (PwD)
                </label>
                <div className="form-radio-group">
                  <div
                    className={`radio-pill ${profile.disability === false ? 'active' : ''}`}
                    onClick={() => handleChange('disability', false)}
                  >
                    No
                  </div>
                  <div
                    className={`radio-pill ${profile.disability === true ? 'active' : ''}`}
                    onClick={() => handleChange('disability', true)}
                  >
                    Yes
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
