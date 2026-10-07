const form = document.querySelector('#lead-form');
const runButton = document.querySelector('#run-button');
const errorBox = document.querySelector('#form-error');
const statusBadge = document.querySelector('#status-badge');
const events = document.querySelector('#events');
let activeJob = null;

function status(text, kind) { statusBadge.textContent = text; statusBadge.className = `badge ${kind}`; }
function error(message) { errorBox.textContent = message; errorBox.hidden = false; status('ERROR', 'error'); runButton.disabled = false; }
function addEvent(item) {
  const li = document.createElement('li');
  li.className = item.type === 'waiting' ? 'waiting' : item.type === 'error' ? 'error' : '';
  const content = document.createElement('div');
  const title = document.createElement('strong');
  title.textContent = item.message || 'Agent step';
  content.append(title);
  if (item.type === 'tool') {
    const sub = document.createElement('div');
    sub.className = 'event-sub';
    const detail = item.tool === 'search_services' ? `Query: ${item.arguments?.query || ''}` : `Service: ${item.arguments?.service_id || ''}`;
    let outcome = item.ok ? 'completed' : 'failed';
    if (item.ok && item.tool === 'search_services') outcome = `Found: ${(item.result || []).map(service => service.name).join(', ') || 'no matches'}`;
    if (item.ok && item.tool === 'get_case_study') outcome = `Read: ${item.result?.title || 'case study'}`;
    sub.textContent = `${detail} · ${outcome}`;
    content.append(sub);
  }
  li.append(content);
  events.append(li);
  events.scrollTop = events.scrollHeight;
}
function fillList(selector, items) {
  const list = document.querySelector(selector);
  list.replaceChildren();
  for (const value of items || []) { const li = document.createElement('li'); li.textContent = value; list.append(li); }
}
function showResult(result) {
  document.querySelector('#result-view').hidden = false;
  document.querySelector('#recommendation').textContent = result.recommendation;
  document.querySelector('#confidence').textContent = `${result.confidence} confidence`;
  document.querySelector('#reason').textContent = result.reason;
  document.querySelector('#service').textContent = result.service_id ? `MATCHED SERVICE  ↗  ${result.service_id}` : 'No service matched';
  fillList('#evidence', result.evidence);
  fillList('#questions', result.questions);
  document.querySelector('#draft').textContent = result.draft_reply;
}
async function poll(jobId) {
  let shown = 0;
  let lastWait = '';
  while (activeJob === jobId) {
    try {
      const response = await fetch(`/api/jobs/${jobId}`, {cache: 'no-store'});
      const job = await response.json();
      if (!response.ok) throw new Error(job.error || 'Could not read agent progress');
      for (const item of job.events.slice(shown)) {
        if (item.type === 'waiting') {
          if (lastWait === item.message) continue;
          lastWait = item.message;
        }
        addEvent(item);
      }
      shown = job.events.length;
      document.querySelector('#activity-count').textContent = `${shown} STEPS`;
      if (job.status === 'complete') { showResult(job.result); status('COMPLETE', 'complete'); runButton.disabled = false; return; }
      if (job.status === 'error') { addEvent({type: 'error', message: job.error}); error(job.error); return; }
    } catch (exc) { error(exc.message); return; }
    await new Promise(resolve => setTimeout(resolve, 1800));
  }
}
form.addEventListener('submit', async event => {
  event.preventDefault();
  errorBox.hidden = true;
  runButton.disabled = true;
  status('RUNNING', 'running');
  document.querySelector('#empty-state').hidden = true;
  document.querySelector('#run-view').hidden = false;
  document.querySelector('#result-view').hidden = true;
  events.replaceChildren();
  const data = new FormData(form);
  const lead = {name: data.get('name').trim(), company: data.get('company').trim(), message: data.get('message').trim()};
  if (data.get('email').trim()) lead.email = data.get('email').trim();
  if (data.get('budget_inr')) lead.budget_inr = Number(data.get('budget_inr'));
  if (data.get('timeline_weeks')) lead.timeline_weeks = Number(data.get('timeline_weeks'));
  const api_key = data.get('api_key').trim() || null;
  try {
    const response = await fetch('/api/jobs', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({lead, api_key})});
    const body = await response.json();
    if (!response.ok) throw new Error(body.error || 'Could not start agent');
    activeJob = body.id;
    addEvent({message: 'Lead received. Starting Gemini agent…'});
    poll(body.id);
  } catch (exc) { error(exc.message); }
});
document.querySelector('#sample').addEventListener('click', () => {
  form.elements.name.value = 'Priya Shah';
  form.elements.company.value = 'BrightPath Academy';
  form.elements.email.value = 'priya@example.com';
  form.elements.message.value = 'We need a CRM for enquiries and WhatsApp follow-ups across two branches. We want to see every lead from first contact to admission.';
  form.elements.budget_inr.value = '250000';
  form.elements.timeline_weeks.value = '8';
});
document.querySelector('#copy').addEventListener('click', async event => {
  await navigator.clipboard.writeText(document.querySelector('#draft').textContent);
  event.target.textContent = 'Copied ✓';
  setTimeout(() => event.target.textContent = 'Copy draft ↗', 1800);
});
fetch('/api/config').then(response => response.json()).then(config => {
  document.querySelector('#model-name').textContent = config.model;
  if (config.key_configured) document.querySelector('#key-hint').textContent = 'A Gemini key is set in the server environment. You can leave this field empty.';
});
