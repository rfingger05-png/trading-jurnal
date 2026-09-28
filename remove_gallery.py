import re

with open('src/App.tsx', 'r') as f:
    content = f.read()

content = content.replace("import Gallery from './components/Gallery';\n", "")
content = re.sub(r'<button[^>]*>Gallery</button>', '', content, flags=re.MULTILINE | re.DOTALL)
# wait, there's a specific block for the gallery button
gallery_button = """                <button 
                  onClick={() => { setActiveTab('gallery'); setMenuOpen(false); }}
                  className={`text-left px-4 py-3 rounded-sm hover:bg-slate-50 dark:bg-neutral-950 hover:text-black dark:hover:text-neutral-100 transition-colors ${activeTab === 'gallery' ? 'text-black dark:text-neutral-100 bg-slate-50 dark:bg-neutral-950 shadow-sm border border-slate-100 dark:border-neutral-800' : ''}`}
                >Gallery</button>"""
content = content.replace(gallery_button, "")
content = content.replace("{activeTab === 'gallery' && <Gallery trades={trades} onTradeUpdated={fetchTrades} />}", "")

with open('src/App.tsx', 'w') as f:
    f.write(content)

