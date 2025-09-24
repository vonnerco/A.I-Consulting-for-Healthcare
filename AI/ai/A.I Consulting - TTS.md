End-to-End TTS Playbook (Click-to-Hear for Markdown & Web Content)

Reference image: “2nd Card: Patient-Friendly Version” (patient message with headings like What happened, Next steps, What to expect). We’ll use this as the running example for clickable read-aloud.

1) Core Decisions (Voices, Where TTS Runs, and UX)

Voice source

Browser-native (Web Speech API): zero backend, fastest to ship, limited voices/SSML, Safari/iOS quirks.

Cloud TTS (Azure, Google, Amazon Polly, ElevenLabs): best quality, SSML, phonemes, word timings; needs a backend & auth.

Hybrid: default to Web Speech; fall back to cloud for unsupported languages/SSML; pre-generate audio for heavy pages.

When to synthesize

On-demand (user click sends text → audio): flexible, no storage; latency depends on network/provider.

Pre-generated (build or publish time): fastest playback; requires asset pipeline and cache invalidation.

Granularity

Whole card (image example), per section (What happened, Next steps…), and term-level buttons (e.g., “Fallopian tube”, “hydrosalpinx”).

Accessibility & Compliance

WCAG 2.2 AA: keyboard focusable controls, visible focus, aria-labels, descriptive button text.

PHI/safety: no patient identifiers in logs; sign BAAs if HIPAA-scope; encrypt in transit/at rest.

Respect autoplay policies: only play after a user gesture.

2) Minimal Front-End (No Backend) — Web Speech API
<div id="card" aria-label="Patient-Friendly Version">
  <h2>What happened</h2>
  <p id="p1">The doctor worked on the left side ... Then they did the same thing on the right side.</p>
  <button class="tts" data-target="p1" aria-label="Read: What happened">🔊 Hear this</button>

  <h2>Next steps</h2>
  <p id="p2">Your medical team will watch how you're healing ...</p>
  <button class="tts" data-target="p2" aria-label="Read: Next steps">🔊 Hear this</button>

  <h2>What to expect</h2>
  <p id="p3">You might feel some pain as your body heals ...</p>
  <button class="tts" data-target="p3" aria-label="Read: What to expect">🔊 Hear this</button>
</div>

<script>
const synth = window.speechSynthesis;
let current;

function speakText(text, {rate=1, pitch=1, lang='en-US'} = {}) {
  if (!synth) return alert('TTS not supported by this browser.');
  if (synth.speaking) synth.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.rate = rate; u.pitch = pitch; u.lang = lang;
  current = u; synth.speak(u);
}

document.querySelectorAll('.tts').forEach(btn=>{
  btn.addEventListener('click', e=>{
    const t = document.getElementById(btn.dataset.target)?.innerText?.trim();
    if (t) speakText(t);
  });
});
</script>


Notes

Works in Chrome/Edge; Safari/iOS supports it but with quirks (no queueing; requires user gesture).

Add a Stop button: speechSynthesis.cancel().

Add speed control (0.8–1.2) for patient comfort.

3) React/Next.js Production Component (Browser-safe, SSR-proof)
// components/ClickToHear.tsx
import {useRef, useEffect, useState} from 'react';
export default function ClickToHear({text, label}:{text:string; label:string}) {
  const [supported, setSupported] = useState(false);
  useEffect(()=> setSupported(typeof window !== 'undefined' && !!window.speechSynthesis), []);
  return (
    <button
      aria-label={`Read: ${label}`}
      onClick={()=> supported ? window.speechSynthesis.speak(Object.assign(new SpeechSynthesisUtterance(text),{lang:'en-US'})) : alert('TTS not supported')}
      className="rounded px-2 py-1 border"
    >
      🔊 Hear this
    </button>
  );
}


Use in Markdown via MDX: wrap sections of the patient card and inject <ClickToHear text={sectionText} label="What happened" />.

4) Markdown-First Workflows

Pure Markdown: render to HTML and post-process headings/paragraphs to insert buttons.

MDX: author content + components inline:

## What happened <ClickToHear text={whatHappened} label="What happened" />
{whatHappened}


Static sites (Docusaurus/Next/Eleventy): write a remark/rehype plugin that:

Finds headings/paragraphs.

Adds a button with data-tts referencing the node id.

Optionally expands [term](#glossary-term) to include a mini speaker icon for term audio.

5) Medical Quality & Pronunciation (SSML & Lexicons)

Prefer cloud TTS with SSML to pronounce terms (e.g., hydrosalpinx):

<speak>
  They found a <say-as interpret-as="spell-out">right</say-as> hydrosalpinx
  (<phoneme alphabet="ipa" ph="haɪˌdroʊˈsælpɪŋks">hydrosalpinx</phoneme>).
</speak>


Maintain a medical pronunciation dictionary (IPA or vendor lexicons) for recurring terms.

Use breaks & prosody to slow critical sentences for comprehension:

<prosody rate="90%">Your medical team will watch how you're healing.</prosody><break time="400ms"/>

6) Cloud TTS Architecture (Secure & Scalable)

Frontend

Buttons emit text + optional SSML key → your backend /tts.

Never expose cloud API keys client-side.

Backend

Auth (JWT/session), rate limiting, PHI-safe logs.

Cloud SDK call → returns audio stream (audio/mpeg), or store in object storage (S3/GCS/Azure Blob) with short-lived URLs.

Caching

Deterministic cache key = hash(voice|lang|text|ssml-version).

Store MP3/OGG; set Cache-Control, ETag for CDN.

Pre-generation (build step)

Collect blocks from Markdown (by id).

Generate audio assets; emit <audio src="..."> or attach URLs to buttons for instant playback.

Express example (pseudo):

app.post('/tts', requireAuth, async (req,res)=>{
  const {text, voice='en-US-JennyNeural', ssml=false} = req.body;
  const key = hash(text+voice+(ssml?'1':'0'));
  const cached = await store.get(key);
  if (cached) return stream(cached, res);

  const audio = await azureTTS({text, voice, ssml}); // or Google/Polly/ElevenLabs
  await store.put(key, audio, {contentType:'audio/mpeg'});
  stream(audio, res);
});

7) UX for the Patient Card (Referencing the Image)

Put a speaker button next to each heading (What happened, Next steps, What to expect) and one “Play all” at the top.

Show play/pause state (toggle icon, aria-pressed).

Offer speed (0.8×/1×/1.2×) and voice selector (if available).

Provide a transcript (already the card text) and a Download audio (optional).

For term tooltips (e.g., Fallopian tube), add a tiny speaker in the tooltip.

8) Selected-Text and Term-Level Playback
document.getElementById('read-selection').addEventListener('click', ()=>{
  const sel = window.getSelection()?.toString().trim();
  if (sel) speakText(sel);
});


For glossary terms, wrap with:

<button class="term" data-tts="hydrosalpinx definition">Hydrosalpinx 🔊</button>


and attach the same handler.

9) Testing & QA (Quality, Accessibility, Reliability)

Unit

Markdown parser → button injection (IDs stable).

SSML builder validates vendor schemas.

Cache key stability tests.

Integration

Backend returns audio ≤ acceptable latency; content type correct.

CORS, auth, rate-limit behavior.

E2E

Play, pause, stop, speed change across Chrome, Edge, Firefox, Safari iOS.

Keyboard: Tab focus buttons, Enter/Space triggers; visible focus ring.

Screen reader labels: each button has aria-label="Read: Section title".

Audio QA

Medical term list regression (IPA/lexicon) with snapshots.

Loudness normalization (−16 LUFS speech target); peak limiting.

Perf/Monitoring

Log TTS cache hit rate, average synth time, failures.

Synthetic checks for /tts health; CDN hit ratio.

10) Security, Privacy, Compliance

No PHI in logs; store only hashes/ids.

Transport encryption (TLS), at-rest encryption for cached audio.

Access control for pre-generated audio URLs (short-lived signed URLs if content is sensitive).

Vendor BAA (Azure/Google/AWS) if TTS processes PHI.

11) Feature Enhancements (Roadmap)

Word-level highlighting using vendor speech marks (Google/AWS) or forced alignment; highlight as words play.

Bilingual toggle (English/Spanish) with separate audio assets.

Reading mode: dim page, larger text, high contrast.

Offline support: pre-cache audio with Service Workers.

12) Quick Reference: When to Use What

Fast demo / internal tool: Web Speech API only.

Patient-facing production: Cloud TTS + SSML + pronunciation lexicon + caching (pre-gen for the three sections in the card).

Heavy traffic / low latency: pre-generate audio at build/publish; serve via CDN.

13) Drop-in Snippet (Play All for the Card)
<button id="playAll" aria-label="Read entire patient message">▶️ Play all</button>
<script>
const ids = ['p1','p2','p3'];
document.getElementById('playAll').addEventListener('click', async ()=>{
  if (!window.speechSynthesis) return alert('TTS not supported.');
  window.speechSynthesis.cancel();
  for (const id of ids) {
    const t = document.getElementById(id)?.innerText?.trim(); if (!t) continue;
    await new Promise(resolve=>{
      const u = new SpeechSynthesisUtterance(t);
      u.lang='en-US'; u.onend=resolve; window.speechSynthesis.speak(u);
    });
  }
});
</script>

14) Medical SSML Example (Cloud)
<speak>
  <p><prosody rate="92%">The doctor worked on the left side of your lower belly, carefully separating your intestine from scar tissue.</prosody></p>
  <p>Next, they found a <phoneme alphabet="ipa" ph="fəˈloʊpiən">Fallopian</phoneme> tube filled with fluid on your right side.
     They removed the <phoneme alphabet="ipa" ph="haɪˌdroʊˈsælpɪŋks">hydrosalpinx</phoneme> while protecting your ovary.</p>
  <p><prosody rate="92%">Your team will watch your healing, guide rest and diet, and discuss safe activities and pain control.</prosody></p>
</speak>

15) Medical SaaS 2nd Card Implementation
<div id="patient-card" aria-label="Patient-Friendly Version">
  <h2>What happened <button class="tts-btn" data-target="what-happened" aria-label="Read: What happened">🔊</button></h2>
  <p id="what-happened">The doctor worked on the left side of your lower belly, carefully separating your intestine from scar tissue that was stuck to your belly wall. They used special tools to cut and gently push the scar tissue away, plus a small electrical tool to safely remove it. Then they did the same thing on the right side.</p>
  
  <h2>Next steps <button class="tts-btn" data-target="next-steps" aria-label="Read: Next steps">🔊</button></h2>
  <p id="next-steps">Your medical team will watch how you're healing and tell you what to do. You'll need to rest and eat certain foods to help your body get better.</p>
  
  <h2>What to expect <button class="tts-btn" data-target="what-expect" aria-label="Read: What to expect">🔊</button></h2>
  <p id="what-expect">You might feel some pain as your body heals from the surgery. Your doctors will talk to you about ways to manage the pain and what activities are safe for you to do while you recover.</p>
  
  <button id="play-all" aria-label="Read entire patient message">▶️ Play All</button>
</div>

<script>
const synth = window.speechSynthesis;
let current;

function speak(t, {rate=0.9, pitch=1, lang='en-US'} = {}) {
  if (!synth) return alert('TTS not supported');
  if (synth.speaking) synth.cancel();
  const u = new SpeechSynthesisUtterance(t);
  u.rate = rate; u.pitch = pitch; u.lang = lang;
  current = u; synth.speak(u);
}

document.querySelectorAll('.tts-btn').forEach(btn => {
  btn.onclick = e => {
    const t = document.getElementById(btn.dataset.target)?.innerText?.trim();
    if (t) speak(t);
  };
});

document.getElementById('play-all').onclick = async () => {
  if (!synth) return alert('TTS not supported');
  synth.cancel();
  const ids = ['what-happened', 'next-steps', 'what-expect'];
  for (const id of ids) {
    const t = document.getElementById(id)?.innerText?.trim();
    if (!t) continue;
    await new Promise(resolve => {
      const u = new SpeechSynthesisUtterance(t);
      u.lang = 'en-US'; u.onend = resolve;
      synth.speak(u);
    });
  }
};
</script>

15) Acceptance Checklist (Go-Live)

 Buttons on each section + “Play all”

 Keyboard & screen-reader accessible (labels, focus)

 Works in Chrome/Edge/Firefox/Safari iOS

 Pronunciations validated for key medical terms

 Latency ≤ 300ms (pre-gen or cached) for card sections

 Logging free of PHI; error alerts wired

 Autoplay blocked unless user gesture; stop/pause available