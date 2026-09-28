import React, { useEffect } from 'react';
import ChatWidget from '../components/chat/ChatWidget';

export default function EmbedPage() {
  useEffect(() => {
    const notifyParent = () => {
      if (window.parent && window.parent !== window) {
        window.parent.postMessage(
          {
            type: 'SAMANVAY_EMBED_RESIZE',
            height: document.body.scrollHeight
          },
          '*'
        );
      }
    };
    window.addEventListener('resize', notifyParent);
    notifyParent();
    return () => window.removeEventListener('resize', notifyParent);
  }, []);

  return (
    <div style={{
      width: '100vw',
      height: '100vh',
      margin: 0,
      padding: '8px',
      display: 'flex',
      flexDirection: 'column',
      boxSizing: 'border-box',
      backgroundColor: 'transparent'
    }}>
      <ChatWidget compact={true} />
    </div>
  );
}
