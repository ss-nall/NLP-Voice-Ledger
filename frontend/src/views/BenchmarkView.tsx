import React, { useState, useEffect } from 'react';
import { FlaskConical, Play, CheckCircle } from 'lucide-react';
import { api } from '../api/client';
import { BenchmarkChart } from '../components/BenchmarkChart';

export const BenchmarkView: React.FC = () => {
  const [experimentData, setExperimentData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadExperiment();
  }, []);

  const loadExperiment = async () => {
    try {
      setLoading(true);
      const data = await api.runExperiment();
      setExperimentData(data);
    } catch (err) {
      console.error('Failed to run experiment', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {loading && !experimentData ? (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '400px', color: 'var(--text-muted)' }}>
          Executing Scientific Benchmark Comparison (Approaches A vs B vs C)...
        </div>
      ) : (
        <BenchmarkChart
          experimentData={experimentData}
          onRerun={loadExperiment}
          isLoading={loading}
        />
      )}
    </div>
  );
};
