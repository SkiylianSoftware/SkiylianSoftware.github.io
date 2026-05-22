---
layout: page
icon: "fa-solid fa-user"
title: About
order: 4
permalink: /about/
---

<p class="about-intro">Software engineer, automation enthusiast, train liker, and professional side-quest finder.</p>

<div class="about-grid">
  <div class="about-section">
    <h2>The Channel</h2>
    <p>The channel is where engineering ambition meets cosy chaos. I play games that let me build, automate, and optimise things -- transport networks, space programs, modded factories -- and spend just as much time talking about my coffee, visiting rail exhibitions, and getting distracted by my cat.</p>
    <p>New videos land on <strong>Saturdays</strong>, with occasional mid-week content when the mood strikes. Streams happen on <strong>Wednesdays</strong> and <strong>Saturdays</strong> over on <a href="https://live.skiylia.dev">Twitch</a>, usually around 7pm UK time.</p>
  </div>

  <div class="about-section">
    <h2>Current Series</h2>
    <ul class="series-list">
      <li><strong>Skiylian Transport</strong> &mdash; Transport Fever 2. Building the best public transport company in Normandie.</li>
      <li><strong>Astral Skiy</strong> &mdash; Modded Minecraft. Building a space station, one distraction at a time.</li>
      <li><strong>Skiylian Logistics</strong> &mdash; Mars First Logistics. Physics-based delivery mayhem with cute robots.</li>
      <li><strong>Automated Realism</strong> &mdash; KSP with Real Solar System. Writing KOS scripts to automate rockets.</li>
      <li><strong>Infrastructure Programming</strong> &mdash; Python automation tools for the YouTube pipeline.</li>
      <li><strong>Skiylian Stations</strong> &mdash; StationFlow. Because railway stations are fascinating.</li>
    </ul>
  </div>

  <div class="about-section">
    <h2>Setup</h2>
    <ul class="spec-list">
      <li><span class="spec-cat">CPU</span> AMD Ryzen 7</li>
      <li><span class="spec-cat">GPU</span> NVIDIA GeForce RTX</li>
      <li><span class="spec-cat">Mic</span> Rode NT-USB</li>
      <li><span class="spec-cat">Editor</span> Shotcut (open source!)</li>
      <li><span class="spec-cat">Code</span> VS Code, Python, Jekyll</li>
      <li><span class="spec-cat">Beverage</span> Mocha, always a mocha</li>
    </ul>
  </div>

  <div class="about-section">
    <h2>Quick Links</h2>
    <div class="quick-links">
      <a href="https://watch.skiylia.dev" class="ql-item"><i class="fab fa-youtube"></i> YouTube</a>
      <a href="https://live.skiylia.dev" class="ql-item"><i class="fab fa-twitch"></i> Twitch</a>
      <a href="https://code.skiylia.dev" class="ql-item"><i class="fab fa-github"></i> GitHub</a>
      <a href="https://store.skiylia.dev" class="ql-item"><i class="fas fa-store"></i> Merch</a>
      <a href="https://vods.skiylia.dev" class="ql-item"><i class="fab fa-youtube"></i> VODs</a>
      <a href="https://support.skiylia.dev" class="ql-item"><i class="fas fa-heart"></i> Support</a>
    </div>
  </div>
</div>

<style>
.about-intro {
  font-size: 1.1rem;
  line-height: 1.6;
  margin: 1.5rem 0 2rem;
  opacity: 0.85;
  font-style: italic;
}
.about-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin: 1.5rem 0;
}
@media (max-width: 640px) {
  .about-grid { grid-template-columns: 1fr; }
}
.about-section h2 {
  font-size: 1rem;
  margin: 0 0 0.75rem;
  border-bottom: 1px solid rgba(45, 212, 191, 0.1);
  padding-bottom: 0.3rem;
}
.about-section p {
  font-size: 0.9rem;
  line-height: 1.6;
  opacity: 0.85;
  margin: 0 0 0.5rem;
}
.series-list, .spec-list {
  padding-left: 0;
  list-style: none;
  margin: 0;
}
.series-list li, .spec-list li {
  font-size: 0.85rem;
  line-height: 1.5;
  margin: 0.4rem 0;
  opacity: 0.85;
}
.series-list li strong { color: #2dd4bf; }
.spec-cat {
  display: inline-block;
  color: #c084fc;
  font-weight: 500;
  min-width: 4em;
}
.quick-links {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.ql-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  background: rgba(13, 13, 30, 0.8);
  border: 1px solid rgba(45, 212, 191, 0.06);
  text-decoration: none;
  color: inherit;
  font-size: 0.85rem;
  transition: border-color 0.15s;
}
.ql-item:hover { border-color: rgba(45, 212, 191, 0.3); }
.ql-item i { color: #c084fc; width: 1.2rem; text-align: center; }
</style>