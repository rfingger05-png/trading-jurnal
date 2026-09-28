const fs = require('fs');
let code = fs.readFileSync('src/components/Dashboard.tsx', 'utf8');
code = code.replace(/<h3 className="text-\[10px\] font-bold uppercase tracking-widest text-slate-400">Consistency \(90 Days, user\?\.currency \|\| 'USD'\)<\/h3>/, '<h3 className="text-[10px] font-bold uppercase tracking-widest text-slate-400">Consistency (90 Days)</h3>');
code = code.replace(/fill="url\(#colorPnl, user\?\.currency \|\| 'USD'\)"/g, 'fill="url(#colorPnl)"');
code = code.replace(/, user\?\.currency \|\| 'USD'\)}/g, '}');
code = code.replace(/, user\?\.currency \|\| 'USD'\);/g, ';');
fs.writeFileSync('src/components/Dashboard.tsx', code);
