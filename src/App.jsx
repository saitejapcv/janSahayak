import React, { useState, useRef } from 'react';
import Header from './components/Header';
import Hero from './components/Hero';
import SearchForm from './components/SearchForm';
import ProfileForm from './components/ProfileForm';
import AIExplanation from './components/AIExplanation';
import SchemeCard from './components/SchemeCard';
import SchemeDetails from './components/SchemeDetails';
import LoadingState from './components/LoadingState';
import EmptyState from './components/EmptyState';
import ErrorState from './components/ErrorState';
import HowItWorksModal from './components/HowItWorksModal';
import AboutModal from './components/AboutModal';
import { searchSchemes } from './services/api';
import { Landmark, ShieldCheck, Heart } from 'lucide-react';
import { motion } from 'motion/react';

const INITIAL_PROFILE = {
  age: '',
  education: '',
  education_level: '',
  course: '',
  family_income: '',
  state: '',
  category: '',
  disability: false,
};

export default function App() {
  const [query, setQuery] = useState('');
  const [profile, setProfile] = useState(INITIAL_PROFILE);
  const [searchResponse, setSearchResponse] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [selectedScheme, setSelectedScheme] = useState(null);

  // Modals
  const [howItWorksOpen, setHowItWorksOpen] = useState(false);
  const [aboutOpen, setAboutOpen] = useState(false);

  const resultsRef = useRef(null);

  const handleSearch = async (forcedQuery = null, forcedProfile = null) => {
    const activeQuery = forcedQuery !== null ? forcedQuery : query;
    const activeProfile = forcedProfile !== null ? forcedProfile : profile;

    setIsLoading(true);
    setError(null);
    setHasSearched(true);

    try {
      const data = await searchSchemes(activeQuery, activeProfile);
      setSearchResponse(data);

      // Smooth scroll down to results after state settles
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 150);
    } catch (err) {
      setError(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePreFillSample = () => {
    const sampleQuery = "I need a scholarship for my BTech";
    const sampleProfile = {
      age: 19,
      education: "BTech",
      education_level: "undergraduate",
      course: "Computer Science",
      family_income: 300000,
      state: "Tamil Nadu",
      category: "General",
      disability: false
    };
    setQuery(sampleQuery);
    setProfile(sampleProfile);
  };

  const handleClearProfile = () => {
    setProfile(INITIAL_PROFILE);
  };

  const handleResetSearch = () => {
    setQuery('');
    setProfile(INITIAL_PROFILE);
    setSearchResponse(null);
    setHasSearched(false);
    setError(null);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleSelectSuggestion = (suggestionText) => {
    setQuery(suggestionText);
    handleSearch(suggestionText, profile);
  };

  const matches = searchResponse?.matches || [];
  const resultCount = matches.length;

  return (
    <div className="app-layout">
      {/* Header Navigation */}
      <Header
        onOpenHowItWorks={() => setHowItWorksOpen(true)}
        onOpenAbout={() => setAboutOpen(true)}
        onResetSearch={handleResetSearch}
      />

      <main id="main-content">
        {/* Hero Banner */}
        <Hero />

        {/* Search & Profile Section */}
        <div className="container">
          <SearchForm
            query={query}
            setQuery={setQuery}
            onSearch={() => handleSearch()}
            isLoading={isLoading}
          />

          <ProfileForm
            profile={profile}
            setProfile={setProfile}
            onPreFillSample={handlePreFillSample}
            onClearProfile={handleClearProfile}
          />
        </div>

        {/* Results Container */}
        <div className="container" ref={resultsRef}>
          {isLoading && (
            <div className="results-container">
              <LoadingState />
            </div>
          )}

          {!isLoading && error && (
            <div className="results-container">
              <ErrorState onRetry={() => handleSearch()} />
            </div>
          )}

          {!isLoading && !error && hasSearched && resultCount === 0 && (
            <div className="results-container">
              <EmptyState 
                onSelectSuggestion={handleSelectSuggestion}
                onResetSearch={handleResetSearch}
              />
            </div>
          )}

          {!isLoading && !error && hasSearched && resultCount > 0 && (
            <div className="results-container">
              {/* AI Guidance Box */}
              <AIExplanation
                answer={searchResponse?.answer}
                bedrockAvailable={searchResponse?.bedrock_available}
              />

              {/* Results Header */}
              <div className="results-header">
                <div className="results-heading-group">
                  <h2>Schemes we found</h2>
                  <p className="results-subtitle">
                    Based on your query and eligibility profile.
                  </p>
                </div>
                <span className="results-count-badge">
                  {resultCount} {resultCount === 1 ? 'scheme' : 'schemes'} found
                </span>
              </div>

              {/* Schemes Grid */}
              <div className="schemes-grid">
                {matches.map((scheme, index) => (
                  <SchemeCard
                    key={scheme.id || index}
                    scheme={scheme}
                    index={index}
                    onViewDetails={(s) => setSelectedScheme(s)}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Slide-out Scheme Details Drawer */}
      <SchemeDetails
        scheme={selectedScheme}
        onClose={() => setSelectedScheme(null)}
      />

      {/* Info Modals */}
      <HowItWorksModal
        isOpen={howItWorksOpen}
        onClose={() => setHowItWorksOpen(false)}
      />
      <AboutModal
        isOpen={aboutOpen}
        onClose={() => setAboutOpen(false)}
      />

      {/* Footer */}
      <footer className="site-footer">
        <div className="container footer-inner">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--primary)', fontWeight: 700 }}>
            <Landmark size={18} />
            <span>JanSahayak</span>
          </div>
          <p className="footer-disclaimer">
            JanSahayak is an open, citizen-first public benefits navigator. All scheme information and application processes are grounded in verified central and state government records.
          </p>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-subtle)' }}>
            Empowering Indian citizens with direct access to government welfare.
          </div>
        </div>
      </footer>
    </div>
  );
}
