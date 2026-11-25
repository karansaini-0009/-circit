import path from 'node:path';
import readline from 'node:readline';
import { fileURLToPath } from 'node:url';
// Keep stdout reserved for the JSON-line bridge protocol. Redirect console
// output before loading the TTS package so diagnostics cannot corrupt the
// JSON handshake.
console.log = (...args) => console.error(...args);
const { KokoroTTS } = await import('kokoro-js');

const here = path.dirname(fileURLToPath(import.meta.url));
const modelDir = process.env.CIRCIT_KOKORO_MODEL_DIR || path.join(here, 'kokoro-model');
const serverMode = process.argv.includes('--server');
const supportedVoices = new Set([
  'af_heart','af_alloy','af_aoede','af_bella','af_jessica','af_kore','af_nicole','af_nova','af_river','af_sarah','af_sky',
  'am_adam','am_echo','am_eric','am_fenrir','am_liam','am_michael','am_onyx','am_puck','am_santa',
  'bf_alice','bf_emma','bf_isabella','bf_lily','bm_daniel','bm_fable','bm_george','bm_lewis',
  'hf_alpha','hf_beta','hm_omega','hm_psi'
]);

async function loadModel() {
  return await KokoroTTS.from_pretrained('onnx-community/Kokoro-82M-v1.0-ONNX', {
    dtype: 'q8',
    device: 'cpu',
    cache_dir: modelDir
  });
}

if (serverMode) {
  let tts;
  try {
    tts = await loadModel();
    process.stdout.write(JSON.stringify({ready: true}) + '\n');
  } catch (e) {
    process.stdout.write(JSON.stringify({ready: false, error: String(e?.message || e)}) + '\n');
    process.exit(1);
  }
  const rl = readline.createInterface({input: process.stdin, crlfDelay: Infinity});
  for await (const line of rl) {
    let req;
    try { req = JSON.parse(line); } catch { process.stdout.write(JSON.stringify({ok:false,error:'Invalid request JSON'})+'\n'); continue; }
    if (req.quit) break;
    try {
      const text = String(req.text || '').trim();
      const out = String(req.out || '');
      const voice = String(req.voice || 'af_heart');
      if (!text || !out) throw new Error('Text and output path are required.');
      if (!supportedVoices.has(voice)) throw new Error(`Unsupported Kokoro voice: ${voice}`);
      const audio = await tts.generate(text, {voice});
      await audio.save(out);
      process.stdout.write(JSON.stringify({ok:true}) + '\n');
    } catch (e) {
      process.stdout.write(JSON.stringify({ok:false,error:String(e?.message || e)}) + '\n');
    }
  }
} else {
  // Legacy one-shot mode remains supported for manual testing.
  const args = process.argv.slice(2);
  function arg(name) { const i = args.indexOf(name); return i >= 0 ? args[i+1] : undefined; }
  const text = arg('--text');
  const out = arg('--out');
  const voice = arg('--voice') || 'af_heart';
  if (!text || !out) { console.error('Usage: node kokoro_tts.mjs --text "text" --out output.wav [--voice af_heart]'); process.exit(2); }
  if (!supportedVoices.has(voice)) { console.error(`Unsupported Kokoro voice: ${voice}`); process.exit(2); }
  const tts = await loadModel();
  const audio = await tts.generate(text, {voice});
  await audio.save(out);
}
