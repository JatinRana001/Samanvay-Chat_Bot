import React from 'react';
import { AlertCircle } from 'lucide-react';

export default function Footer() {
  return (
    <footer style={{
      backgroundColor: '#0a2547',
      color: '#cbd5e1',
      padding: '32px 24px 20px',
      marginTop: 'auto',
      borderTop: '1px solid #1e3a5f'
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{
          backgroundColor: 'rgba(230, 81, 0, 0.12)',
          border: '1px solid rgba(230, 81, 0, 0.3)',
          borderRadius: '8px',
          padding: '12px 16px',
          display: 'flex',
          gap: '12px',
          alignItems: 'flex-start',
          marginBottom: '24px'
        }}>
          <AlertCircle size={18} color="#fb923c" style={{ flexShrink: 0, marginTop: '2px' }} />
          <p style={{ fontSize: '12px', color: '#fed7aa', lineHeight: 1.6 }}>
            <strong>Regulatory Guidance Notice:</strong> This assistant provides preliminary guidance based on available regulatory information. Actual approval requirements may vary based on project-specific conditions. Verify requirements with the relevant government authority before submitting an application.
          </p>
        </div>

        <div style={{
          display: 'flex',
          flexWrap: 'wrap',
          justifyContent: 'space-between',
          alignItems: 'center',
          gap: '16px',
          fontSize: '12px',
          borderTop: '1px solid rgba(255, 255, 255, 0.1)',
          paddingTop: '20px'
        }}>
          <div>
            <span style={{ fontWeight: '600', color: '#fff' }}>Samanvay (समन्वय)</span> — Single Window Facilitation Platform for Maharashtra Industries
          </div>
          <div style={{ display: 'flex', gap: '20px' }}>
            <span style={{ color: '#94a3b8' }}>Scope: State of Maharashtra, India</span>
            <span style={{ color: '#94a3b8' }}>•</span>
            <span style={{ color: '#94a3b8' }}>Deterministic Rules & Grounded RAG</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
