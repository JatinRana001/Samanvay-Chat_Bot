import React from 'react';
import {
  Factory,
  FileCheck2,
  FolderCheck,
  Compass,
  HelpCircle,
  LayoutGrid,
  ArrowRight
} from 'lucide-react';

const ACTION_CARDS = [
  {
    id: 'start_industry',
    title: 'Start a New Industry',
    marathi: 'नवीन उद्योग सुरू करा',
    description: 'Determine your sector classification, required clearances, and initial planning roadmap in Maharashtra.',
    icon: Factory,
    accentColor: '#0e3768',
    badge: 'Step 1: Onboarding',
    prompt: 'I want to start a new industry in Maharashtra. Guide me through the initial classification and required clearances.'
  },
  {
    id: 'find_approvals',
    title: 'Find Required Approvals',
    marathi: 'आवश्यक परवानग्या शोधा',
    description: 'Find department-specific NOCs (MPCB Consent, Factory License, Fire NOC, DisCom power connection).',
    icon: FileCheck2,
    accentColor: '#e65100',
    badge: 'Statutory Clearances',
    prompt: 'What approvals and NOCs are mandatory for my manufacturing unit in Maharashtra?'
  },
  {
    id: 'check_documents',
    title: 'Check Documents',
    marathi: 'कागदपत्रे तपासा',
    description: 'Generate an audit checklist of required certificates, site plans, DPRs, and land title documents.',
    icon: FolderCheck,
    accentColor: '#0d9488',
    badge: 'Documentation',
    prompt: 'What documents do I need to prepare before applying for industrial approvals in Maharashtra?'
  },
  {
    id: 'understand_process',
    title: 'Understand the Setup Process',
    marathi: 'स्थापना प्रक्रिया समजून घ्या',
    description: 'Step-by-step guidance from land acquisition & MIDC allotment to construction and commercial production.',
    icon: Compass,
    accentColor: '#7c3aed',
    badge: 'Lifecycle Guide',
    prompt: 'Explain the sequential step-by-step process of setting up an industrial unit in Maharashtra.'
  },
  {
    id: 'ask_question',
    title: 'Ask a Question',
    marathi: 'प्रश्न विचारा',
    description: 'Ask specific questions regarding government fees, processing timelines, or policy incentives.',
    icon: HelpCircle,
    accentColor: '#ea580c',
    badge: 'Regulatory Q&A',
    prompt: 'How long does it take to obtain MPCB Consent to Establish and what are the official fees?'
  },
  {
    id: 'explore_industries',
    title: 'Explore Industries',
    marathi: 'उद्योग क्षेत्रे एक्सप्लोर करा',
    description: 'Browse Maharashtra focus sectors: Food Processing, Textiles, Auto Components, IT/ITES, Pharmaceuticals.',
    icon: LayoutGrid,
    accentColor: '#2563eb',
    badge: 'Focus Sectors',
    prompt: 'Tell me about the priority industrial sectors in Maharashtra and specific cluster locations.'
  }
];

export default function DashboardCards({ onSelectAction }) {
  return (
    <section style={{ margin: '32px 0 40px' }}>
      <div style={{ textAlign: 'center', marginBottom: '28px' }}>
        <h2 style={{
          fontSize: '26px',
          fontWeight: '700',
          color: '#0e3768',
          letterSpacing: '-0.02em',
          marginBottom: '8px'
        }}>
          How can we help you today?
        </h2>
        <p style={{ fontSize: '15px', color: '#475569', maxWidth: '640px', margin: '0 auto' }}>
          Select an action below to begin guided assessment or use the assistant below to enter your business details.
        </p>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
        gap: '20px'
      }}>
        {ACTION_CARDS.map((card) => {
          const Icon = card.icon;
          return (
            <div
              key={card.id}
              onClick={() => onSelectAction(card.prompt)}
              style={{
                backgroundColor: '#ffffff',
                border: '1px solid #e2e8f0',
                borderRadius: '12px',
                padding: '24px',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
                position: 'relative',
                overflow: 'hidden'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = card.accentColor;
                e.currentTarget.style.boxShadow = '0 6px 16px rgba(0,0,0,0.08)';
                e.currentTarget.style.transform = 'translateY(-2px)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = '#e2e8f0';
                e.currentTarget.style.boxShadow = '0 1px 3px rgba(0,0,0,0.04)';
                e.currentTarget.style.transform = 'translateY(0)';
              }}
            >
              <div style={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                height: '4px',
                backgroundColor: card.accentColor
              }} />

              <div>
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: '16px'
                }}>
                  <div style={{
                    width: '42px',
                    height: '42px',
                    borderRadius: '8px',
                    backgroundColor: `${card.accentColor}12`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: card.accentColor
                  }}>
                    <Icon size={22} />
                  </div>
                  <span style={{
                    fontSize: '11px',
                    fontWeight: '600',
                    color: '#64748b',
                    backgroundColor: '#f1f5f9',
                    padding: '3px 8px',
                    borderRadius: '4px',
                    textTransform: 'uppercase',
                    letterSpacing: '0.04em'
                  }}>
                    {card.badge}
                  </span>
                </div>

                <h3 style={{
                  fontSize: '17px',
                  fontWeight: '700',
                  color: '#0f172a',
                  marginBottom: '4px'
                }}>
                  {card.title}
                </h3>
                <div style={{
                  fontSize: '12px',
                  color: '#ea580c',
                  fontFamily: 'var(--font-marathi)',
                  fontWeight: '500',
                  marginBottom: '8px'
                }}>
                  {card.marathi}
                </div>
                <p style={{
                  fontSize: '13px',
                  color: '#475569',
                  lineHeight: 1.5,
                  marginBottom: '20px'
                }}>
                  {card.description}
                </p>
              </div>

              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                fontSize: '13px',
                fontWeight: '600',
                color: card.accentColor
              }}>
                <span>Open Assistant</span>
                <ArrowRight size={15} />
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
