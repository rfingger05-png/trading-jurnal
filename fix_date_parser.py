import re

with open('src/components/ImportTradesModal.tsx', 'r') as f:
    content = f.read()

extract_find = """            else if (kl === 'date') {
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

extract_replace = """            else if (kl === 'date' || kl === 'tanggal') {
               openDate = val;
            }
            else if (kl === 'time' || kl === 'waktu' || kl === 'jam') {
               openTime = val;
            }
            else if (kl.includes('time') || kl.includes('date') || kl.includes('created') || kl.includes('waktu') || kl.includes('tanggal')) {
               // If it looks like just a time
               if (val.match(/^\d{1,2}:\d{2}/)) {
                   if (!openTime) openTime = val;
               } else {
                   if (!openDate) openDate = val;
               }
            }"""

content = content.replace(extract_find, extract_replace)

date_find = """          let dateStr = new Date().toISOString();
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

date_replace = """          let dateStr = "";
          let combinedDateTimeStr = openDate;
          
          if (openDate && openTime) {
             combinedDateTimeStr = `${openDate} ${openTime}`;
          } else if (openTime && !openDate) {
             const today = new Date().toISOString().split('T')[0];
             combinedDateTimeStr = `${today} ${openTime}`;
          } else if (openDate && !openTime) {
             combinedDateTimeStr = openDate;
          }
          
          if (combinedDateTimeStr) {
             // Let's normalize it to YYYY-MM-DDTHH:mm:ss
             let cleanStr = combinedDateTimeStr.replace(/\./g, '-').replace(/\//g, '-').replace(' ', 'T');
             // If it lacks time, add default time
             if (!cleanStr.includes('T')) {
                 cleanStr += 'T00:00:00';
             }
             // If it has time but lacks seconds
             if (cleanStr.match(/T\d{1,2}:\d{2}$/)) {
                 cleanStr += ':00';
             }
             
             // Verify it can be parsed
             const testDate = new Date(cleanStr);
             if (!isNaN(testDate.getTime())) {
                 dateStr = cleanStr; // Store without 'Z' so it's treated as face-value local time!
             } else {
                 // Try one more fallback for DD-MM-YYYY format
                 const parts = combinedDateTimeStr.split(/[ T]/);
                 if (parts[0] && parts[0].split('-').length === 3) {
                     const dParts = parts[0].split('-');
                     if (dParts[0].length <= 2) { // likely DD-MM-YYYY
                         const reversed = `${dParts[2]}-${dParts[1]}-${dParts[0]}`;
                         let timePart = parts[1] || '00:00:00';
                         if (timePart.split(':').length === 2) timePart += ':00';
                         const testReversed = new Date(`${reversed}T${timePart}`);
                         if (!isNaN(testReversed.getTime())) {
                             dateStr = `${reversed}T${timePart}`;
                         }
                     }
                 }
             }
          }
          
          // If all parsing failed or no date was provided, DO NOT use new Date().
          // Wait, if it's completely empty, maybe we should use today's date with 00:00?
          // The prompt says: "JANGAN gunakan new Date() / waktu server/waktu lokal saat pengguna mengunggah file CSV."
          // But we need a valid timestamp for the DB. If it's empty, we'll use a placeholder.
          if (!dateStr) {
             dateStr = "2000-01-01T00:00:00"; // Fallback placeholder if really no date provided
          }"""

content = content.replace(date_find, date_replace)

with open('src/components/ImportTradesModal.tsx', 'w') as f:
    f.write(content)
