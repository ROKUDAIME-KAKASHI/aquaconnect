import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { 
  LayoutDashboard, 
  Droplets, 
  TrendingUp, 
  MessageSquare, 
  LogOut, 
  User as UserIcon,
  Menu,
  X
} from 'lucide-react';

const Layout = ({ children }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = React.useState(false);

  const navItems = [
    { label: 'Dashboard', icon: <LayoutDashboard size={20} />, path: '/' },
    { label: 'Water Analysis', icon: <Droplets size={20} />, path: '/water' },
    { label: 'Finance', icon: <TrendingUp size={20} />, path: '/finance' },
    { label: 'Forum', icon: <MessageSquare size={20} />, path: '/forum' },
  ];

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="flex min-h-screen">
      {/* Sidebar - Desktop */}
      <aside className="w-64 glass-card m-4 rounded-3xl sticky top-4 h-[calc(100vh-2rem)] hidden lg:flex flex-col p-6">
        <div className="flex items-center gap-3 mb-10 px-2">
          <div className="bg-primary p-2 rounded-xl">
            <Droplets size={24} className="text-white" />
          </div>
          <span className="text-xl font-bold">AquaConnect</span>
        </div>

        <nav className="flex-1 space-y-2">
          {navItems.map((item) => (
            <button
              key={item.label}
              onClick={() => navigate(item.path)}
              className="flex items-center gap-3 w-full px-4 py-3 rounded-xl hover:bg-white/10 transition-colors text-dim hover:text-white"
            >
              {item.icon}
              <span className="font-medium">{item.label}</span>
            </button>
          ))}
        </nav>

        <div className="mt-auto space-y-4">
          <div className="flex items-center gap-3 px-4 py-3 bg-white/5 rounded-2xl border border-white/5">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-white font-bold">
              {user?.full_name?.charAt(0)}
            </div>
            <div className="overflow-hidden">
              <p className="font-semibold truncate">{user?.full_name}</p>
              <p className="text-xs text-dim truncate capitalize">{user?.role}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 w-full px-4 py-3 rounded-xl text-accent hover:bg-accent/10 transition-colors"
          >
            <LogOut size={20} />
            <span className="font-medium">Sign Out</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-4 lg:p-8">
        <header className="flex justify-between items-center mb-8 lg:hidden">
            <div className="flex items-center gap-3">
              <div className="bg-primary p-2 rounded-xl">
                <Droplets size={20} className="text-white" />
              </div>
              <span className="text-xl font-bold">AquaConnect</span>
            </div>
            <button 
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="p-2 glass-card rounded-xl"
            >
              {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
        </header>
        {children}
      </main>

      {/* Mobile Menu Overlay */}
      {isMobileMenuOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setIsMobileMenuOpen(false)} />
          <nav className="absolute right-0 top-0 bottom-0 w-64 bg-slate-900 p-8 shadow-2xl animate-fade">
            <div className="space-y-6">
               {navItems.map((item) => (
                <button
                  key={item.label}
                  onClick={() => {
                    navigate(item.path);
                    setIsMobileMenuOpen(false);
                  }}
                  className="flex items-center gap-4 w-full text-lg"
                >
                  {item.icon}
                  {item.label}
                </button>
              ))}
              <hr className="border-white/10" />
              <button 
                onClick={handleLogout}
                className="flex items-center gap-4 w-full text-accent"
              >
                <LogOut size={20} />
                Sign Out
              </button>
            </div>
          </nav>
        </div>
      )}
    </div>
  );
};

export default Layout;
