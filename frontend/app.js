const API_URL = 'https://pitchforge-backend-632605595642.us-central1.run.app';

function setStep(stepId, state) {
  const el = document.getElementById('step-' + stepId);
  if (!el) return;
  el.className = 'step-pill ' + state;
  const dot = el.querySelector('.dot');
  if (state === 'active') dot.classList.add('pulse');
  else dot.classList.remove('pulse');
}

function copyToClipboard(text, btn) {
  navigator.clipboard.writeText(text).then(() => {
    const orig = btn.textContent;
    btn.textContent = 'Copied!';
    setTimeout(() => btn.textContent = orig, 2000);
  });
}

async function generateCampaign() {
  const description = document.getElementById('description').value.trim();
  const language = document.getElementById('language').value;

  if (description.length < 10) {
    document.getElementById('description').style.borderColor = '#E8477A';
    document.getElementById('description').focus();
    return;
  }
  document.getElementById('description').style.borderColor = '';

  const btn = document.getElementById('generateBtn');
  const spinner = document.getElementById('spinner');
  const btnText = document.getElementById('btnText');

  btn.disabled = true;
  spinner.style.display = 'block';
  btnText.textContent = 'Creating your campaign...';

  document.getElementById('progressWrap').style.display = 'block';
  document.getElementById('results').style.display = 'block';

  // Hide all result sections
  ['taglineSection','copySection','headlinesSection','imagesSection',
   'scriptSection','audioSection','socialSection','hashtagsSection'].forEach(id => {
    document.getElementById(id).style.display = 'none';
  });

  // Reset images
  document.getElementById('heroImageCard').innerHTML = '<div class="placeholder-img">✦</div>';
  document.getElementById('socialImageCard').innerHTML = '<div class="placeholder-img">✦</div>';

  setStep('thinking', 'active');
  setStep('copy', '');
  setStep('images', '');
  setStep('video', '');
  setStep('social', '');

  const fullDescription = language !== 'English'
    ? `${description}\n\n[Generate ALL campaign content — tagline, copy, headlines, video script, and social media posts — entirely in ${language}. Do not mix languages.]`
    : description;

  try {
    const resp = await fetch(`${API_URL}/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description: fullDescription })
    });

    const reader = resp.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop();

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        try {
          const event = JSON.parse(line.slice(6));
          handleEvent(event);
        } catch (e) {}
      }
    }
  } catch (err) {
    console.error(err);
  }

  btn.disabled = false;
  spinner.style.display = 'none';
  btnText.textContent = '✦ Generate Campaign';
  setStep('thinking', 'done');
}

function handleEvent(event) {
  const { type, key, content } = event;

  if (type === 'status') {
    if (key === 'thinking') { setStep('thinking', 'active'); }
    if (key === 'copy_done') { setStep('thinking', 'done'); setStep('copy', 'done'); setStep('images', 'active'); }
    if (key === 'images_done') { setStep('images', 'done'); setStep('video', 'active'); }
    if (key === 'video_done') { setStep('video', 'done'); setStep('social', 'active'); }
    if (key === 'social_done') { setStep('social', 'done'); }
    return;
  }

  if (type === 'text' && key === 'tagline' && content) {
    document.getElementById('taglineText').textContent = content;
    document.getElementById('taglineSection').style.display = 'block';
  }

  if (type === 'text' && key === 'hero_copy' && content) {
    document.getElementById('heroCopyText').textContent = content;
    document.getElementById('copySection').style.display = 'block';
  }

  if (type === 'text' && key === 'headlines' && content && content.length) {
    const grid = document.getElementById('headlinesGrid');
    grid.innerHTML = '';
    content.forEach(h => {
      const d = document.createElement('div');
      d.className = 'headline-pill';
      d.textContent = h;
      grid.appendChild(d);
    });
    document.getElementById('headlinesSection').style.display = 'block';
  }

  if (type === 'image' && key === 'hero_image' && content) {
    document.getElementById('heroImageCard').innerHTML = `<img src="${content}" alt="Hero campaign image">`;
    document.getElementById('imagesSection').style.display = 'block';
  }

  if (type === 'image' && key === 'social_image' && content) {
    document.getElementById('socialImageCard').innerHTML = `<img src="${content}" alt="Social media image">`;
    document.getElementById('imagesSection').style.display = 'block';
  }

  if (type === 'text' && key === 'script' && content && content.scenes) {
    const list = document.getElementById('scenesList');
    list.innerHTML = '';
    content.scenes.forEach((scene, i) => {
      list.innerHTML += `
        <div class="scene-item">
          <div class="scene-num">${i + 1}</div>
          <div class="scene-content">
            <div class="scene-visual">${scene.scene}</div>
            <div class="scene-vo">"${scene.vo}"</div>
            <div class="scene-duration">${scene.duration}s</div>
          </div>
        </div>`;
    });
    document.getElementById('scriptSection').style.display = 'block';
  }

  if (type === 'audio' && key === 'voiceover' && content) {
    const audio = document.getElementById('audioPlayer');
    audio.src = content;
    document.getElementById('audioSection').style.display = 'block';
  }

  if (type === 'text' && key === 'social' && content) {
    const grid = document.getElementById('socialGrid');
    grid.innerHTML = '';

    const platforms = [
      { id: 'instagram', label: 'Instagram', badge: 'platform-ig', icon: '📸' },
      { id: 'twitter', label: 'X (Twitter)', badge: 'platform-tw', icon: '✦' },
      { id: 'linkedin', label: 'LinkedIn', badge: 'platform-li', icon: '💼', full: true },
    ];

    platforms.forEach(p => {
      const text = content[p.id];
      if (!text) return;
      const div = document.createElement('div');
      div.className = `social-post-card${p.full ? ' full-width' : ''}`;
      div.innerHTML = `
        <div class="social-platform">
          <span class="platform-badge ${p.badge}">${p.icon} ${p.label}</span>
        </div>
        <p class="social-text">${text}</p>
        <button class="copy-btn" onclick="copyToClipboard(${JSON.stringify(text)}, this)">Copy</button>`;
      grid.appendChild(div);
    });

    document.getElementById('socialSection').style.display = 'block';

    if (content.hashtags && content.hashtags.length) {
      const hc = document.getElementById('hashtagsCard');
      hc.innerHTML = content.hashtags.map(h => `<span class="hashtag">#${h}</span>`).join('');
      document.getElementById('hashtagsSection').style.display = 'block';
    }
  }

  if (type === 'error') {
    console.error('Campaign error:', content);
  }
}

document.getElementById('description').addEventListener('keydown', function(e) {
  if (e.key === 'Enter' && e.ctrlKey) generateCampaign();
});