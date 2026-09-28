const fs = require('fs');
let code = fs.readFileSync('src/components/Dashboard.tsx', 'utf8');

code = code.replace(/\]\);\n\s*}, \[trades\]\);/g, "];\n  }, [trades]);");
code = code.replace(/\]\);\n\s*}, \[trades, today\]\);/g, "];\n  }, [trades, today]);");
code = code.replace(/\]\);\n\s*}, \[\]\);/g, "];\n  }, []);");
code = code.replace(/\]\);\n/g, "];\n");

fs.writeFileSync('src/components/Dashboard.tsx', code);
