const fs = require('fs');
let code = fs.readFileSync('src/components/Dashboard.tsx', 'utf8');

// Undo the `;\s*}` to `);\n}` that caused so much damage
// Wait, `);` before `}` was replaced by `));`. `});` was replaced by `}));`.
code = code.replace(/\)\);\n}/g, ');\n}');

// But some might have been `;\n}` like `return new Date(...);\n}` which became `return new Date(...));\n}`
code = code.replace(/Z'\)\);\n\}/g, "Z');\n}");
code = code.replace(/created_at\)\)\);\n\}/g, "created_at));\n}");
code = code.replace(/89\)\);\n\}/g, "89);\n}");
code = code.replace(/0\)\);\n\}/g, "0);\n}");
code = code.replace(/a\.pnl\)\);\n\}/g, "a.pnl);\n}");
code = code.replace(/b\.level\)\);\n\}/g, "b.level);\n}");
code = code.replace(/today\)\);\n\}/g, "today);\n}");

fs.writeFileSync('src/components/Dashboard.tsx', code);
