import React, { useState } from 'react';
import { Send, Copy, Check, X, Smartphone, QrCode } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

interface ReminderModalProps {
  isOpen: boolean;
  onClose: () => void;
  reminderData: any;
}

export const ReminderModal: React.FC<ReminderModalProps> = ({ isOpen, onClose, reminderData }) => {
  const { t, language } = useLanguage();
  const [selectedTab, setSelectedTab] = useState<'vernacular' | 'english'>('vernacular');
  const [showQr, setShowQr] = useState(true);
  const [copied, setCopied] = useState(false);

  if (!isOpen || !reminderData) return null;

  const amount = Number(reminderData.amount || 0);
  const upiUrl = `upi://pay?pa=merchant@upi&pn=Khata&am=${amount}&cu=INR`;
  const qrCodeUrl = `https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=${encodeURIComponent(upiUrl)}`;

  const getVernacularText = () => {
    if (language === 'te') return reminderData.templates?.telugu_script || reminderData.templates?.romanized_telugu || '';
    if (language === 'ta') return reminderData.templates?.tamil_script || reminderData.templates?.romanized_tamil || '';
    if (language === 'hi') return reminderData.templates?.hindi_script || reminderData.templates?.romanized_hindi || '';
    if (language === 'kn') return `ನಮಸ್ಕಾರ ${reminderData.customer_name || reminderData.entity_name || ''} ರವರೇ,\nನಿಮ್ಮ ವ್ಯಾಪಾರ ಖಾತೆಯ ಪ್ರಕಾರ ₹${amount.toLocaleString()} ಬಾಕಿ ಮೊತ್ತ ಪಾವತಿಸಬೇಕಾಗಿದೆ. ದಯವಿಟ್ಟು ಪಾವತಿಸಿ ಸಹಕರಿಸಿ. ಧನ್ಯವಾದಗಳು!`;
    if (language === 'ml') return `നമസ്കാരം ${reminderData.customer_name || reminderData.entity_name || ''},\nനിങ്ങളുടെ വ്യാപാര കണക്ക് പ്രകാരം ₹${amount.toLocaleString()} നൽകാനുള്ള തീയതി ആയിരിക്കുന്നു. ദയവായി അടയ്ക്കുക. നന്ദി!`;
    if (language === 'ur') return `محترم ${reminderData.customer_name || reminderData.entity_name || ''} صاحب،\nآپ کے کاروباری کھاتے کے مطابق ₹${amount.toLocaleString()} کی واجب الادا رقم ادا فرمائیں۔ شکریہ!`;
    if (language === 'gu') return `નમસ્તે ${reminderData.customer_name || reminderData.entity_name || ''} ભાઈ,\nતમારા ખાતા મુજબ ₹${amount.toLocaleString()} ચૂકવવાના બાકી છે. કૃપા કરીને સમયસર ચૂકવણી કરો. આભાર!`;
    return reminderData.templates?.english || '';
  };

  const currentTemplate = selectedTab === 'english'
    ? (reminderData.templates?.english || '')
    : (getVernacularText() || reminderData.templates?.romanized_telugu || reminderData.templates?.english || '');

  const handleCopy = () => {
    navigator.clipboard.writeText(currentTemplate);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSendWhatsApp = () => {
    window.open(reminderData.whatsapp_url, '_blank');
  };

  const getLanguageTabLabel = () => {
    if (language === 'te') return 'తెలుగు (Telugu)';
    if (language === 'ta') return 'தமிழ் (Tamil)';
    if (language === 'hi') return 'हिन्दी (Hindi)';
    if (language === 'kn') return 'ಕನ್ನಡ (Kannada)';
    if (language === 'ml') return 'മലയാളം (Malayalam)';
    if (language === 'ur') return 'اردو (Urdu)';
    if (language === 'gu') return 'ગુજરાતી (Gujarati)';
    return 'Primary Language';
  };

  return (
    <div className="modal-backdrop">
      <div className="modal-card" style={{ maxWidth: '520px' }}>
        {/* Header */}
        <div style={{ padding: '16px 20px', background: 'rgba(16, 185, 129, 0.15)', borderBottom: '1px solid rgba(16, 185, 129, 0.3)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: '#10B981', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff' }}>
              <Smartphone size={18} />
            </div>
            <div>
              <h3 style={{ fontSize: '1.05rem', color: '#34D399', margin: 0 }}>{t('modal.reminder_title', 'Send Due Date Payment Notice')}</h3>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: 0 }}>{reminderData.customer_name || reminderData.entity_name} (₹{amount.toLocaleString()})</p>
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
              onClick={() => setSelectedTab('vernacular')}
              style={{
                flex: 1,
                padding: '6px 10px',
                borderRadius: 'var(--radius-sm)',
                border: 'none',
                background: selectedTab === 'vernacular' ? '#10B981' : 'transparent',
                color: selectedTab === 'vernacular' ? '#fff' : 'var(--text-muted)',
                fontWeight: 600,
                fontSize: '0.78rem',
                cursor: 'pointer'
              }}
            >
              {getLanguageTabLabel()}
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

          {/* Dynamic UPI QR Code Box */}
          <div style={{
            background: 'var(--bg-card-subtle)',
            border: '1px solid rgba(16, 185, 129, 0.3)',
            borderRadius: '12px',
            padding: '12px 16px',
            marginBottom: '16px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '16px'
          }}>
            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#10B981', fontWeight: 700, fontSize: '0.88rem' }}>
                <QrCode size={16} /> Instant UPI QR Settle
              </div>
              <p style={{ fontSize: '0.76rem', color: 'var(--text-muted)', margin: '4px 0 0 0', lineHeight: 1.4 }}>
                Customer can scan with PhonePe, GPay or Paytm to settle <strong>₹{amount.toLocaleString()}</strong> directly.
              </p>
            </div>
            {showQr && (
              <img
                src={qrCodeUrl}
                alt="UPI QR Code"
                style={{ width: '80px', height: '80px', borderRadius: '8px', border: '2px solid #fff', background: '#fff' }}
              />
            )}
          </div>

          {/* Message Text Preview */}
          <div style={{ background: 'var(--bg-card-subtle)', padding: '14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', marginBottom: '16px', minHeight: '110px', whiteSpace: 'pre-wrap', fontSize: '0.88rem', color: 'var(--text-main)', lineHeight: 1.6 }}>
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
