const fs = require('fs');
let code = fs.readFileSync('src/components/Dashboard.tsx', 'utf8');
code = code.replace(/;\s*}/g, ');\n}');
fs.writeFileSync('src/components/Dashboard.tsx', code);
