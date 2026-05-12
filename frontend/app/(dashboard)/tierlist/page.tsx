import fs from 'fs';
import path from 'path';
import TierListClient from './TierListClient';

export default function TierListPage() {
  const iconsDirectory = path.join(process.cwd(), 'public/icons');
  let icons: string[] = [];
  try {
    const files = fs.readdirSync(iconsDirectory);
    // Filter out only webp or png files
    icons = files.filter(file => file.endsWith('.webp') || file.endsWith('.png'));
  } catch (err) {
    console.error('Error reading icons directory:', err);
  }

  return (
    <div className="flex flex-col h-full gap-4">
      <h1 className="text-3xl font-bold text-primary mb-4">Tier List Maker</h1>
      <TierListClient initialIcons={icons} />
    </div>
  );
}
