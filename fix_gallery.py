import re

with open('src/components/Gallery.tsx', 'r') as f:
    content = f.read()

find_html = """              <div className="p-3 bg-white dark:bg-neutral-900 mt-auto border-t border-slate-100 dark:border-neutral-800">
                <p className="text-[10px] text-slate-600 dark:text-neutral-400 line-clamp-3 italic leading-relaxed">"{trade.notes || 'No reason provided.'}"</p>
                <div className="text-[8px] text-slate-400 uppercase tracking-widest mt-2"> 
                   {format(new Date(!isNaN(new Date(trade.created_at).getTime()) ? trade.created_at : (!isNaN(new Date(trade.created_at.replace(/\./g, '-').replace(' ', 'T') + 'Z').getTime()) ? trade.created_at.replace(/\./g, '-').replace(' ', 'T') + 'Z' : new Date())), 'dd MMM yyyy, HH:mm')}
                </div>
              </div>"""

replace_html = """              <div className="px-3 pb-3 mt-auto">
                <p className="text-xs text-slate-500 dark:text-neutral-400 whitespace-pre-wrap break-words opacity-90 leading-relaxed">
                  {trade.notes || 'No reason provided.'}
                </p>
                <div className="text-[8px] text-slate-400 uppercase tracking-widest mt-3"> 
                   {format(new Date(!isNaN(new Date(trade.created_at).getTime()) ? trade.created_at : (!isNaN(new Date(trade.created_at.replace(/\./g, '-').replace(' ', 'T') + 'Z').getTime()) ? trade.created_at.replace(/\./g, '-').replace(' ', 'T') + 'Z' : new Date())), 'dd MMM yyyy, HH:mm')}
                </div>
              </div>"""

content = content.replace(find_html, replace_html)

with open('src/components/Gallery.tsx', 'w') as f:
    f.write(content)

