import React, { useEffect, useRef, useState } from 'react';
import { Bot, CircleHelp, MessageCircle, Minus, Send, X } from 'lucide-react';
import { checkApiHealth, sendWebsiteHelp } from '../../services/api';
import styles from './WebsiteHelpWidget.module.css';

export default function WebsiteHelpWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    checkApiHealth().catch((error) => {
      console.warn('[Samanvay] Backend health check failed on website-help mount.', error);
    });
  }, []);

  useEffect(() => {
    if (isOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      inputRef.current?.focus();
    }
  }, [isOpen, messages, isTyping]);

  const handleSendMessage = async (messageToSend = inputValue) => {
    const text = messageToSend.trim();
    if (!text || isTyping) return;

    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    setMessages((current) => [...current, {
      id: `${Date.now()}-user`, sender: 'user', text, timestamp,
    }]);
    setInputValue('');
    setIsTyping(true);

    try {
      const response = await sendWebsiteHelp(text);
      setMessages((current) => [...current, {
        id: `${Date.now()}-assistant`, sender: 'bot', text: response.message, timestamp,
      }]);
    } catch (error) {
      console.error('[Samanvay] Website help request failed.', error);
      setMessages((current) => [...current, {
        id: `${Date.now()}-error`,
        sender: 'bot',
        text: 'I could not reach the website help service. Please try again in a moment.',
        timestamp,
      }]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className={styles.widget}>
      {isOpen && (
        <section className={styles.panel} aria-label="Website help chat">
          <header className={styles.header}>
            <div className={styles.headerIdentity}>
              <div className={styles.avatar}><Bot size={19} aria-hidden="true" /></div>
              <div>
                <h2 className={styles.title}>Website Assistant</h2>
                <p className={styles.subtitle}>Help using Samanvay</p>
              </div>
            </div>
            <button className={styles.closeButton} type="button" onClick={() => setIsOpen(false)} aria-label="Close website help">
              <Minus size={19} />
            </button>
          </header>

          <div className={styles.messages} role="log" aria-live="polite" aria-relevant="additions text">
            {messages.length === 0 && (
              <div className={styles.welcome}>
                <div className={styles.welcomeIcon}><CircleHelp size={21} /></div>
                <p>Hi! I can help you find your way around the Samanvay website.</p>
                <button type="button" onClick={() => handleSendMessage('How do I register?')}>
                  How do I register?
                </button>
              </div>
            )}
            {messages.map((message) => (
              <div key={message.id} className={`${styles.messageRow} ${message.sender === 'user' ? styles.userRow : styles.assistantRow}`}>
                <div className={`${styles.bubble} ${message.sender === 'user' ? styles.userBubble : styles.assistantBubble}`}>
                  <p>{message.text}</p>
                  <time>{message.timestamp}</time>
                </div>
              </div>
            ))}
            {isTyping && <div className={`${styles.bubble} ${styles.assistantBubble} ${styles.typing}`}>Checking the site guide…</div>}
            <div ref={messagesEndRef} />
          </div>

          <form className={styles.form} onSubmit={(event) => { event.preventDefault(); handleSendMessage(); }}>
            <label className={styles.srOnly} htmlFor="website-help-input">Ask how to use the website</label>
            <input
              id="website-help-input"
              ref={inputRef}
              value={inputValue}
              onChange={(event) => setInputValue(event.target.value)}
              placeholder="Ask about using the site…"
              maxLength={500}
              disabled={isTyping}
            />
            <button type="submit" aria-label="Send message" disabled={!inputValue.trim() || isTyping}>
              <Send size={17} />
            </button>
          </form>
          <p className={styles.footerNote}>For project approvals, use the Setup &amp; Approval Assistant.</p>
        </section>
      )}

      <div className={styles.launcherRow}>
        {!isOpen && <span className={styles.launcherLabel}>Need help using the site?</span>}
        <button
          className={`${styles.launcher} ${isOpen ? styles.launcherOpen : ''}`}
          type="button"
          aria-label={isOpen ? 'Close website help' : 'Open website help'}
          aria-expanded={isOpen}
          onClick={() => setIsOpen((open) => !open)}
        >
          {isOpen ? <X size={21} /> : <MessageCircle size={22} />}
        </button>
      </div>
    </div>
  );
}
