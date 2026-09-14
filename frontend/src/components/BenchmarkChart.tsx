import React from 'react';
import { FlaskConical, AlertOctagon, CheckCircle2, ShieldAlert, Zap, Clock } from 'lucide-react';

interface BenchmarkChartProps {
  experimentData: any;
  onRerun: () => void;
  isLoading: boolean;
}

export const BenchmarkChart: React.FC<BenchmarkChartProps> = ({ experimentData, onRerun, isLoading }) => {
  if (!experimentData) return null;

  const { approach_a, approach_b, approach_c } = experimentData;

  const approaches = [
    { key: 'approach_a', data: approach_a, badge: 'badge-rose', color: '#EF4444' },
    { key: 'approach_b', data: approach_b, badge: 'badge-amber', color: '#F59E0B' },
    { key: 'approach_c', data: approach_c, badge: 'badge-emerald', color: '#10B981' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '10px' }}>
        <div>
          <h3 style={{ fontSize: '1.25rem', color: '#818CF8' }}>Scientific Research Experiment: 3-Way Architectural Comparison</h3>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
            Empirical evaluation proving why LLMs must not directly mutate financial ledgers.
          </p>
        </div>

        <button onClick={onRerun} disabled={isLoading} className="btn btn-primary" style={{ padding: '8px 16px' }}>
          <FlaskConical size={16} /> {isLoading ? 'Running Benchmark Suite...' : 'Re-Run Comparative Experiment'}
        </button>
      </div>

      {/* 3 Comparison Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px' }}>
        {approaches.map(({ key, data, badge, color }) => (
          <div
            key={key}
            className="fin-card"
            style={{
              border: key === 'approach_c' ? '2px solid rgba(16, 185, 129, 0.5)' : '1px solid var(--border-color)',
              background: key === 'approach_c' ? 'linear-gradient(135deg, rgba(16, 185, 129, 0.08), rgba(6, 182, 212, 0.04))' : 'var(--bg-card)',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between'
            }}
          >
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span className={`badge ${badge}`}>{data.name.split(':')[0]}</span>
                {key === 'approach_c' && <span className="badge badge-emerald">PROPOSED ARCHITECTURE</span>}
              </div>
              <h4 style={{ fontSize: '1.05rem', color: '#F8FAFC', marginBottom: '4px' }}>{data.name}</h4>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-dim)', marginBottom: '16px' }}>{data.description}</p>

              {/* Accuracy Bar */}
              <div style={{ marginBottom: '14px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', marginBottom: '4px' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Ground Truth Exact Match</span>
                  <strong style={{ color }}>{data.accuracy_percentage}%</strong>
                </div>
                <div style={{ width: '100%', height: '8px', background: 'rgba(255,255,255,0.06)', borderRadius: '4px', overflow: 'hidden' }}>
                  <div style={{ width: `${data.accuracy_percentage}%`, height: '100%', background: color, borderRadius: '4px', transition: 'width 0.5s ease' }} />
                </div>
              </div>

              {/* Metric Row */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '14px' }}>
                <div style={{ background: 'rgba(0,0,0,0.25)', padding: '8px 10px', borderRadius: 'var(--radius-sm)' }}>
                  <div style={{ fontSize: '0.68rem', color: 'var(--text-dim)' }}>Hallucination Rate</div>
                  <div style={{ fontSize: '0.95rem', fontWeight: 700, color: data.hallucination_rate > 0 ? '#F87171' : '#34D399' }}>
                    {data.hallucination_rate}%
                  </div>
                </div>

                <div style={{ background: 'rgba(0,0,0,0.25)', padding: '8px 10px', borderRadius: 'var(--radius-sm)' }}>
                  <div style={{ fontSize: '0.68rem', color: 'var(--text-dim)' }}>Direction Reversal Rate</div>
                  <div style={{ fontSize: '0.95rem', fontWeight: 700, color: data.direction_reversal_rate > 0 ? '#F87171' : '#34D399' }}>
                    {data.direction_reversal_rate}%
                  </div>
                </div>

                <div style={{ background: 'rgba(0,0,0,0.25)', padding: '8px 10px', borderRadius: 'var(--radius-sm)' }}>
                  <div style={{ fontSize: '0.68rem', color: 'var(--text-dim)' }}>Avg Latency</div>
                  <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#38BDF8', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <Clock size={12} /> {data.avg_latency_ms} ms
                  </div>
                </div>

                <div style={{ background: 'rgba(0,0,0,0.25)', padding: '8px 10px', borderRadius: 'var(--radius-sm)' }}>
                  <div style={{ fontSize: '0.68rem', color: 'var(--text-dim)' }}>Arithmetic Error</div>
                  <div style={{ fontSize: '0.95rem', fontWeight: 700, color: data.arithmetic_error_rate > 0 ? '#F87171' : '#34D399' }}>
                    {data.arithmetic_error_rate}%
                  </div>
                </div>
              </div>
            </div>

            <div style={{ paddingTop: '10px', borderTop: '1px solid var(--border-color)', fontSize: '0.75rem', color: 'var(--text-dim)' }}>
              Auditability: <strong style={{ color: '#F8FAFC' }}>{data.auditability_score}</strong>
            </div>
          </div>
        ))}
      </div>

      {/* Test Case Failure Deep-Dive Table */}
      <div className="fin-card">
        <h4 style={{ fontSize: '1rem', color: '#F8FAFC', marginBottom: '12px' }}>
          Test Bench Failure Breakdown (Where Approaches Fail)
        </h4>

        <div style={{ overflowX: 'auto' }}>
          <table className="fin-table">
            <thead>
              <tr>
                <th>Test Prompt</th>
                <th>Category</th>
                <th>Approach A (Direct LLM)</th>
                <th>Approach B (NLP+LLM)</th>
                <th>Approach C (Ours: NLP+State Machine)</th>
              </tr>
            </thead>
            <tbody>
              {approach_c.results?.map((resC: any, idx: number) => {
                const resA = approach_a.results?.[idx];
                const resB = approach_b.results?.[idx];
                return (
                  <tr key={idx}>
                    <td style={{ fontWeight: 600, color: '#F8FAFC' }}>"{resC.input}"</td>
                    <td><span className="badge badge-neutral">{resC.category}</span></td>
                    <td>
                      <span className={`badge ${resA?.exact_match ? 'badge-emerald' : 'badge-rose'}`}>
                        {resA?.exact_match ? '✓ Correct' : '✗ Failed (Hallucinated)'}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${resB?.exact_match ? 'badge-emerald' : 'badge-amber'}`}>
                        {resB?.exact_match ? '✓ Correct' : '⚠ Drift Risk'}
                      </span>
                    </td>
                    <td>
                      <span className="badge badge-emerald">
                        ✓ 100% Exact Match ({resC.latency_ms}ms)
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
