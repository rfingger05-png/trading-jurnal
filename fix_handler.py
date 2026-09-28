import re

with open('src/lib/telegram.ts', 'r') as f:
    content = f.read()

find_compound = """      } else if (timeframe === 'compound') {
        const sisaTarget = targetBalance - currentEquity;
        const rawProgress = (currentEquity / targetBalance) * 100;
        const progressPercent = rawProgress > 100 ? 100 : rawProgress;
        
        // Buat Progress Bar 10 blok
        const filledBlocks = Math.floor(progressPercent / 10);
        const emptyBlocks = 10 - filledBlocks;
        const progressBar = '🟩'.repeat(filledBlocks) + '⬜'.repeat(emptyBlocks);
        
        let estimasiHari = 0;
        if (currentEquity > 0 && targetBalance > currentEquity) {
            estimasiHari = Math.ceil(Math.log(targetBalance / currentEquity) / Math.log(1.05));
        }

        let msg = `📈 <b>COMPOUNDING PROGRESS & PLAN</b>\\n━━━━━━━━━━━━━━━━━━━\\n`;
        msg += `💰 <b>Balance Saat Ini:</b> ${currentEquity.toLocaleString('en-US', {minimumFractionDigits:0, maximumFractionDigits:2})} USC\\n`;
        msg += `🎯 <b>Target Akhir:</b> ${targetBalance.toLocaleString('en-US', {minimumFractionDigits:0, maximumFractionDigits:2})} USC\\n`;
        msg += `📊 <b>Progres Total:</b> [${progressBar}] ${progressPercent.toFixed(2)}%\\n`;
        msg += `🚀 <b>Sisa Target:</b> ${sisaTarget > 0 ? sisaTarget.toLocaleString('en-US', {minimumFractionDigits:0, maximumFractionDigits:2}) : 0} USC\\n`;
        msg += `⏳ <b>Estimasi Sisa:</b> ~${estimasiHari} Hari Trading\\n\\n`;
        msg += `🗓️ <b>Proyeksi Target 10 Hari Ke Depan (Net 5%/Hari):</b>\\n`;

        let projEquity = currentEquity;
        for (let i = 1; i <= 10; i++) {
           let risk = projEquity * 0.025; // 2.5% risk
           let lot = risk / 150; // SL 15 pips (150 points for USC standard calculation if 1 pip = 10, or depends. 15 pips * 10 = $150 per lot? User logic: risk/(sl_pips*pip_value). Usually standard lot is risk/(15). Let's use risk/150 as a placeholder if they use micro accounts, or risk/15. Wait, 15 pips on gold = 150 ticks. If 1 lot = $1 per tick, 150 ticks = $150. lot = risk / 150. Let's use risk / 150 for XAUUSD.)
           // We will format them properly.
           
           projEquity = projEquity * 1.05;
           msg += `• <b>Hari ${i}:</b> Balance ${projEquity.toLocaleString('en-US', {minimumFractionDigits:0, maximumFractionDigits:2})} USC | Lot: ${lot.toFixed(2)} | Risk: ${risk.toLocaleString('en-US', {minimumFractionDigits:0, maximumFractionDigits:2})} USC\\n`;
        }
        
        msg += `━━━━━━━━━━━━━━━━━━━\\n<i>*Gunakan command \`/settarget <jumlah>\` untuk mengubah target.</i>`;
        await sendOrEdit(ctx, msg, true);
        return;
      }"""

replace_compound = """      } else if (timeframe === 'compound') {
        try {
          // 1. SAFE GUARD DATA & NULL CHECK
          let safeBalance = currentEquity && currentEquity > 0 ? currentEquity : 1000;
          let safeTarget = targetBalance && targetBalance > 0 ? targetBalance : 1000000;

          // Cegah division by zero
          if (safeTarget <= 0) safeTarget = 1000000;

          const sisaTarget = safeTarget - safeBalance;
          
          // 2. PENANGANAN MATH LOGIC COMPOUNDING
          const rawProgress = (safeBalance / safeTarget) * 100;
          const progressPercent = Math.min(100, Math.max(0, rawProgress));
          const progressPercentStr = progressPercent.toFixed(1);
          
          // Buat Progress Bar 10 blok
          const filledBlocks = Math.floor(progressPercent / 10);
          const emptyBlocks = 10 - filledBlocks;
          const progressBar = '🟩'.repeat(filledBlocks) + '⬜'.repeat(emptyBlocks);
          
          let estimasiHari = 0;
          if (safeTarget > safeBalance) {
              estimasiHari = Math.ceil(Math.log(safeTarget / safeBalance) / Math.log(1.05));
          }

          let msg = `📈 <b>COMPOUNDING PROGRESS & PLAN</b>\\n━━━━━━━━━━━━━━━━━━━\\n`;
          msg += `💰 <b>Balance Saat Ini:</b> ${safeBalance.toLocaleString('en-US', {minimumFractionDigits:0, maximumFractionDigits:2})} USC\\n`;
          msg += `🎯 <b>Target Akhir:</b> ${safeTarget.toLocaleString('en-US', {minimumFractionDigits:0, maximumFractionDigits:2})} USC\\n`;
          msg += `📊 <b>Progres Total:</b> [${progressBar}] ${progressPercentStr}%\\n`;
          msg += `🚀 <b>Sisa Target:</b> ${sisaTarget > 0 ? sisaTarget.toLocaleString('en-US', {minimumFractionDigits:0, maximumFractionDigits:2}) : 0} USC\\n`;
          msg += `⏳ <b>Estimasi Sisa:</b> ~${estimasiHari} Hari Trading\\n\\n`;
          msg += `🗓️ <b>Proyeksi Target 10 Hari Ke Depan (Net 5%/Hari):</b>\\n`;

          let projEquity = safeBalance;
          for (let i = 1; i <= 10; i++) {
             // Loop 10 hari ke depan
             projEquity = projEquity * 1.05;
             let risk = projEquity * 0.025; // 2.5% risk
             let lot = Math.max(0.01, risk / 150); // SL 15 pips
             
             msg += `• <b>Hari ${i}:</b> Balance ${projEquity.toLocaleString('en-US', {minimumFractionDigits:0, maximumFractionDigits:2})} USC | Lot: ${lot.toFixed(2)} | Risk: ${risk.toLocaleString('en-US', {minimumFractionDigits:0, maximumFractionDigits:2})} USC\\n`;
          }
          
          msg += `━━━━━━━━━━━━━━━━━━━\\n<i>*Gunakan command \`/settarget <jumlah>\` untuk mengubah target.</i>`;
          await sendOrEdit(ctx, msg, true);
          return;
        } catch (err) {
          console.error(err);
          await ctx.reply('❌ Gagal memuat data compounding.');
          return;
        }
      }"""

if find_compound in content:
    content = content.replace(find_compound, replace_compound)
    with open('src/lib/telegram.ts', 'w') as f:
        f.write(content)
        print("Updated compound block")
else:
    print("find_compound not found")
