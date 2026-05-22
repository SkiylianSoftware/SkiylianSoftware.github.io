---
layout: page
icon: "fa-solid fa-heart"
title: Support
order: 5
permalink: /support/
---

<div class="support-hero">
  <p>This whole operation runs on tea, chaos, and the kindness of folks like you. If my content brings you joy, there are a few ways to keep the trains running on time (and the tangents flowing).</p>
</div>

{% if site.data.fourthwall.total_orders %}
<div class="support-metrics">
  {% assign fw = site.data.fourthwall %}
  <div class="metric-card">
    <i class="fas fa-box"></i>
    <span class="metric-value">{{ fw.total_orders }}</span>
    <span class="metric-label">Merch orders</span>
  </div>
</div>
{% endif %}

<div class="support-grid">
  <a href="https://store.skiylia.dev" target="_blank" rel="noopener" class="support-card card-merch">
    <div class="card-icon"><i class="fas fa-tshirt"></i></div>
    <div class="card-body">
      <h3>Merch Store</h3>
      <p>T-shirts, hoodies, stickers, and more — powered by Fourthwall. Look good while supporting the channel.</p>
      <span class="card-cta">Browse the store &rarr;</span>
    </div>
  </a>

  <a href="https://www.youtube.com/@skiylia/join" target="_blank" rel="noopener" class="support-card card-yt">
    <div class="card-icon"><i class="fab fa-youtube"></i></div>
    <div class="card-body">
      <h3>YouTube Membership</h3>
      <p>Join the channel on YouTube for exclusive badges, emotes, and other perks. Your support goes directly into better content.</p>
      <span class="card-cta">Become a member &rarr;</span>
    </div>
  </a>

  <a href="https://ko-fi.com/skiylia" target="_blank" rel="noopener" class="support-card card-kofi">
    <div class="card-icon"><i class="fas fa-mug-hot"></i></div>
    <div class="card-body">
      <h3>Ko-fi</h3>
      <p>Buy me a tea! One-off donations with no subscription — perfect if you just want to say thanks after a video.</p>
      <span class="card-cta">Buy me a tea &rarr;</span>
    </div>
  </a>
</div>

<div class="support-why">
  <h2>What your support means</h2>
  <div class="why-grid">
    <div class="why-item">
      <i class="fas fa-microchip"></i>
      <h3>Better hardware</h3>
      <p>Upgrades to my PC and streaming setup mean better quality videos and streams for everyone.</p>
    </div>
    <div class="why-item">
      <i class="fas fa-gamepad"></i>
      <h3>More games</h3>
      <p>More games to explore means more variety in content — more trains, more automation, more chaos.</p>
    </div>
    <div class="why-item">
      <i class="fas fa-clock"></i>
      <h3>More time</h3>
      <p>Support lets me dedicate more hours to creating, editing, and streaming rather than juggling other work.</p>
    </div>
  </div>
</div>

<div class="support-note">
  <i class="fas fa-heart" style="color: #c084fc;"></i>
  <p>No matter how you choose to support — whether it's a membership, a Ko-fi, or just watching and sharing — I genuinely appreciate it. This little corner of the internet exists because of you.</p>
  <p class="support-signoff">&mdash; Skye</p>
</div>
