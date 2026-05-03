export default function MatchDetailPage() {
  return (
    <div className="space-y-8">
      <div className="flex justify-between items-end border-b border-gray-800 pb-4">
        <div>
          <h1 className="text-4xl font-bold text-red-400">Derrota en Yggdrasill</h1>
          <p className="text-gray-400 mt-2">Hace 2 horas • Duración: 22:15</p>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-400">Replay Score</p>
          <p className="text-3xl font-bold text-blue-400">9.5</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-gray-900 p-6 rounded-xl border border-gray-800">
          <h3 className="text-xl font-bold mb-4">Tu Rendimiento</h3>
          <p className="text-purple-400 font-bold mb-4">Héroe: Spider-Man</p>
          <div className="space-y-2">
            <div className="flex justify-between"><span className="text-gray-400">K/D/A</span><span className="font-bold">8 / 6 / 12</span></div>
            <div className="flex justify-between"><span className="text-gray-400">Daño</span><span className="font-bold">14,500</span></div>
            <div className="flex justify-between"><span className="text-gray-400">Curación</span><span className="font-bold">0</span></div>
          </div>
        </div>

        <div className="bg-gray-900 p-6 rounded-xl border border-gray-800">
          <h3 className="text-xl font-bold mb-4">¿Por qué ver este replay?</h3>
          <ul className="list-disc list-inside space-y-2 text-gray-300">
            <li>Partida muy igualada (Derrota ajustada).</li>
            <li>Duración extensa indica muchas peleas de equipo.</li>
            <li>Alto nivel de asistencias pero bajo daño proporcional.</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
