"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      const formData = new URLSearchParams();
      formData.append("username", email); // OAuth2PasswordRequestForm expects 'username'
      formData.append("password", password);

      const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://rivals-analyzer-ocr.onrender.com";
      const res = await fetch(`${API_URL}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formData.toString(),
      });
      if (!res.ok) {
        const data = await res.json();
        let errorMessage = "Error en el login";
        if (data.detail) {
          if (Array.isArray(data.detail)) {
            errorMessage = data.detail.map((err: any) => err.msg).join(", ");
          } else {
            errorMessage = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
          }
        }
        throw new Error(errorMessage);
      }
      const data = await res.json();
      // En una app real, guardaríamos el token en cookies o localstorage
      localStorage.setItem("token", data.access_token);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-black">
      <div className="w-full max-w-md p-8 space-y-6 bg-gray-900 rounded-xl shadow-2xl border border-gray-800">
        <h2 className="text-3xl font-bold text-center text-white">Iniciar Sesión</h2>
        {error && <p className="text-red-500 text-sm text-center">{error}</p>}
        <form className="space-y-4" onSubmit={handleLogin}>
          <div>
            <label className="block text-sm font-medium text-gray-400">Email</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required className="w-full px-4 py-2 mt-1 bg-gray-800 border border-gray-700 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-primary" placeholder="tu@email.com" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400">Contraseña</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required className="w-full px-4 py-2 mt-1 bg-gray-800 border border-gray-700 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-primary" placeholder="••••••••" />
          </div>
          <button type="submit" className="w-full px-4 py-2 font-bold text-white bg-primary rounded-md hover:bg-blue-600 transition-colors">
            Entrar
          </button>
        </form>
        <p className="text-center text-sm text-gray-500">¿No tienes cuenta? <Link href="/register" className="text-primary hover:underline">Regístrate</Link></p>
      </div>
    </div>
  );
}
