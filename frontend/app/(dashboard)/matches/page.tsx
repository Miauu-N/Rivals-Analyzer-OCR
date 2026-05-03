"use client";
import { useEffect, useState } from "react";

export default function MatchesPage() {
  const [matches, setMatches] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMatches = async () => {
      try {
        const token = localStorage.getItem("token");
        const res = await fetch("http://localhost:8000/api/matches/", {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          setMatches(data);
        }
      } catch (err) {
        console.error("Error fetching matches", err);
      } finally {
        setLoading(false);
      }
    };
    fetchMatches();
  }, []);

  const handleClearHistory = async () => {
    if (!confirm("¿Estás seguro de que quieres borrar todo el historial? Esta acción no se puede deshacer.")) return;
    
    try {
      const token = localStorage.getItem("token");
      const res = await fetch("http://localhost:8000/api/matches/clear", {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        setMatches([]);
        alert("Historial limpiado correctamente.");
      }
    } catch (err) {
      console.error("Error clearing history", err);
      alert("Hubo un error al limpiar el historial.");
    }
  };

  if (loading) return <div className="text-center p-12 text-gray-400">Cargando historial...</div>;

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-4xl font-bold">Historial de Partidas</h1>
        {matches.length > 0 && (
          <button 
            onClick={handleClearHistory}
            className="px-4 py-2 bg-red-600/20 text-red-500 border border-red-600/50 hover:bg-red-600/40 hover:text-red-400 rounded-md font-medium transition-colors"
          >
            Limpiar Historial
          </button>
        )}
      </div>
      
      {matches.length === 0 ? (
        <div className="bg-gray-900 p-8 rounded-xl border border-gray-800 text-center text-gray-400">
          No hay partidas registradas aún. Sube tus capturas para comenzar.
        </div>
      ) : (
        <div className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden">
          <table className="w-full text-left">
            <thead className="bg-gray-950 border-b border-gray-800 text-gray-400 text-sm">
              <tr>
                <th className="p-4">Fecha</th>
                <th className="p-4">Resultado</th>
                <th className="p-4">Rango</th>
                <th className="p-4">Mapa</th>
                <th className="p-4">KDA</th>
                <th className="p-4">Duración</th>
                <th className="p-4">Replay Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              {matches.map((m) => {
                const date = new Date(m.created_at);
                const dateString = date.toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric' });
                const timeString = date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
                
                return (
                  <tr key={m.id} className="hover:bg-gray-800/50 transition-colors">
                    <td className="p-4 text-sm text-gray-400">
                      <div>{dateString}</div>
                      <div className="text-xs">{timeString}</div>
                    </td>
                    <td className={`p-4 font-bold ${m.result?.toUpperCase() === 'VICTORY' ? 'text-green-400' : 'text-red-400'}`}>
                      {m.result || 'Desconocido'}
                    </td>
                    <td className="p-4">
                      {m.rank ? (
                        <span className={`font-semibold ${m.rank.toUpperCase().includes('GRANDMASTER') ? 'text-yellow-500' : 'text-purple-400'}`}>
                          {m.rank}
                        </span>
                      ) : (
                        <span className="text-gray-500">-</span>
                      )}
                    </td>
                    <td className="p-4">{m.map_name || 'Desconocido'}</td>
                    <td className="p-4">{m.kda || '-'}</td>
                    <td className="p-4">{Math.floor(m.duration_seconds / 60)}:{(m.duration_seconds % 60).toString().padStart(2, '0')}</td>
                    <td className="p-4">
                      <span className={`px-2 py-1 rounded text-sm font-bold ${m.replay_score > 5 ? 'bg-blue-900/50 text-blue-400' : 'bg-gray-800 text-gray-300'}`}>
                        {m.replay_score}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
