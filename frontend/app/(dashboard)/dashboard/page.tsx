"use client";
import { useEffect, useState } from "react";
import Link from "next/link";

export default function DashboardPage() {
  const [recommended, setRecommended] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRecommended = async () => {
      try {
        const token = localStorage.getItem("token");
        const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://rivals-analyzer-ocr.onrender.com";
        const res = await fetch(`${API_URL}/api/matches/recommended`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          setRecommended(data);
        }
      } catch (err) {
        console.error("Error fetching recommended matches", err);
      } finally {
        setLoading(false);
      }
    };
    fetchRecommended();
  }, []);

  return (
    <div className="space-y-8">
      <h1 className="text-4xl font-bold">Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-gray-900 p-6 rounded-xl border border-gray-800">
          <p className="text-gray-400 text-sm">Partidas Analizadas</p>
          <p className="text-3xl font-bold mt-2">--</p>
        </div>
        <div className="bg-gray-900 p-6 rounded-xl border border-gray-800">
          <p className="text-gray-400 text-sm">Win Rate</p>
          <p className="text-3xl font-bold mt-2 text-green-400">--%</p>
        </div>
        <div className="bg-gray-900 p-6 rounded-xl border border-gray-800">
          <p className="text-gray-400 text-sm">Héroe más jugado</p>
          <p className="text-3xl font-bold mt-2 text-purple-400">--</p>
        </div>
        <div className="bg-gray-900 p-6 rounded-xl border border-gray-800">
          <p className="text-gray-400 text-sm">KDA Promedio</p>
          <p className="text-3xl font-bold mt-2 text-blue-400">--</p>
        </div>
      </div>

      <div>
        <h2 className="text-2xl font-semibold mb-4">Replays Recomendados</h2>
        {loading ? (
          <p className="text-gray-500">Cargando...</p>
        ) : recommended.length === 0 ? (
          <div className="bg-gray-900 rounded-xl border border-gray-800 p-8 text-center text-gray-500">
            Aún no hay partidas recomendadas. Sube imágenes a la pestaña de "Subir".
          </div>
        ) : (
          <div className="bg-gray-900 rounded-xl border border-gray-800 p-4 divide-y divide-gray-800">
            {recommended.map((m) => (
              <div key={m.id} className="py-4 flex justify-between items-center">
                <div>
                  <p className="font-bold">{m.result === 'Victory' ? 'Victoria' : 'Derrota'} en {m.map_name || 'Mapa Desconocido'}</p>
                  <p className="text-sm text-gray-400">
                    Duración: {Math.floor(m.duration_seconds / 60)}:{(m.duration_seconds % 60).toString().padStart(2, '0')} mins • 
                    Score: <span className="text-blue-400 font-bold">{m.replay_score}</span>
                  </p>
                </div>
                <Link href={`/matches/${m.id}`} className="px-4 py-2 bg-gray-800 rounded-md hover:bg-gray-700 transition-colors">
                  Ver Detalles
                </Link>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
