import React, { useState, useEffect } from 'react';
import { FileText, Search, Sparkles, Plus, BookOpen } from 'lucide-react';
import { api } from '../api/client';

export const DocumentsView: React.FC = () => {
  const [documents, setDocuments] = useState<any[]>([]);
  const [ragQuery, setRagQuery] = useState('');
  const [ragResult, setRagResult] = useState<any>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      const data = await api.getDocuments();
      setDocuments(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleRAGSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ragQuery.trim()) return;
    try {
      setIsSearching(true);
      const res = await api.queryRAG(ragQuery);
      setRagResult(res);
    } catch (err: any) {
      alert("RAG Query error: " + err.message);
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div>
        <h3 style={{ fontSize: '1.25rem', color: '#F8FAFC' }}>Document Intelligence & Hybrid RAG</h3>
        <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
          Retrieval-Augmented Generation for store policies, credit rules, and tax invoices. Financial arithmetic remains deterministic in SQL.
        </p>
      </div>

      {/* RAG Query Bar */}
      <div className="fin-card" style={{ background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.08), rgba(6, 182, 212, 0.04))', border: '1px solid rgba(99, 102, 241, 0.3)' }}>
        <h4 style={{ fontSize: '1rem', color: '#818CF8', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Sparkles size={16} /> Ask Questions About Store Policies & Invoices
        </h4>
        
        <form onSubmit={handleRAGSearch} style={{ display: 'flex', gap: '10px' }}>
          <input
            type="text"
            value={ragQuery}
            onChange={(e) => setRagQuery(e.target.value)}
            placeholder="e.g., 'What is our store credit policy for overdue payments?' or 'Invoice INV-2026-089 details'..."
            style={{
              flex: 1,
              background: 'var(--bg-card)',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-md)',
              padding: '10px 14px',
              color: '#F8FAFC',
              fontSize: '0.88rem',
              outline: 'none'
            }}
          />
          <button type="submit" disabled={isSearching || !ragQuery.trim()} className="btn btn-primary">
            <Search size={16} /> {isSearching ? 'Searching...' : 'RAG Query'}
          </button>
        </form>

        {/* RAG Answer Display */}
        {ragResult && (
          <div style={{ marginTop: '16px', padding: '14px', background: '#090D16', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '4px' }}>
              Synthesized Answer with Grounded Source Citations
            </div>
            <div style={{ fontSize: '0.9rem', color: '#F8FAFC', whiteSpace: 'pre-wrap', lineHeight: 1.6 }}>
              {ragResult.answer}
            </div>

            {ragResult.sources?.length > 0 && (
              <div style={{ marginTop: '10px', paddingTop: '8px', borderTop: '1px solid var(--border-color)', display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>Retrieved Document Citations:</span>
                {ragResult.sources.map((s: any, idx: number) => (
                  <span key={idx} className="badge badge-indigo">
                    {s.title} ({s.doc_type})
                  </span>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Uploaded Unstructured Documents List */}
      <div>
        <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '12px' }}>
          Indexed Business Documents ({documents.length})
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '16px' }}>
          {documents.map((d) => (
            <div key={d.id} className="fin-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <BookOpen size={16} color="#38BDF8" />
                  <h4 style={{ fontSize: '0.95rem', color: '#F8FAFC' }}>{d.title}</h4>
                </div>
                <span className="badge badge-neutral">{d.doc_type}</span>
              </div>

              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', whiteSpace: 'pre-wrap', maxHeight: '140px', overflowY: 'auto', background: 'rgba(0,0,0,0.2)', padding: '10px', borderRadius: 'var(--radius-sm)' }}>
                {d.content.trim()}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
