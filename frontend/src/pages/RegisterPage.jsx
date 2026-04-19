import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { authService } from '../services/api'; // Import specifically for registration
import { UserPlus, Droplets, Fish, CheckCircle2, ShieldCheck, TrendingUp } from 'lucide-react';

const RegisterPage = () => {
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    password: '',
    role: 'farmer',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // 1. Register the user
      await authService.register(formData);
      
      // 2. Automatically log them in
      await login({ email: formData.email, password: formData.password });
      
      // 3. Redirect to dashboard
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.error || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 lg:p-8">
      <div className="w-full max-w-6xl grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
        
        {/* Left Side: Promo Content */}
        <div className="hidden lg:flex flex-col gap-8 p-8 animate-fade">
          <div className="flex items-center gap-3">
             <div className="bg-primary p-3 rounded-2xl shadow-lg shadow-primary-glow">
              <Droplets className="text-white w-8 h-8" />
            </div>
            <span className="text-3xl font-extrabold tracking-tight">AquaConnect</span>
          </div>

          <div className="space-y-6">
            <h1 className="text-5xl font-black leading-tight bg-gradient-to-br from-white to-slate-400 bg-clip-text text-transparent">
              Elevate Your <br />
              Aquaculture Business
            </h1>
            <p className="text-xl text-dim leading-relaxed max-w-lg">
              Join the future of fish farming. Use AI to monitor water health, 
              track your finances, and connect with global experts.
            </p>
          </div>

          <div className="grid gap-6">
            {[
              { icon: <CheckCircle2 className="text-secondary" />, text: "Free to get started – no credit card required" },
              { icon: <ShieldCheck className="text-primary" />, text: "AI-powered insights to prevent fish loss" },
              { icon: <TrendingUp className="text-accent" />, text: "Track profitability and forecast revenue" }
            ].map((feature, i) => (
              <div key={i} className="flex items-center gap-4 group">
                <div className="p-2 rounded-lg bg-white/5 border border-white/5 group-hover:border-white/20 transition-colors">
                  {feature.icon}
                </div>
                <span className="text-lg font-medium text-slate-300">{feature.text}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Right Side: Registration Form */}
        <div className="glass-card p-8 lg:p-12 animate-fade w-full max-w-md mx-auto">
          <div className="mb-10 text-center lg:text-left">
            <h2 className="text-3xl font-bold mb-2">Create Account</h2>
            <p className="text-dim">Start managing your farm smarter today</p>
          </div>

          {error && (
            <div className="bg-accent/20 border border-accent/50 text-accent p-4 rounded-xl mb-8 text-sm flex items-center gap-3">
              <div className="shrink-0 w-1.5 h-1.5 rounded-full bg-accent" />
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-2">
              <label className="text-sm font-semibold text-dim px-1 text-dim">Full Name</label>
              <input
                type="text"
                value={formData.full_name}
                onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                className="input-glass w-full"
                placeholder="John Doe"
                required
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-semibold text-dim px-1">Email Address</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                className="input-glass w-full"
                placeholder="farmer@example.com"
                required
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-semibold text-dim px-1">Password</label>
              <input
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({...formData, password: e.target.value})}
                className="input-glass w-full"
                placeholder="Min. 6 characters"
                required
                minLength="6"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-semibold text-dim px-1">Account Type</label>
              <select
                value={formData.role}
                onChange={(e) => setFormData({...formData, role: e.target.value})}
                className="input-glass w-full appearance-none cursor-pointer"
              >
                <option value="farmer">🐠 Fish Farmer</option>
                <option value="expert">🎓 Aquaculture Expert</option>
              </select>
              <p className="text-[10px] text-dim px-1 mt-1">
                Experts can provide verified answers in the community forum.
              </p>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full py-4 flex items-center justify-center gap-3 text-lg mt-4"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-white" />
              ) : (
                <>
                  <UserPlus size={20} />
                  Create Free Account
                </>
              )}
            </button>
          </form>

          <div className="mt-8 text-center text-sm text-dim">
            Already have an account?{' '}
            <a href="/login" className="text-primary font-bold hover:underline transition-colors">
              Sign In
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
