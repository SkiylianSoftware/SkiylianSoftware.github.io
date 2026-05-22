---
layout: page
icon: "fa-solid fa-user"
title: About
order: 4
permalink: /about/
---

{% if site.data.site_meta.description %}
  <p class="about-intro">{{ site.data.site_meta.description }}</p>
{% endif %}

<div class="about-grid">
  <div class="about-section">
    <h2>Content</h2>
    <p>I play games that let me build, automate, and optimise things -- transport networks, space programs, factories, code. The channel is where engineering ambition meets cosy chaos.</p>
    <p>Current series span Transport Fever 2, modded Minecraft, Mars First Logistics, Kerbal Space Program, and various programming infrastructure projects.</p>
  </div>

  <div class="about-section">
    <h2>Links</h2>
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
  font-size: 1.05rem;
  line-height: 1.7;
  margin: 1.5rem 0;
  opacity: 0.9;
  max-width: 600px;
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
  transition: border-color 0.15s, color 0.15s;
}
.ql-item:hover { border-color: rgba(45, 212, 191, 0.3); color: #2dd4bf; }
.ql-item i { color: #c084fc; width: 1.2rem; text-align: center; }
</style>