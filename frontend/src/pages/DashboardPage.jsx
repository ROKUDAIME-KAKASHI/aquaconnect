import React, { useState, useEffect } from 'react';
import { farmService } from '../services/api';
import { Plus, MapPin, Fish, Ruler } from 'lucide-react';

const DashboardPage = () => {
  const [farms, setFarms] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchFarms = async () => {
      try {
        const res = await farmService.getFarms();
        setFarms(res.data);
      } catch (err) {
        console.error('Failed to fetch farms');
      } finally {
        setLoading(false);
      }
    };
    fetchFarms();
  }, []);

  return (
    <div className="animate-fade">
      <div className="flex justify-between items-center mb-10">
        <div>
          <h1 className="text-4xl font-bold">My Farms</h1>
          <p className="text-dim mt-2">Manage your aquaculture operations</p>
        </div>
        <button className="btn-primary flex items-center gap-2">
          <Plus size={20} />
          <span>New Farm</span>
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center py-20">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-primary" />
        </div>
      ) : farms.length === 0 ? (
        <div className="glass-card p-20 text-center">
          <Fish size={64} className="mx-auto text-dim mb-6" />
          <h2 className="text-2xl font-bold">No farms found</h2>
          <p className="text-dim mt-2 mb-8">Start by adding your first aquaculture farm</p>
          <button className="btn-primary">Add a Farm</button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {farms.map((farm) => (
            <div key={farm.id} className="glass-card p-6 flex flex-col group">
              <div className="aspect-video rounded-2xl bg-gradient-to-br from-primary/20 to-secondary/20 mb-6 relative overflow-hidden">
                <div className="absolute inset-0 flex items-center justify-center opacity-40">
                  <Fish size={80} className="group-hover:scale-110 transition-transform" />
                </div>
              </div>
              
              <h3 className="text-2xl font-bold mb-4">{farm.name}</h3>
              
              <div className="space-y-3 mb-8">
                <div className="flex items-center gap-2 text-dim">
                  <MapPin size={16} />
                  <span>{farm.location}</span>
                </div>
                <div className="flex items-center gap-2 text-dim">
                  <Ruler size={16} />
                  <span>{farm.area_hectares} Hectares</span>
                </div>
                <div className="flex items-center gap-2 text-dim">
                  <Fish size={16} />
                  <span>{farm.fish_species}</span>
                </div>
              </div>

              <button className="mt-auto py-3 rounded-xl border border-white/10 hover:bg-white/5 transition-colors font-medium">
                View Details
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default DashboardPage;
