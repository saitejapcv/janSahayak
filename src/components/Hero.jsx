import React, { useEffect, useRef } from 'react';
import { Sparkles, ShieldCheck } from 'lucide-react';
import gsap from 'gsap';

export default function Hero() {
  const heroRef = useRef(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.from('.hero-pill', {
        opacity: 0,
        y: -15,
        duration: 0.6,
        ease: 'power2.out',
      });
      gsap.from('.hero-title', {
        opacity: 0,
        y: 20,
        duration: 0.8,
        delay: 0.1,
        ease: 'power3.out',
      });
      gsap.from('.hero-description', {
        opacity: 0,
        y: 15,
        duration: 0.8,
        delay: 0.25,
        ease: 'power3.out',
      });
    }, heroRef);

    return () => ctx.revert();
  }, []);

  return (
    <section className="hero-section" ref={heroRef}>
      <div className="container">
        <div className="hero-pill">
          <span className="hero-pill-dot"></span>
          <span>Verified Citizen Welfare Navigator</span>
        </div>

        <h1 className="hero-title">
          Find the government benefits <span>you may be eligible for</span>.
        </h1>

        <p className="hero-description">
          Tell JanSahayak what you need. We'll help you discover relevant government schemes, 
          understand the requirements, and figure out what to do next.
        </p>
      </div>
    </section>
  );
}
