"use client";
import React, { useEffect, useState, useMemo } from "react";

// Extracts the sub-map name (the specific location, not the zone)
function shortMapName(mapName: string): string {
  if (!mapName) return 'Desconocido';
  if (mapName.includes(' - ')) return mapName.split(' - ')[0].trim();
  if (mapName.includes('-')) {
    const last = mapName.split('-').pop()?.trim() || mapName;
    return last.charAt(0).toUpperCase() + last.slice(1).toLowerCase();
  }
  return mapName;
}

// Get main user's performance from a match
function getMainPerformance(match: any) {
  if (!match.performances || match.performances.length === 0) return null;
  return match.performances.find((p: any) => p.is_main_user) || null;
}

// Compute damage and healing per 10 minutes for the main user
function getPer10(match: any) {
  const perf = getMainPerformance(match);
  if (!perf || !match.duration_seconds) return { dmg: null, heal: null };
  const tenMins = match.duration_seconds / 600;
  return {
    dmg: Math.round(perf.damage / tenMins),
    heal: Math.round(perf.healing / tenMins),
  };
}

type SortKey =
  | 'created_at' | 'result' | 'rank' | 'map_name'
  | 'kda' | 'duration_seconds' | 'replay_score'
  | 'has_scoreboard' | 'dmg_per10' | 'heal_per10';

type SortDir = 'asc' | 'desc';

function sortValue(m: any, key: SortKey): any {
  switch (key) {
    case 'created_at':       return new Date(m.created_at).getTime();
    case 'result':           return m.result || '';
    case 'rank':             return m.rank || '';
    case 'map_name':         return shortMapName(m.map_name);
    case 'kda': {
      // Sort by kills
      const k = parseInt((m.kda || '0').split('/')[0]) || 0;
      return k;
    }
    case 'duration_seconds': return m.duration_seconds || 0;
    case 'replay_score':     return m.replay_score || 0;
    case 'has_scoreboard':   return m.performances?.length > 0 ? 1 : 0;
    case 'dmg_per10':        return getPer10(m).dmg ?? -1;
    case 'heal_per10':       return getPer10(m).heal ?? -1;
    default:                 return 0;
  }
}

const COLUMNS: { key: SortKey; label: string }[] = [
  { key: 'created_at',       label: 'Fecha'         },
  { key: 'result',           label: 'Resultado'     },
  { key: 'rank',             label: 'Rango'         },
  { key: 'map_name',         label: 'Mapa'          },
  { key: 'kda',              label: 'KDA'           },
  { key: 'duration_seconds', label: 'Duración'      },
  { key: 'replay_score',     label: 'Score'         },
  { key: 'dmg_per10',        label: 'DMG/10min'     },
  { key: 'heal_per10',       label: 'Cura/10min'    },
  { key: 'has_scoreboard',   label: 'Scoreboard'    },
];

export default function MatchesPage() {
  const [matches, setMatches] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedMatchId, setExpandedMatchId] = useState<number | null>(null);
  const [sortKey, setSortKey] = useState<SortKey>('created_at');
  const [sortDir, setSortDir] = useState<SortDir>('desc');

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

  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDir(d => d === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortDir('asc');
    }
  };

  const sortedMatches = useMemo(() => {
    return [...matches].sort((a, b) => {
      const va = sortValue(a, sortKey);
      const vb = sortValue(b, sortKey);
      if (va < vb) return sortDir === 'asc' ? -1 : 1;
      if (va > vb) return sortDir === 'asc' ? 1 : -1;
      return 0;
    });
  }, [matches, sortKey, sortDir]);

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

  const SortIcon = ({ col }: { col: SortKey }) => {
    if (sortKey !== col) return <span className="ml-1 text-gray-600">⇅</span>;
    return <span className="ml-1 text-indigo-400">{sortDir === 'asc' ? '↑' : '↓'}</span>;
  };

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
        <div className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-gray-950 border-b border-gray-800 text-gray-400">
              <tr>
                {COLUMNS.map(col => (
                  <th
                    key={col.key}
                    className="p-3 whitespace-nowrap cursor-pointer select-none hover:text-white hover:bg-gray-800/60 transition-colors"
                    onClick={() => handleSort(col.key)}
                  >
                    {col.label}<SortIcon col={col.key} />
                  </th>
                ))}
                {/* Details button column — not sortable */}
                <th className="p-3 text-gray-400"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              {sortedMatches.map((m) => {
                const date = new Date(m.created_at);
                const dateString = date.toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric' });
                const timeString = date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
                const { dmg, heal } = getPer10(m);
                const durationStr = m.duration_seconds
                  ? `${Math.floor(m.duration_seconds / 60)}:${(m.duration_seconds % 60).toString().padStart(2, '0')}`
                  : '-';
                const hasScoreboard = m.performances && m.performances.length > 0;

                return (
                  <React.Fragment key={m.id}>
                    <tr className={`hover:bg-gray-800/50 transition-colors ${expandedMatchId === m.id ? 'bg-gray-800/50' : ''}`}>
                      {/* Fecha */}
                      <td className="p-3 text-gray-400">
                        <div>{dateString}</div>
                        <div className="text-xs text-gray-500">{timeString}</div>
                      </td>
                      {/* Resultado */}
                      <td className={`p-3 font-bold ${m.result?.toUpperCase() === 'VICTORY' ? 'text-green-400' : m.result?.toUpperCase() === 'DRAW' ? 'text-yellow-400' : 'text-red-400'}`}>
                        {m.result || 'Desconocido'}
                      </td>
                      {/* Rango */}
                      <td className="p-3">
                        {m.rank ? (
                          <span className={`font-semibold text-xs ${m.rank.toUpperCase().includes('GRANDMASTER') ? 'text-yellow-500' : 'text-purple-400'}`}>
                            {m.rank}
                          </span>
                        ) : (
                          <span className="text-gray-600">-</span>
                        )}
                      </td>
                      {/* Mapa */}
                      <td className="p-3" title={m.map_name || ''}>
                        {shortMapName(m.map_name)}
                      </td>
                      {/* KDA */}
                      <td className="p-3 font-mono">{m.kda || '-'}</td>
                      {/* Duración */}
                      <td className="p-3 tabular-nums">{durationStr}</td>
                      {/* Replay Score */}
                      <td className="p-3">
                        <span className={`px-2 py-0.5 rounded text-xs font-bold ${m.replay_score > 5 ? 'bg-blue-900/50 text-blue-400' : 'bg-gray-800 text-gray-300'}`}>
                          {m.replay_score}
                        </span>
                      </td>
                      {/* DMG/10min */}
                      <td className="p-3">
                        {dmg !== null
                          ? <span className="text-orange-400 font-medium">{dmg.toLocaleString()}</span>
                          : <span className="text-gray-600">-</span>}
                      </td>
                      {/* Cura/10min */}
                      <td className="p-3">
                        {heal !== null
                          ? <span className="text-teal-400 font-medium">{heal.toLocaleString()}</span>
                          : <span className="text-gray-600">-</span>}
                      </td>
                      {/* Scoreboard badge */}
                      <td className="p-3">
                        {hasScoreboard ? (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-emerald-900/40 text-emerald-400 border border-emerald-700/50 rounded text-xs font-semibold">
                            ✓ Subido
                          </span>
                        ) : (
                          <span className="text-gray-600 text-xs">Pendiente</span>
                        )}
                      </td>
                      {/* Details button */}
                      <td className="p-3">
                        {hasScoreboard && (
                          <button
                            onClick={() => setExpandedMatchId(expandedMatchId === m.id ? null : m.id)}
                            className="px-3 py-1 bg-indigo-600/20 text-indigo-400 hover:bg-indigo-600/40 rounded text-xs transition-colors"
                          >
                            {expandedMatchId === m.id ? 'Ocultar' : 'Ver'}
                          </button>
                        )}
                      </td>
                    </tr>

                    {/* Expanded scoreboard detail */}
                    {expandedMatchId === m.id && hasScoreboard && (
                      <tr className="bg-gray-950 border-b border-gray-800">
                        <td colSpan={11} className="p-0">
                          <div className="p-6">
                            <h4 className="text-base font-bold mb-4 text-indigo-400">Estadísticas de Jugadores</h4>
                            <table className="w-full text-sm text-left">
                              <thead className="bg-gray-900 text-gray-400 border-b border-gray-800">
                                <tr>
                                  <th className="p-2">Jugador</th>
                                  <th className="p-2">Héroe</th>
                                  <th className="p-2">K / D / A</th>
                                  <th className="p-2">Daño</th>
                                  <th className="p-2">Curación</th>
                                  <th className="p-2">Mitigación</th>
                                  <th className="p-2 text-orange-400">DMG/10min</th>
                                  <th className="p-2 text-teal-400">Cura/10min</th>
                                </tr>
                              </thead>
                              <tbody className="divide-y divide-gray-800">
                                {m.performances.map((p: any) => {
                                  const tenMins = (m.duration_seconds || 600) / 600;
                                  const dmgPer10 = Math.round(p.damage / tenMins).toLocaleString();
                                  const healPer10 = Math.round(p.healing / tenMins).toLocaleString();
                                  return (
                                    <tr key={p.id} className={p.is_main_user ? 'bg-indigo-900/20' : ''}>
                                      <td className={`p-2 font-medium ${p.is_main_user ? 'text-yellow-500' : 'text-gray-300'}`}>
                                        {p.player_name || 'Desconocido'}
                                      </td>
                                      <td className="p-2 text-gray-300">{p.hero_name}</td>
                                      <td className="p-2 font-mono">{p.kills} / {p.deaths} / {p.assists}</td>
                                      <td className="p-2">{p.damage.toLocaleString()}</td>
                                      <td className="p-2">{p.healing.toLocaleString()}</td>
                                      <td className="p-2">{(p.mitigation || 0).toLocaleString()}</td>
                                      <td className="p-2 text-orange-400 font-medium">{dmgPer10}</td>
                                      <td className="p-2 text-teal-400 font-medium">{healPer10}</td>
                                    </tr>
                                  );
                                })}
                              </tbody>
                            </table>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
