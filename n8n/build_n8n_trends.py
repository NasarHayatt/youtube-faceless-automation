import json, uuid

BASE = "http://host.docker.internal:8300"
GEMINI_CRED = {"googlePalmApi": {"id": "YOUR_GEMINI_CREDENTIAL_ID", "name": "Google Gemini(PaLM) Api account"}}
MODEL = "gemini-3.1-flash-lite"
GURL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

nodes, conns = [], {}


def add(name, typ, params, pos, ver=1, creds=None, extra=None):
    n = {"id": str(uuid.uuid4()), "name": name, "type": typ, "typeVersion": ver, "position": pos, "parameters": params}
    if creds:
        n["credentials"] = creds
    if extra:
        n.update(extra)
    nodes.append(n)
    return name


def link(a, b):
    b = FIRST.get(b, b)
    conns.setdefault(a, {"main": [[]]})
    conns[a]["main"][0].append({"node": b, "type": "main", "index": 0})


def code(name, js, pos):
    return add(name, "n8n-nodes-base.code", {"jsCode": js}, pos, 2)


FIRST = {}


def gemini(name, expr_prompt, pos):
    js = "const prompt = " + expr_prompt + ";\nreturn {json: {body: {contents: [{parts: [{text: prompt}]}], generationConfig: {responseMimeType: 'application/json', temperature: 0.5}}}};"
    pn = add(name + " (prompt)", "n8n-nodes-base.code", {"mode": "runOnceForEachItem", "jsCode": js}, [pos[0] - 120, pos[1] + 160], 2)
    http = add(name, "n8n-nodes-base.httpRequest", {
        "method": "POST", "url": GURL, "authentication": "predefinedCredentialType", "nodeCredentialType": "googlePalmApi",
        "sendBody": True, "specifyBody": "json", "jsonBody": "={{ JSON.stringify($json.body) }}", "options": {"timeout": 90000}},
        pos, 4.2, GEMINI_CRED, {"continueOnFail": True, "retryOnFail": True, "maxTries": 4, "waitBetweenTries": 10000})
    FIRST[http] = pn
    nodes_link(pn, http)
    return http


def nodes_link(a, b):
    conns.setdefault(a, {"main": [[]]})
    conns[a]["main"][0].append({"node": b, "type": "main", "index": 0})


UA = {"sendHeaders": True, "headerParameters": {"parameters": [{"name": "User-Agent", "value": "Mozilla/5.0 (compatible; TrendReader/1.0)"}]}}

t = add("Research trigger 01:00", "n8n-nodes-base.scheduleTrigger", {"rule": {"interval": [{"field": "cronExpression", "expression": "0 1 * * *"}]}}, [0, 0], 1.2)

niche = code("Pick niche", r"""
const niches = [
  {name:'technology', kids:false, brief:'technology, software, AI, gadgets, internet and how modern tech works'},
  {name:'kids learning', kids:true, brief:'fun, safe learning topics for children aged 6 to 12: animals, nature, space, human body, simple science, how things work'},
  {name:'science and nature', kids:false, brief:'science, nature, animals, earth, weather and the human body'},
  {name:'technology', kids:false, brief:'technology, software, AI, gadgets, internet and how modern tech works'},
  {name:'kids learning', kids:true, brief:'fun, safe learning topics for children aged 6 to 12: animals, nature, space, human body, simple science, how things work'},
  {name:'history and explained', kids:false, brief:'history, geography, culture and everyday things explained'},
  {name:'trending explained', kids:false, brief:'the most interesting factual topics people are curious about today'}
];
const d = new Date();
const n = niches[d.getDay()];
const y = new Date(d.getTime() - 86400000);
return [{json:{niche:n.name, kids:n.kids, brief:n.brief, date:d.toISOString().slice(0,10), y:y.getUTCFullYear(), m:String(y.getUTCMonth()+1).padStart(2,'0'), d:String(y.getUTCDate()).padStart(2,'0')}}];
""", [240, 0])

wiki = add("Wikipedia most read", "n8n-nodes-base.httpRequest", {
    "method": "GET", "url": "=https://en.wikipedia.org/api/rest_v1/feed/featured/{{ $json.y }}/{{ $json.m }}/{{ $json.d }}",
    "options": {"timeout": 30000}, **UA}, [480, -160], 4.2, extra={"continueOnFail": True})
hn = add("Hacker News front page", "n8n-nodes-base.httpRequest", {
    "method": "GET", "url": "https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=30", "options": {"timeout": 30000}, **UA}, [480, 0], 4.2, extra={"continueOnFail": True})
gt = add("Google Trends", "n8n-nodes-base.httpRequest", {
    "method": "GET", "url": "https://trends.google.com/trending/rss?geo=US", "options": {"timeout": 30000, "response": {"response": {"responseFormat": "text"}}}, **UA}, [480, 160], 4.2, extra={"continueOnFail": True})

cand = code("Build candidate list", r"""
const niche = $('Pick niche').first().json;
let wikiList = [];
try { wikiList = ($('Wikipedia most read').first().json.mostread.articles || []).slice(0,40).map(a => a.normalizedtitle || a.title); } catch(e) {}
let hnList = [];
try { hnList = ($('Hacker News front page').first().json.hits || []).map(h => h.title).slice(0,30); } catch(e) {}
let gtList = [];
try { const x = String($('Google Trends').first().json.data || $('Google Trends').first().json); gtList = [...x.matchAll(/<title>([^<]+)<\/title>/g)].map(m=>m[1]).slice(1,25); } catch(e) {}
const kidsPool = ['Octopus','Giant panda','Blue whale','Honey bee','Emperor penguin','Monarch butterfly','Elephant','Giraffe','Chameleon','Dolphin','Sloth','Koala','Kangaroo','Tyrannosaurus','Triceratops','Volcano','Rainbow','Thunderstorm','Tornado','Moon','Mars','Saturn','Jupiter','Solar System','Sun','Black hole','Milky Way','Human heart','Human brain','Skeleton','Tooth','Rainforest','Coral reef','Great Barrier Reef','Antarctica','Sahara','Mount Everest','Amazon River','Niagara Falls','Earthquake','Glacier','Tide','Aurora','Bat','Owl','Eagle','Hummingbird','Spider','Ant','Shark','Sea turtle','Seahorse','Jellyfish','Camel','Polar bear','Cheetah','Lion','Tiger','Gorilla','Rocket','Airplane','Train','Bicycle','Telescope','Magnet','Electricity','Gravity','Photosynthesis','Water cycle'];
const pool = kidsPool.sort(() => Math.random() - 0.5).slice(0, 15);
return [{json:{...niche, wikiList: niche.kids ? [] : wikiList, hnList: niche.kids ? [] : hnList, gtList: niche.kids ? [] : gtList, kidsPool: pool}}];
""", [720, 0])

pick = gemini("Gemini: choose 6 topics", r"""'You plan a daily educational YouTube channel. Today\'s niche is: ' + $json.niche + ' (' + $json.brief + ').\nCandidate trending items:\nWikipedia most read: ' + JSON.stringify($json.wikiList) + '\nTech news headlines: ' + JSON.stringify($json.hnList) + '\nGoogle Trends: ' + JSON.stringify($json.gtList) + '\n\nChoose exactly 6 DIFFERENT topics that fit the niche, are factual and safe for a general audience, and each has an English Wikipedia article. Prefer trending items when they fit; otherwise choose evergreen topics of high interest. Avoid: politics, elections, war, violence, crime, tragedies, deaths, celebrity gossip, medical advice, adult content, living private people. ' + ($json.kids ? 'This is for children aged 6 to 12. Choose ONLY from this evergreen list of kid-friendly topics: ' + JSON.stringify($json.kidsPool) + '. Never choose anything else. ' : '') + 'Return JSON only: {"topics":[{"wikipedia_title":"exact English Wikipedia article title","angle":"one sentence on the most interesting angle","format":"wide"|"short"}]} with 3 wide and 3 short.'""", [960, 0])

parse = code("Split topics", r"""
const niche = $('Build candidate list').first().json;
const txt = $input.first().json.candidates[0].content.parts.map(p=>p.text||'').join('');
let topics = [];
try { topics = JSON.parse(txt).topics || []; } catch(e) {}
return topics.slice(0,6).map((t,i) => ({json:{...t, idx:i, niche:niche.niche, kids:niche.kids, date:niche.date}}));
""", [1200, 0])

ext = add("Wikipedia extract", "n8n-nodes-base.httpRequest", {
    "method": "GET", "url": "=https://en.wikipedia.org/w/api.php?action=query&prop=extracts&explaintext=1&exchars=4000&redirects=1&format=json&titles={{ encodeURIComponent($json.wikipedia_title) }}",
    "options": {"timeout": 30000}, **UA}, [1440, 0], 4.2, extra={"continueOnFail": True})

prep = code("Attach extract", r"""
const tops = $('Split topics').all();
return $input.all().map((it, i) => {
  let text = '';
  try { text = Object.values(it.json.query.pages)[0].extract || ''; } catch(e) {}
  return {json: {...tops[i].json, extract: text}};
});
""", [1680, 0])

script = gemini("Gemini: write script", r"""'Write a script for a faceless educational YouTube video using ONLY facts stated in the SOURCE TEXT below. Topic: ' + $json.wikipedia_title + '. Angle: ' + $json.angle + '. Niche: ' + $json.niche + '. Format: ' + ($json.format === 'wide' ? 'horizontal video, 7 scenes, about 35 seconds total (each voice-over line 12 to 18 words)' : 'vertical Short, 4 scenes, about 25 seconds total (each voice-over line 12 to 18 words)') + '. ' + ($json.kids ? 'Audience: children aged 6 to 12. Use simple friendly words, a fun tone, no scary content. ' : 'Audience: curious general viewers. ') + '\n\nRules: every fact must be supported by a sentence in SOURCE TEXT. Scene 1 is a strong hook. The last scene is a short call to subscribe to the channel. Write numbers as words inside "vo" (for speech) but use digits in "big". "big" is one short striking number or word (max 10 characters) or empty. "label" is 2 to 5 words explaining big. "sub" is a short caption (max 8 words). "image_prompt" describes a vivid, safe, realistic illustration for the scene with no text and no real people. "evidence" is an EXACT sentence copied from SOURCE TEXT that supports the scene, or empty for the hook and the subscribe scene. "numbers" lists every number used in that scene (in vo or big) written as digits exactly as they appear in the evidence sentence, for example ["29","75"], or an empty list if none. Never use a number that is not in the evidence.\nReturn JSON only: {"title":"under 70 characters, engaging, no clickbait lies","description":"2 sentences","tags":["5 short tags"],"scenes":[{"vo":"","big":"","label":"","sub":"","image_prompt":"","evidence":"","numbers":[]}]}\n\nSOURCE TEXT:\n' + $json.extract""", [1920, 0])

build = code("Validate and build spec", r"""
const atts = $('Attach extract').all();
const results = [];
$input.all().forEach((inp, idx) => {
const t = atts[idx].json;
const src = (t.extract || '').toLowerCase().replace(/\s+/g,' ');
let s = {};
try { s = JSON.parse(inp.json.candidates[0].content.parts.map(p=>p.text||'').join('')); } catch(e) { return; }
const scenes = (s.scenes || []);
const wide = t.format === 'wide';
const bad = /(kill|murder|suicide|nude|sex|porn|terror|massacre)/i;
let verified = 0, factual = 0;
const out = [];
const palette = [[255,210,90],[120,200,255],[255,150,150],[110,220,160],[200,150,255],[255,170,60],[255,110,110]];
scenes.forEach((sc, i) => {
  if (bad.test(sc.vo || '')) return;
  const ev = (sc.evidence || '').toLowerCase().replace(/\s+/g,' ').trim();
  const isFact = ev.length > 0;
  if (isFact) {
    factual++;
    if (!src.includes(ev.slice(0, 80))) return;
    const nums = (sc.numbers || []).map(x => String(x).replace(/,/g,''));
    const evn = ev.replace(/,/g,'');
    if (nums.some(x => !evn.includes(x))) return;
    const bigd = (sc.big || '').replace(/[^0-9.]/g,'');
    if (bigd && !evn.includes(bigd)) return;
    verified++;
  }
  out.push({vo: sc.vo, bg: {type:'ai_api', prompt: sc.image_prompt || t.wikipedia_title, c1:[10,8,40], c2:[60,25,100]}, big: (sc.big||'').slice(0,10), label: sc.label||'', sub: sc.sub||'', color: palette[i % palette.length]});
});
const minScenes = wide ? 5 : 3;
if (out.length < minScenes || verified < 2 || !s.title) return;
const slug = t.date + '-' + (wide ? 'v' : 's') + t.idx + '-' + t.wikipedia_title.toLowerCase().replace(/[^a-z0-9]+/g,'-').slice(0,40);
const tags = (s.tags || []).map(x => String(x).replace(/[^a-zA-Z0-9]/g,'')).filter(Boolean).slice(0,5);
const desc = (s.description || '') + '\n\nSource: Wikipedia, article "' + t.wikipedia_title + '" (CC BY-SA). Images and narration were generated with AI. Facts were checked against the source text but may be simplified.\n\n' + tags.map(x => '#' + x).join(' ') + (wide ? '' : ' #shorts');
const spec = {slug, title: String(s.title).slice(0,95), description: desc, scenes: out, kind: wide ? 'video' : 'short', made_for_kids: !!t.kids, niche: t.niche};
if (wide) spec.format = 'wide';
results.push({json: spec});
});
return results;
""", [2160, 0])

post = add("Add to render queue", "n8n-nodes-base.httpRequest", {
    "method": "POST", "url": BASE + "/queue", "sendBody": True, "specifyBody": "json", "jsonBody": "={{ JSON.stringify($json) }}", "options": {"timeout": 30000}}, [2400, 0], 4.2)

tt = add("Manual test trigger", "n8n-nodes-base.executeWorkflowTrigger", {}, [0, 200], 1)
link(t, niche)
link(tt, niche)
link(niche, wiki)
link(wiki, hn)
link(hn, gt)
link(gt, cand)
link(cand, pick)
link(pick, parse)
link(parse, ext)
link(ext, prep)
link(prep, script)
link(script, build)
link(build, post)

wf = {"name": "Daily trends and scripts", "nodes": nodes, "connections": conns, "settings": {"executionOrder": "v1"}, "active": False, "id": "ytdailytrends0001"}
json.dump([wf], open("youtube-trends-scripts.json", "w", encoding="utf-8"), indent=1)
print("trend workflow written")
