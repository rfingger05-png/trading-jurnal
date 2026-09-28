const fs = require('fs');
let code = fs.readFileSync('src/components/Dashboard.tsx', 'utf8');

code = code.replace(/length\);\n/g, "length;\n");
code = code.replace(/t\.realized_pl \|\| 0\)\);\n/g, "t.realized_pl || 0);\n");
code = code.replace(/\.getTime\(\)\)\);\n/g, ".getTime());\n");
code = code.replace(/a\.pnl\)\);\n/g, "a.pnl);\n");
code = code.replace(/b\.level\)\);\n/g, "b.level);\n");

fs.writeFileSync('src/components/Dashboard.tsx', code);
