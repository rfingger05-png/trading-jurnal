const fs = require('fs');
let code = fs.readFileSync('src/components/Dashboard.tsx', 'utf8');

code = code.replace(/pnl: runningPL\n\s*}\);/g, "pnl: runningPL\n        };");

fs.writeFileSync('src/components/Dashboard.tsx', code);
