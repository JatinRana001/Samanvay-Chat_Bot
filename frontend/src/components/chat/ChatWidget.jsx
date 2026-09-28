import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, RefreshCw, CheckCircle2, Building, MapPin, IndianRupee, Users, ArrowRight, ExternalLink } from 'lucide-react';
import { checkApiHealth, sendChatMessage, recommendApprovals } from '../../services/api';
import styles from './ChatWidget.module.css';

const STARTER_PROMPTS = [
  "I want to set up an automobile component manufacturing unit in Chhatrapati Sambhajinagar.",
  "What approvals are required for a food processing unit in Pune with 2.5 Crore investment?",
  "Tell me the required documents and pollution NOC for a textile unit in Nashik.",
  "What are the baseline steps to set up an IT/ITES unit in Mumbai?"
];

export default function ChatWidget({ initialPrompt = '', compact = false }) {
  const [sessionId, setSessionId] = useState(() => 'sess-' + Math.random().toString(36).substring(2, 9));
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [currentProfile, setCurrentProfile] = useState({});
  const [quickSuggestions, setQuickSuggestions] = useState([]);
  const [isReady, setIsReady] = useState(false);
  const [recommendations, setRecommendations] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping, recommendations]);

  useEffect(() => {
    checkApiHealth().catch((error) => {
      console.warn('[Samanvay] Backend health check failed on chat mount.', error);
    });
  }, []);

  useEffect(() => {
    if (initialPrompt) {
      setInputValue(initialPrompt);
    }
  }, [initialPrompt]);

  const handleSendMessage = async (textToSend) => {
    const text = textToSend || inputValue;
    if (!text.trim()) return;

    const userMessage = {
      id: Date.now(),
      sender: 'user',
      text: text.trim(),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    try {
      const data = await sendChatMessage(sessionId, text.trim());
      
      setSessionId(data.session_id);
      setCurrentProfile(data.extracted_profile || {});
      setQuickSuggestions(data.quick_suggestions || []);
      setIsReady(data.ready_for_recommendation || false);

      const botResponse = {
        id: Date.now() + 1,
        sender: 'bot',
        text: data.message,
        outOfScope: data.out_of_scope,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages((prev) => [...prev, botResponse]);
    } catch (err) {
      console.error('[Samanvay] Chat request failed.', err);
      const errorResponse = {
        id: Date.now() + 1,
        sender: 'bot',
        text: '⚠️ Unable to connect to the Maharashtra regulatory server. Please check your network or try again in a moment.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages((prev) => [...prev, errorResponse]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleGenerateApprovals = async () => {
    setIsTyping(true);
    try {
      const result = await recommendApprovals(currentProfile);
      setRecommendations(result);
      
      const botResponse = {
        id: Date.now() + 1,
        sender: 'bot',
        isStructuredResult: true,
        data: result,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages((prev) => [...prev, botResponse]);
      setIsReady(false);
    } catch (err) {
      console.error('Error generating approvals:', err);
    } finally {
      setIsTyping(false);
    }
  };

  const handleReset = () => {
    setSessionId('sess-' + Math.random().toString(36).substring(2, 9));
    setMessages([]);
    setInputValue('');
    setCurrentProfile({});
    setQuickSuggestions([]);
    setIsReady(false);
    setRecommendations(null);
  };

  const formatText = (content) => {
    const lines = content.split('\n');
    return lines.map((line, i) => {
      const formattedLine = line.split(/(\*\*.*?\*\*)/g).map((chunk, j) => {
        if (chunk.startsWith('**') && chunk.endsWith('**')) {
          return <strong key={j}>{chunk.slice(2, -2)}</strong>;
        }
        return chunk;
      });

      return (
        <span key={i}>
          {formattedLine}
          {i < lines.length - 1 && <br />}
        </span>
      );
    });
  };

  const hasProfileData = currentProfile.industry || currentProfile.district || currentProfile.investment_inr;

  return (
    <div className={styles.chatContainer}>
      <div className={styles.chatHeader}>
        <div className={styles.headerLeft}>
          <div className={styles.botAvatar}>
            <Bot size={20} />
          </div>
          <div>
            <div className={styles.headerTitle}>Samanvay Assistant</div>
            <div className={styles.headerSubtitle}>
              <span className={styles.statusDot}></span>
              <span>Maharashtra Regulatory Advisor • Online</span>
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button
            onClick={handleReset}
            title="Reset conversation & profile"
            style={{
              background: 'transparent',
              border: 'none',
              color: '#93c5fd',
              padding: '4px',
              display: 'flex',
              alignItems: 'center',
              cursor: 'pointer',
              borderRadius: '4px'
            }}
          >
            <RefreshCw size={15} />
          </button>
          <span className={styles.headerBadge}>Deterministic Engine</span>
        </div>
      </div>

      {hasProfileData && (
        <div className={styles.profileStrip}>
          <span className={styles.profileStripLabel}>
            <Building size={13} /> Active Profile:
          </span>
          {currentProfile.industry && (
            <span className={`${styles.profilePill} ${styles.profilePillActive}`}>
              {currentProfile.industry}
            </span>
          )}
          {currentProfile.district && (
            <span className={styles.profilePill}>
              <MapPin size={11} /> {currentProfile.district}
            </span>
          )}
          {currentProfile.investment_display && (
            <span className={styles.profilePill}>
              <IndianRupee size={11} /> {currentProfile.investment_display}
            </span>
          )}
          {currentProfile.employee_count && (
            <span className={styles.profilePill}>
              <Users size={11} /> {currentProfile.employee_count} workers
            </span>
          )}
        </div>
      )}

      <div className={styles.messageArea}>
        {messages.length === 0 ? (
          <div className={styles.emptyState}>
            <div className={styles.emptyStateIcon}>
              <Bot size={28} />
            </div>
            <h3 className={styles.emptyStateTitle}>Welcome to Samanvay (समन्वय)</h3>
            <p className={styles.emptyStateDesc}>
              Ask any question about starting an industry in Maharashtra, or describe your project (e.g. industry sector, district, investment amount) to calculate required approvals.
            </p>

            <div className={styles.quickQuestionsTitle}>Suggested Scenarios:</div>
            <div className={styles.quickQuestionsList}>
              {STARTER_PROMPTS.map((prompt, idx) => (
                <button
                  key={idx}
                  className={styles.quickQuestionBtn}
                  onClick={() => handleSendMessage(prompt)}
                >
                  <span>{prompt}</span>
                  <ArrowRight size={14} color="#64748b" style={{ flexShrink: 0, marginLeft: '8px' }} />
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`${styles.messageRow} ${msg.sender === 'user' ? styles.userRow : styles.botRow}`}
              >
                <div className={`
                  ${styles.messageBubble} 
                  ${msg.sender === 'user' ? styles.userBubble : styles.botBubble}
                  ${msg.outOfScope ? styles.scopeAlertBubble : ''}
                `}>
                  {msg.isStructuredResult ? (
                    <div>
                      <h4 style={{ color: '#0e3768', marginBottom: '8px', fontSize: '15px' }}>
                        📋 Statutory Approvals & Clearance Assessment
                      </h4>
                      <p style={{ fontSize: '13px', color: '#475569', marginBottom: '12px' }}>
                        Calculated by deterministic rules engine for <strong>{msg.data.business_profile.industry}</strong> in <strong>{msg.data.business_profile.district}</strong>:
                      </p>
                      {msg.data.explanation && <p style={{ whiteSpace: 'pre-wrap', marginBottom: '12px' }}>{msg.data.explanation}</p>}

                      {msg.data.approvals.map((app, i) => (
                        <div key={i} className={styles.approvalCard}>
                          <div className={styles.approvalName}>
                            {app.name} <span style={{ fontSize: '11px', color: '#16a34a' }}>({app.applicability})</span>
                            {app.is_potentially_outdated && (
                              <span className={styles.outdatedWarning}> ⚠️ Last verified &gt;180 days ago</span>
                            )}
                          </div>
                          <div className={styles.approvalMeta}>
                            <div><strong>Department:</strong> {app.department_name}</div>
                            <div><strong>Why Applicable:</strong> {app.why_applicable}</div>
                            {app.fee_info && <div><strong>Fee:</strong> {app.fee_info}</div>}
                            {app.processing_time && <div><strong>Timeline:</strong> {app.processing_time}</div>}
                            <div className={styles.sourceBadge}>
                              <span>Source: {app.official_source} (Verified: {app.last_verified})</span>
                            </div>
                          </div>
                        </div>
                      ))}

                      <div style={{ marginTop: '16px' }}>
                        <strong style={{ fontSize: '13px', color: '#0e3768' }}>📁 Required Documents Checklist:</strong>
                        <ul style={{ paddingLeft: '20px', marginTop: '6px', fontSize: '12px', color: '#334155' }}>
                          {msg.data.document_checklist.missing_required.map((doc, idx) => (
                            <li key={idx}>⚠ {doc}</li>
                          ))}
                        </ul>
                      </div>

                      <div style={{ marginTop: '14px' }}>
                        <strong style={{ fontSize: '13px', color: '#0e3768' }}>🚀 Immediate Next Steps:</strong>
                        <ul style={{ paddingLeft: '20px', marginTop: '6px', fontSize: '12px', color: '#334155' }}>
                          {msg.data.next_steps.map((step, idx) => (
                            <li key={idx}>{step}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  ) : (
                    <div>{formatText(msg.text)}</div>
                  )}

                  {msg.sender === 'bot' && isReady && (
                    <div className={styles.readyBanner}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', color: '#166534', fontWeight: '600' }}>
                        <CheckCircle2 size={16} color="#16a34a" />
                        <span>Profile Complete • Deterministic rules ready</span>
                      </div>
                      <button
                        className={styles.readyBtn}
                        onClick={handleGenerateApprovals}
                      >
                        Calculate Clearances <ArrowRight size={14} />
                      </button>
                    </div>
                  )}

                  <div className={styles.messageTime}>{msg.timestamp}</div>
                </div>
              </div>
            ))}
            {isTyping && (
              <div className={`${styles.messageRow} ${styles.botRow}`}>
                <div className={`${styles.messageBubble} ${styles.botBubble}`} style={{ color: '#64748b', fontStyle: 'italic', fontSize: '13px' }}>
                  Evaluating Maharashtra regulatory rules and statutory databases...
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {quickSuggestions.length > 0 && !isTyping && (
        <div className={styles.suggestionsRow}>
          {quickSuggestions.map((suggestion, idx) => (
            <button
              key={idx}
              className={styles.suggestionChip}
              onClick={() => handleSendMessage(suggestion)}
            >
              {suggestion}
            </button>
          ))}
        </div>
      )}

      <form
        className={styles.inputForm}
        onSubmit={(e) => {
          e.preventDefault();
          handleSendMessage();
        }}
      >
        <div className={styles.inputRow}>
          <input
            type="text"
            className={styles.textInput}
            placeholder="Describe your industry (e.g. Food processing unit in Pune with 2.5 Cr investment)..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
          />
          <button
            type="submit"
            className={styles.sendButton}
            disabled={!inputValue.trim() || isTyping}
          >
            <Send size={18} />
          </button>
        </div>
        <div className={styles.inputFooterNotice}>
          Preliminary regulatory guidance for Maharashtra • Grounded in verified government records
        </div>
      </form>
    </div>
  );
}
