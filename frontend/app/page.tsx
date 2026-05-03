import Link from "next/link";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gradient-to-br from-gray-900 to-black text-white">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm lg:flex flex-col text-center space-y-8">
        <h1 className="text-6xl font-bold tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-600">
          Rivals Replay Analyzer
        </h1>
        <p className="text-xl text-gray-400 max-w-2xl">
          Sube tus capturas de pantalla de Marvel Rivals y deja que nuestro sistema analice tu historial y scoreboards para recomendarte las mejores partidas para revisar y mejorar.
        </p>
        
        <div className="flex gap-4 mt-8">
          <Link href="/login" className="px-8 py-3 bg-primary text-white rounded-md font-semibold hover:bg-blue-600 transition-colors">
            Comenzar
          </Link>
          <Link href="/register" className="px-8 py-3 bg-gray-800 text-white rounded-md font-semibold hover:bg-gray-700 transition-colors">
            Crear cuenta
          </Link>
        </div>
      </div>
    </main>
  );
}
