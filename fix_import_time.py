import re

with open('src/components/ImportTradesModal.tsx', 'r') as f:
    content = f.read()

# 1. Update variables
content = content.replace(
    "let openTime = '';\n          let image = null;",
    "let openDate = '';\n          let openTime = '';\n          let image = null;"
)

# 2. Update column extraction
extract_find = """            else if (kl.includes('time') || kl.includes('date') || kl.includes('created')) {
               openTime = val;
            }"""
extract_replace = """            else if (kl === 'date') {
               openDate = val;
            }
            else if (kl === 'time') {
               openTime = val;
            }
            else if (kl.includes('time') || kl.includes('date') || kl.includes('created')) {
               if (!openDate && !openTime) {
                  openDate = val;
               }
            }"""
content = content.replace(extract_find, extract_replace)

# 3. Update Date construction
date_find = """          let dateStr = new Date().toISOString();
          if (openTime) {
            let d = new Date(openTime);
            if (isNaN(d.getTime())) {
               // Fallback for MT4/MT5 "YYYY.MM.DD HH:mm:ss"
               const cleanStr = openTime.replace(/\./g, '-').replace(' ', 'T') + 'Z';
               d = new Date(cleanStr);
            }
            if (!isNaN(d.getTime())) {
              dateStr = d.toISOString();
            }
          }"""
date_replace = """          let dateStr = new Date().toISOString();
          let combinedDateTimeStr = openDate;
          if (openDate && openTime) {
             combinedDateTimeStr = `${openDate} ${openTime}`;
          } else if (openTime && !openDate) {
             const today = new Date().toISOString().split('T')[0];
             combinedDateTimeStr = `${today} ${openTime}`;
          }
          
          if (combinedDateTimeStr) {
            let d = new Date(combinedDateTimeStr);
            if (isNaN(d.getTime())) {
               // Fallback for MT4/MT5 "YYYY.MM.DD HH:mm:ss"
               const cleanStr = combinedDateTimeStr.replace(/\./g, '-').replace(' ', 'T') + 'Z';
               d = new Date(cleanStr);
            }
            // Additional fallback if it's just a time like "19:36"
            if (isNaN(d.getTime()) && combinedDateTimeStr.match(/^\d{1,2}:\d{2}$/)) {
               const today = new Date().toISOString().split('T')[0];
               d = new Date(`${today}T${combinedDateTimeStr}:00Z`);
            }
            if (!isNaN(d.getTime())) {
              dateStr = d.toISOString();
            }
          }"""
content = content.replace(date_find, date_replace)

with open('src/components/ImportTradesModal.tsx', 'w') as f:
    f.write(content)

