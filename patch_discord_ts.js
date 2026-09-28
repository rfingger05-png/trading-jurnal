import fs from 'fs';
let content = fs.readFileSync('src/lib/discord.ts', 'utf-8');
content = content.replace(/channel\.send/g, '(channel as any).send');
content = content.replace(/channel\.messages/g, '(channel as any).messages');
fs.writeFileSync('src/lib/discord.ts', content);
console.log("Patched discord.ts");
