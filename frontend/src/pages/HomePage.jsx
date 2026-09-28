import React, { useState, useRef } from 'react';
import Header from '../components/common/Header';
import Footer from '../components/common/Footer';
import DashboardCards from '../components/dashboard/DashboardCards';
import ChatWidget from '../components/chat/ChatWidget';
import WebsiteHelpWidget from '../components/chat/WebsiteHelpWidget';
import { Sparkles, CheckCircle } from 'lucide-react';

export default function HomePage() {
  const [selectedPrompt, setSelectedPrompt] = useState('');
  const chatRef = useRef(null);

  const handleSelectCardAction = (prompt) => {
    setSelectedPrompt(prompt);
    if (chatRef.current) {
      chatRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Header />

      <main style={{ flex: 1, maxWidth: '1200px', margin: '0 auto', padding: '32px 24px', width: '100%' }}>
        <section style={{
          backgroundColor: '#ffffff',
          border: '1px solid #e2e8f0',
          borderRadius: '16px',
          padding: '36px 32px',
          marginBottom: '32px',
          backgroundImage: 'radial-gradient(#0e376808 1px, transparent 1px)',
          backgroundSize: '16px 16px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.02)'
        }}>
          <div style={{ maxWidth: '800px' }}>
            <div style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              backgroundColor: '#eff6ff',
              color: '#1d4ed8',
              fontSize: '12px',
              fontWeight: '600',
              padding: '4px 12px',
              borderRadius: '20px',
              marginBottom: '16px'
            }}>
              <Sparkles size={14} />
              <span>Maharashtra Single-Window Industrial Advisory</span>
            </div>

            <h1 style={{
              fontSize: '32px',
              fontWeight: '800',
              color: '#0a2547',
              letterSpacing: '-0.03em',
              lineHeight: 1.2,
              marginBottom: '12px'
            }}>
              Set Up & Scale Your Industrial Unit in Maharashtra
            </h1>

            <p style={{
              fontSize: '16px',
              color: '#475569',
              lineHeight: 1.6,
              marginBottom: '24px'
            }}>
              Navigate required government approvals, environmental consents (MPCB), MIDC procedures, and statutory licenses with deterministic accuracy grounded in official government resolutions.
            </p>

            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '20px', fontSize: '13px', color: '#334155' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <CheckCircle size={16} color="#16a34a" />
                <span>Deterministic Rules Engine</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <CheckCircle size={16} color="#16a34a" />
                <span>Verified Source Citations</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <CheckCircle size={16} color="#16a34a" />
                <span>Zero Hallucination Architecture</span>
              </div>
            </div>
          </div>
        </section>

        <DashboardCards onSelectAction={handleSelectCardAction} />

        <section ref={chatRef} style={{ marginTop: '48px', marginBottom: '32px' }}>
          <div style={{ marginBottom: '16px' }}>
            <h2 style={{ fontSize: '20px', fontWeight: '700', color: '#0e3768' }}>
              Interactive Setup & Approval Assistant
            </h2>
            <p style={{ fontSize: '13px', color: '#64748b' }}>
              Enter details below to calculate your required clearances, fees, and next steps.
            </p>
          </div>

          <ChatWidget initialPrompt={selectedPrompt} />
        </section>
      </main>

      <Footer />
      <WebsiteHelpWidget />
    </div>
  );
}
