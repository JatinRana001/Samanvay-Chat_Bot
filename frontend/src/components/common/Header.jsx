import React from 'react';
import { Building2, ShieldCheck } from 'lucide-react';

export default function Header() {
  return (
    <header style={{
      backgroundColor: 'var(--gov-surface)',
      borderBottom: '1px solid var(--gov-border)',
      boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
    }}>
      <div style={{
        backgroundColor: '#0a2547',
        color: '#f8fafc',
        padding: '6px 24px',
        fontSize: '12px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        borderBottom: '2px solid #e65100'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontWeight: '700', letterSpacing: '0.5px' }}>महाराष्ट्र शासन</span>
          <span style={{ opacity: 0.6 }}>|</span>
          <span>Government of Maharashtra — Industry & Commerce Department</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', fontSize: '11px', opacity: 0.9 }}>
          <span>MAITRI Integrated Single Window</span>
          <span>•</span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <ShieldCheck size={13} color="#4ade80" /> Verified Regulatory Data
          </span>
        </div>
      </div>

      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '16px 24px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{
            width: '44px',
            height: '44px',
            backgroundColor: '#0e3768',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
            boxShadow: '0 2px 4px rgba(14,55,104,0.2)'
          }}>
            <Building2 size={26} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
              <h1 style={{ fontSize: '20px', fontWeight: '700', color: '#0e3768', letterSpacing: '-0.02em' }}>
                Samanvay <span style={{ fontFamily: 'var(--font-marathi)', fontWeight: '600', color: '#e65100' }}>समन्वय</span>
              </h1>
              <span style={{
                backgroundColor: '#fef3c7',
                color: '#92400e',
                fontSize: '11px',
                fontWeight: '600',
                padding: '2px 8px',
                borderRadius: '12px',
                border: '1px solid #fde68a'
              }}>
                Prototype v1.0
              </span>
            </div>
            <p style={{ fontSize: '13px', color: '#475569', marginTop: '2px' }}>
              Maharashtra Industry Setup & Regulatory Approval Navigation Assistant
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            backgroundColor: '#f1f5f9',
            padding: '6px 12px',
            borderRadius: '6px',
            fontSize: '12px',
            color: '#334155',
            fontWeight: '500'
          }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#22c55e' }}></span>
            <span>Deterministic Rules Engine Active</span>
          </div>
        </div>
      </div>
    </header>
  );
}
