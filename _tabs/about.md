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

{% if site.data.pc_parts.display.size > 0 %}
<div class="about-section">
  <h2>PC Setup</h2>
  <div class="pc-parts">
    {% for part in site.data.pc_parts.display %}
    <div class="part-row">
      <span class="part-component">{{ part.component }}</span>
      <span class="part-name">{% if part.url %}<a href="{{ part.url }}" target="_blank" rel="noopener">{{ part.name }}</a>{% else %}{{ part.name }}{% endif %}</span>
    </div>
    {% endfor %}
  </div>
  <p class="parts-attribution">Auto-updated from <a href="{{ site.data.pc_parts.list_url }}" target="_blank" rel="noopener">PCPartPicker</a></p>
</div>
{% endif %}
