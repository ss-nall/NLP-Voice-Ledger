import React, { useState } from 'react';
import { MessageSquare, Send, Copy, Check, X, Smartphone } from 'lucide-react';

interface ReminderModalProps {
  isOpen: boolean;
  onClose: () => void;
  reminderData: any;
}

export const ReminderModal: React.FC<ReminderModalProps> = ({ isOpen, onClose, reminderData }) => {
  const [selectedTab, setSelectedTab] = useState<'telugu_script' | 'romanized_telugu' | 'english'>('romanized_telugu');
  const [copied, setCopied] = useState(false);

  if (!isOpen || !reminderData) return null;

  const currentTemplate = reminderData.templates?.[selectedTab] || '';

  const handleCopy = () => {
    navigator.clipboard.writeText(currentTemplate);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSendWhatsApp = () => {
    window.open(reminderData.whatsapp_url, '_blank');
  };

  return (
    <div className="modal-backdrop">
      <div className="modal-card">
        {/* Header */}
        <div style={{ padding: '16px 20px', background: 'rgba(16, 185, 129, 0.15)', borderBottom: '1px solid rgba(16, 185, 129, 0.3)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: '#10B981', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff' }}>
              <Smartphone size={18} />
            </div>
            <div>
              <h3 style={{ fontSize: '1.05rem', color: '#34D399' }}>Bilingual Payment Reminder</h3>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Auto-Generated for {reminderData.customer_name} (₹{Number(reminderData.amount).toLocaleString()})</p>
            </div>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--text-dim)', cursor: 'pointer' }}>
            <X size={20} />
          </button>
        </div>

        {/* Body */}
        <div style={{ padding: '20px' }}>
          {/* Language Selection Tabs */}
          <div style={{ display: 'flex', gap: '6px', marginBottom: '14px', background: 'var(--bg-card-subtle)', padding: '4px', borderRadius: 'var(--radius-md)' }}>
            <button
              onClick={() => setSelectedTab('romanized_telugu')}
              style={{
                flex: 1,
                padding: '6px 10px',
                borderRadius: 'var(--radius-sm)',
                border: 'none',
                background: selectedTab === 'romanized_telugu' ? '#10B981' : 'transparent',
                color: selectedTab === 'romanized_telugu' ? '#fff' : 'var(--text-muted)',
                fontWeight: 600,
                fontSize: '0.78rem',
                cursor: 'pointer'
              }}
            >
              Romanized Telugu
            </button>

            <button
              onClick={() => setSelectedTab('telugu_script')}
              style={{
                flex: 1,
                padding: '6px 10px',
                borderRadius: 'var(--radius-sm)',
                border: 'none',
                background: selectedTab === 'telugu_script' ? '#10B981' : 'transparent',
                color: selectedTab === 'telugu_script' ? '#fff' : 'var(--text-muted)',
                fontWeight: 600,
                fontSize: '0.78rem',
                cursor: 'pointer'
              }}
            >
              తెలుగు లిపి (Telugu Script)
            </button>

            <button
              onClick={() => setSelectedTab('english')}
              style={{
                flex: 1,
                padding: '6px 10px',
                borderRadius: 'var(--radius-sm)',
                border: 'none',
                background: selectedTab === 'english' ? '#10B981' : 'transparent',
                color: selectedTab === 'english' ? '#fff' : 'var(--text-muted)',
                fontWeight: 600,
                fontSize: '0.78rem',
                cursor: 'pointer'
              }}
            >
              English
            </button>
          </div>

          {/* Message Text Preview */}
          <div style={{ background: 'var(--bg-card-subtle)', padding: '14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', marginBottom: '16px', minHeight: '120px', whiteSpace: 'pre-wrap', fontSize: '0.88rem', color: 'var(--text-main)', lineHeight: 1.6 }}>
            {currentTemplate}
          </div>

          {/* Action Buttons */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
            <button onClick={handleCopy} className="btn btn-secondary" style={{ width: '100%' }}>
              {copied ? <Check size={16} color="#10B981" /> : <Copy size={16} />} {copied ? 'Copied!' : 'Copy Text'}
            </button>

            <button onClick={handleSendWhatsApp} className="btn btn-emerald" style={{ width: '100%' }}>
              <Send size={16} /> Open in WhatsApp
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
