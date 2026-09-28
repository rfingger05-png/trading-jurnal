import re

with open('src/components/Gallery.tsx', 'r') as f:
    content = f.read()

# 1. Update imports
content = content.replace(
    "import { X } from 'lucide-react';",
    "import { X } from 'lucide-react';\nimport { formatImageUrl } from '../utils';"
)

# 2. Update filter logic
content = content.replace(
    "const tradesWithImages = trades.filter(t => t.image);",
    "const tradesWithImages = trades.filter(t => t.image || (t.image_url && t.image_url.trim() !== '' && t.image_url !== 'NULL'));"
)

# 3. Update map loop
old_map = """          {tradesWithImages.map(trade => (
            <div key={trade.id} className="bg-white dark:bg-neutral-900 border border-slate-200 dark:border-neutral-800 shadow-sm flex flex-col">"""

new_map = """          {tradesWithImages.map(trade => {
            const rawImg = trade.image || trade.image_url;
            const imgSrc = formatImageUrl(rawImg);
            return (
            <div key={trade.id} className="bg-white dark:bg-neutral-900 border border-slate-200 dark:border-neutral-800 shadow-sm flex flex-col">"""

content = content.replace(old_map, new_map)

# 4. Update image rendering
old_img = """                <div className="aspect-video bg-slate-100 dark:bg-neutral-950 border border-slate-200 dark:border-neutral-800 relative group overflow-hidden cursor-zoom-in" onClick={() => trade.image && setSelectedImage(trade.image)}>
                  {trade.image && (
                    <img src={trade.image} alt="Trade Chart" className="w-full h-full object-cover" />
                  )}"""

new_img = """                <div className="aspect-video bg-slate-100 dark:bg-neutral-950 border border-slate-200 dark:border-neutral-800 relative group overflow-hidden cursor-zoom-in" onClick={() => rawImg && setSelectedImage(imgSrc)}>
                  {imgSrc && (
                    <img 
                       src={imgSrc} 
                       alt="Trade Chart" 
                       className="w-full h-full object-cover" 
                       onError={(e) => {
                         if (rawImg && rawImg !== imgSrc) {
                           e.currentTarget.src = rawImg;
                         }
                       }}
                    />
                  )}"""

content = content.replace(old_img, new_img)

# 5. Add closing brace for map
old_close = """            </div>
          ))}"""
new_close = """            </div>
            );
          })}"""
content = content.replace(old_close, new_close)

with open('src/components/Gallery.tsx', 'w') as f:
    f.write(content)

