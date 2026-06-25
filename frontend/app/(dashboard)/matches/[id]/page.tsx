"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";

export default function MatchDetailPage() {
  const { id } = useParams();
  const [match, setMatch] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    const fetchMatch = async () => {
      try {
        const token = localStorage.getItem("token");
        const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://rivals-analyzer-ocr.onrender.com";
        const res = await fetch(`${API_URL}/api/matches/${id}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          setMatch(data);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchMatch();
  }, [id]);

  if (loading) return <div className="text-gray-500">Cargando partida...</div>;
  if (!match) return <div className="text-red-500">No se pudo cargar la partida.</div>;

  const isVictory = match.result === 'Victory' || match.result === 'Win' || match.result === 'WIN' || match.result === 'VICTORY' || match.result === 'VICTORY!';
  const titleColor = isVictory ? 'text-green-400' : 'text-red-400';
  const resultText = isVictory ? 'Victoria' : 'Derrota';

  // Find main user performance
  const mainPerf = match.performances?.find((p: any) => p.is_main_user) || {};

  return (
    <div className="space-y-8">
      <Link href="/dashboard" className="text-gray-400 hover:text-white transition-colors mb-4 inline-block">
        &larr; Volver al Dashboard
      </Link>
      <div className="flex justify-between items-end border-b border-gray-800 pb-4">
        <div>
          <h1 className={`text-4xl font-bold ${titleColor}`}>{resultText} en {match.map_name || 'Mapa Desconocido'}</h1>
          <p className="text-gray-400 mt-2">
            Fecha: {new Date(match.created_at).toLocaleString()} • Duración: {match.duration_seconds ? `${Math.floor(match.duration_seconds / 60)}:${(match.duration_seconds % 60).toString().padStart(2, '0')}` : '--'} mins
          </p>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-400">Replay Score</p>
          <p className="text-3xl font-bold text-blue-400">{match.replay_score || 0}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-gray-900 p-6 rounded-xl border border-gray-800">
          <h3 className="text-xl font-bold mb-4">Tu Rendimiento</h3>
          {mainPerf.hero_name && (
            <p className="text-purple-400 font-bold mb-4">Rol / Personaje: {mainPerf.hero_name}</p>
          )}
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-400">K/D/A</span>
              <span className="font-bold">{match.kda || `${mainPerf.kills || 0} / ${mainPerf.deaths || 0} / ${mainPerf.assists || 0}`}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Daño</span>
              <span className="font-bold">{mainPerf.damage?.toLocaleString() || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Curación</span>
              <span className="font-bold">{mainPerf.healing?.toLocaleString() || 0}</span>
            </div>
            {mainPerf.mitigation !== null && mainPerf.mitigation !== undefined && (
              <div className="flex justify-between">
                <span className="text-gray-400">Mitigación</span>
                <span className="font-bold">{mainPerf.mitigation.toLocaleString()}</span>
              </div>
            )}
          </div>
        </div>

        <div className="bg-gray-900 p-6 rounded-xl border border-gray-800">
          <h3 className="text-xl font-bold mb-4">Detalles Extra</h3>
          <ul className="list-disc list-inside space-y-2 text-gray-300">
            {match.rank && <li>Rango: {match.rank}</li>}
            {match.replay_id && <li>Replay ID: {match.replay_id}</li>}
            {match.replay_score >= 7 && <li className="text-green-400">¡Buen puntaje de Replay! Deberías considerarla como destacada.</li>}
            {match.performances && match.performances.length > 0 ? (
               <li>Hay {match.performances.length} jugadores registrados en el tablero.</li>
            ) : (
               <li>No hay detalles de jugadores (registrado solo desde historial rápido).</li>
            )}
          </ul>
        </div>
      </div>
    </div>
  );
}
