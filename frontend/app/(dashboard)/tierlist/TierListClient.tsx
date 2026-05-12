"use client";

import React, { useState, useRef, useEffect } from "react";
import html2canvas from "html2canvas";
import { Download, RefreshCcw } from "lucide-react";

interface Tier {
  id: string;
  name: string;
  color: string;
  items: string[];
}

interface TierListClientProps {
  initialIcons: string[];
}

export default function TierListClient({ initialIcons }: TierListClientProps) {
  const [tiers, setTiers] = useState<Tier[]>([
    { id: "s", name: "S", color: "#FF7F7F", items: [] },
    { id: "a", name: "A", color: "#FFBF7F", items: [] },
    { id: "b", name: "B", color: "#FFFF7F", items: [] },
    { id: "c", name: "C", color: "#7FFF7F", items: [] },
    { id: "d", name: "D", color: "#7FBFFF", items: [] },
  ]);
  
  const [unranked, setUnranked] = useState<string[]>([]);
  const [draggedItem, setDraggedItem] = useState<string | null>(null);
  const [dragSource, setDragSource] = useState<string | null>(null);
  const tierListRef = useRef<HTMLDivElement>(null);
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setUnranked(initialIcons);
    setIsMounted(true);
  }, [initialIcons]);

  const handleDragStart = (e: React.DragEvent, item: string, sourceId: string) => {
    setDraggedItem(item);
    setDragSource(sourceId);
    e.dataTransfer.effectAllowed = "move";
    // Set a transparent image or handle the drag image if needed,
    // but default works fine.
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = "move";
  };

  const handleDrop = (e: React.DragEvent, targetId: string) => {
    e.preventDefault();
    if (!draggedItem || !dragSource) return;

    if (dragSource === targetId) {
      return;
    }

    // Remove from source
    if (dragSource === "unranked") {
      setUnranked((prev) => prev.filter((i) => i !== draggedItem));
    } else {
      setTiers((prev) =>
        prev.map((tier) =>
          tier.id === dragSource ? { ...tier, items: tier.items.filter((i) => i !== draggedItem) } : tier
        )
      );
    }

    // Add to target
    if (targetId === "unranked") {
      setUnranked((prev) => [...prev, draggedItem]);
    } else {
      setTiers((prev) =>
        prev.map((tier) =>
          tier.id === targetId ? { ...tier, items: [...tier.items, draggedItem] } : tier
        )
      );
    }

    setDraggedItem(null);
    setDragSource(null);
  };

  const downloadImage = async () => {
    if (!tierListRef.current) return;
    try {
      const canvas = await html2canvas(tierListRef.current, {
        backgroundColor: "#030712", // matches gray-950 roughly
        useCORS: true,
        scale: 2, // better resolution
      });
      const dataUrl = canvas.toDataURL("image/png");
      const link = document.createElement("a");
      link.download = "rivals_tierlist.png";
      link.href = dataUrl;
      link.click();
    } catch (err) {
      console.error("Failed to download image", err);
    }
  };

  const handleClear = () => {
    const allItems = [...unranked];
    tiers.forEach(t => allItems.push(...t.items));
    setUnranked(allItems);
    setTiers(tiers.map(t => ({ ...t, items: [] })));
  };

  const formatName = (filename: string) => {
    return filename.replace(" Deluxe Avatar.webp", "").replace(".webp", "").replace("item_herohead_", "ID ");
  };

  if (!isMounted) return <div className="h-96 flex items-center justify-center">Cargando...</div>;

  return (
    <div className="flex flex-col gap-6 h-full">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center bg-gray-900 p-4 rounded-lg border border-gray-800 gap-4">
        <p className="text-gray-400 text-sm">Arrastra los personajes a sus categorías correspondientes para armar tu Tier List.</p>
        <div className="flex gap-3">
          <button onClick={handleClear} className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded transition-colors text-sm font-medium border border-gray-700">
            <RefreshCcw size={16} />
            Reiniciar
          </button>
          <button onClick={downloadImage} className="flex items-center gap-2 px-4 py-2 bg-primary hover:bg-primary/90 text-white rounded transition-colors text-sm font-medium shadow-lg shadow-primary/20">
            <Download size={16} />
            Descargar Imagen
          </button>
        </div>
      </div>

      <div 
        ref={tierListRef} 
        className="flex flex-col gap-[2px] p-4 bg-gray-950 rounded-xl border border-gray-800 min-h-[400px] shadow-xl"
      >
        {tiers.map((tier) => (
          <div 
            key={tier.id} 
            className="flex min-h-[100px] bg-gray-900 rounded overflow-hidden"
            onDragOver={handleDragOver}
            onDrop={(e) => handleDrop(e, tier.id)}
          >
            <div 
              className="w-24 md:w-32 flex items-center justify-center font-bold text-2xl text-black shrink-0 border-r border-gray-950 shadow-inner"
              style={{ backgroundColor: tier.color }}
            >
              {tier.name}
            </div>
            <div className="flex-1 flex flex-wrap gap-2 p-3 items-start content-start bg-[#1a1c23]">
              {tier.items.map((item) => (
                <div 
                  key={item}
                  draggable
                  onDragStart={(e) => handleDragStart(e, item, tier.id)}
                  className="w-16 h-16 md:w-20 md:h-20 bg-gray-800 rounded border-2 border-transparent hover:border-gray-500 cursor-grab active:cursor-grabbing overflow-hidden group shadow-md transition-transform hover:scale-105"
                  title={formatName(item)}
                >
                  <img src={`/icons/${item}`} alt={formatName(item)} className="w-full h-full object-cover pointer-events-none" />
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="flex flex-col gap-3">
        <h2 className="text-xl font-semibold text-gray-200 border-b border-gray-800 pb-2">Personajes sin clasificar ({unranked.length})</h2>
        <div 
          className="flex flex-wrap gap-3 p-4 bg-gray-900 rounded-xl border border-gray-800 min-h-[200px]"
          onDragOver={handleDragOver}
          onDrop={(e) => handleDrop(e, "unranked")}
        >
          {unranked.map((item) => (
            <div 
              key={item}
              draggable
              onDragStart={(e) => handleDragStart(e, item, "unranked")}
              className="w-16 h-16 md:w-20 md:h-20 bg-gray-800 rounded border-2 border-transparent hover:border-gray-500 cursor-grab active:cursor-grabbing overflow-hidden group shadow-md transition-transform hover:scale-105"
              title={formatName(item)}
            >
              <img src={`/icons/${item}`} alt={formatName(item)} className="w-full h-full object-cover pointer-events-none" />
            </div>
          ))}
          {unranked.length === 0 && (
            <div className="w-full h-full flex flex-col items-center justify-center text-gray-500 italic py-8">
              <span className="text-4xl mb-2">🎉</span>
              Todos los personajes han sido clasificados.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
