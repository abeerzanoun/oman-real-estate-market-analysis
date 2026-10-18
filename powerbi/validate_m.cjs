// Microsoft's parser checks language syntax, not evaluation or library bindings.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const parser = require('@microsoft/powerquery-parser');

(async () => {
  const dir = path.join(__dirname, 'm');
  const results = [];
  for (const name of fs.readdirSync(dir).filter(n => n.endsWith('.pq')).sort()) {
    const payload = fs.readFileSync(path.join(dir, name));
    const parsed = await parser.TaskUtils.tryLexParse(parser.DefaultSettings, payload.toString('utf8'));
    if (parser.TaskUtils.isError(parsed)) {
      throw new Error(`${name}: Microsoft parser rejected M syntax: ${parsed.error.message}`);
    }
    results.push({file: `m/${name}`, sha256: crypto.createHash('sha256').update(payload).digest('hex'), syntax: 'passed'});
  }
  const result = {
    parser: '@microsoft/powerquery-parser', version: '0.19.0',
    validation: 'syntax_only', microsoft_power_query_engine_executed: false, queries: results
  };
  const text = JSON.stringify(result, null, 2) + '\n';
  const target = path.join(__dirname, 'validation', 'm_syntax_results.json');
  if (process.argv.includes('--check')) {
    if (!fs.existsSync(target) || fs.readFileSync(target, 'utf8') !== text) {
      throw new Error('Stale M syntax report; run node powerbi/validate_m.cjs');
    }
  } else {
    fs.writeFileSync(target, text);
  }
  console.log(`${results.length} Power Query files passed Microsoft parser syntax checks; engine execution pending.`);
})().catch(error => { console.error(error.message); process.exitCode = 1; });
