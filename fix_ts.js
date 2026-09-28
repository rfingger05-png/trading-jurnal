import fs from 'fs';
let content = fs.readFileSync('src/lib/telegram.ts', 'utf8');
content = content.replace(/disable_web_page_preview: false/g, 'link_preview_options: { is_disabled: false }');
content = content.replace(/const caption = ctx\.message\.caption;/g, 'const caption = (ctx.message as any).caption;');
fs.writeFileSync('src/lib/telegram.ts', content);
console.log('Fixed TS errors');
