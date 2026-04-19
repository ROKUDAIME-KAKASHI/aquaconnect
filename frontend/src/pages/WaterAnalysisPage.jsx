import React, { useState } from 'react';
import { waterService } from '../services/api';
import { Beaker, AlertTriangle, CheckCircle, Info } from 'lucide-react';

const WaterAnalysisPage = () => {
  const [formData, setFormData] = useState({
    farm_id: '',
    ph: 7.0,
    temperature: 25.0,
    dissolved_oxygen: 6.0,
    ammonia: 0.1,
    salinity: 0.0
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await waterService.analyze(formData);
      setResult(res.data);
    } catch (err) {
      alert('Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'good': return 'text-secondary bg-secondary/10 border-secondary/20';
      case 'warning': return 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20';
      case 'critical': return 'text-accent bg-accent/10 border-accent/20';
      default: return 'text-dim';
    }
  };

  return (
    <div className="animate-fade max-w-5xl mx-auto">
      <div className="mb-10 text-center">
        <h1 className="text-4xl font-bold italic">AI Water Expert</h1>
        <p className="text-dim mt-2">Get instant health analysis for your ponds</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
        {/* Form Section */}
        <section className="glass-card p-8">
          <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
            <Beaker className="text-primary" />
            Input Parameters
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
             <div className="flex flex-col gap-1">
              <label className="text-sm text-dim">Farm ID (Temporary)</label>
              <input 
                type="number" 
                className="input-glass" 
                value={formData.farm_id}
                onChange={(e) => setFormData({...formData, farm_id: e.target.value})}
                required
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="flex flex-col gap-1">
                <label className="text-sm text-dim">pH Level</label>
                <input 
                  type="number" step="0.1" className="input-glass" 
                  value={formData.ph}
                  onChange={(e) => setFormData({...formData, ph: e.target.value})}
                />
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-sm text-dim">Temp (°C)</label>
                <input 
                  type="number" step="0.5" className="input-glass" 
                  value={formData.temperature}
                  onChange={(e) => setFormData({...formData, temperature: e.target.value})}
                />
              </div>
            </div>

            <div className="flex flex-col gap-1">
              <label className="text-sm text-dim">Dissolved Oxygen (mg/L)</label>
              <input 
                type="number" step="0.1" className="input-glass" 
                value={formData.dissolved_oxygen}
                onChange={(e) => setFormData({...formData, dissolved_oxygen: e.target.value})}
              />
            </div>

            <button type="submit" disabled={loading} className="btn-primary w-full py-4 text-lg mt-6">
              {loading ? 'Analyzing...' : 'Run Diagnostics'}
            </button>
          </form>
        </section>

        {/* Results Section */}
        <section className="flex flex-col gap-6">
          {!result ? (
            <div className="glass-card p-12 flex flex-col items-center justify-center text-center h-full">
              <Info size={48} className="text-dim mb-4" />
              <p className="text-dim">Enter parameters and run analysis to see results here.</p>
            </div>
          ) : (
            <>
              <div className={`glass-card p-6 border-l-4 ${getStatusColor(result.health_status)}`}>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-2xl font-bold capitalize">Status: {result.health_status}</h3>
                  {result.health_status === 'good' ? <CheckCircle /> : <AlertTriangle />}
                </div>
                <p className="text-3xl font-black">Score: {result.risk_score}/100</p>
              </div>

              <div className="glass-card p-6">
                <h3 className="font-bold mb-4">Urgent Alerts</h3>
                <div className="space-y-2">
                  {result.alerts.map((a, i) => (
                    <div key={i} className="flex gap-2 text-sm text-accent bg-accent/5 p-2 rounded-lg">
                      <span>•</span> {a}
                    </div>
                  ))}
                  {result.alerts.length === 0 && <p className="text-secondary">No urgent alerts.</p>}
                </div>
              </div>

              <div className="glass-card p-6">
                <h3 className="font-bold mb-4">Expert Recommendations</h3>
                <div className="space-y-3">
                  {result.recommendations.map((r, i) => (
                    <div key={i} className="flex gap-3 text-sm">
                      <div className="mt-1 bullet w-1.5 h-1.5 rounded-full bg-primary" />
                      {r}
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </section>
      </div>
    </div>
  );
};

export default WaterAnalysisPage;
