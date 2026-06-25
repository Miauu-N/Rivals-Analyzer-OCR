"use client";
import { useState, useRef } from "react";
import { useRouter } from "next/navigation";

export default function UploadPage() {
  const router = useRouter();
  const [isDragging, setIsDragging] = useState(false);
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      setFiles(Array.from(e.dataTransfer.files));
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFiles(Array.from(e.target.files));
    }
  };

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (files.length === 0) return;
    setUploading(true);
    setError("");

    try {
      const token = localStorage.getItem("token");
      if (!token) throw new Error("No estás autenticado. Inicia sesión de nuevo.");

      const formData = new FormData();
      files.forEach((file) => formData.append("files", file));

      const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://rivals-analyzer-ocr.onrender.com";
      const res = await fetch(`${API_URL}/api/uploads/upload-images`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      if (!res.ok) {
        if (res.status === 401) {
          localStorage.removeItem("token");
          router.push("/login");
          throw new Error("Tu sesión ha expirado. Redirigiendo al inicio de sesión...");
        }
        throw new Error("Error al subir las imágenes");
      }

      setFiles([]);
      alert("¡Imágenes subidas y analizadas correctamente!");
      router.push("/matches");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-8 max-w-3xl mx-auto">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-4xl font-bold">Subir Capturas</h1>
          <p className="text-gray-400 mt-2">Sube capturas del historial de partidas o del scoreboard final. El sistema las clasificará automáticamente.</p>
        </div>
        <a 
          href="/datos_de_prueba.zip" 
          download 
          className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-md transition-colors border border-gray-700 flex items-center gap-2 text-sm whitespace-nowrap"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
          Datos de Prueba
        </a>
      </div>
      
      {error && <p className="text-red-500 font-medium">{error}</p>}

      <div 
        className={`mt-8 border-2 border-dashed rounded-xl p-12 text-center transition-colors cursor-pointer ${isDragging ? 'border-primary bg-primary/10' : 'border-gray-700 bg-gray-900/50 hover:bg-gray-900'}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input 
          type="file" 
          multiple 
          accept="image/*" 
          className="hidden" 
          ref={fileInputRef} 
          onChange={handleFileSelect} 
        />
        <div className="mx-auto w-16 h-16 mb-4 text-gray-500">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
          </svg>
        </div>
        <p className="text-lg font-medium text-white">Arrastra tus imágenes aquí</p>
        <p className="text-sm text-gray-500 mt-2">o haz clic para seleccionar archivos</p>
      </div>

      {files.length > 0 && (
        <div className="bg-gray-900 p-4 rounded-xl border border-gray-800">
          <h3 className="font-semibold text-gray-300 mb-3">Archivos seleccionados:</h3>
          <ul className="space-y-2">
            {files.map((f, i) => (
              <li key={i} className="flex justify-between items-center text-sm text-gray-400">
                <span>{f.name} ({(f.size / 1024 / 1024).toFixed(2)} MB)</span>
                <button onClick={() => removeFile(i)} className="text-red-500 hover:text-red-400">Quitar</button>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="flex justify-end mt-4">
        <button 
          onClick={handleUpload}
          disabled={files.length === 0 || uploading}
          className="px-6 py-2 bg-primary text-white rounded-md font-bold hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {uploading ? "Analizando..." : "Analizar Imágenes"}
        </button>
      </div>
    </div>
  );
}
