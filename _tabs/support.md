---
layout: page
icon: "fa-solid fa-heart"
title: Support
order: 5
permalink: /support/
---

<p>If you enjoy what I do, there are a few ways to support the channel:</p>

<div class="support-grid">
  <a href="https://store.skiylia.dev" target="_blank" class="support-card">
    <h3>Merch Store</h3>
    <p>T-shirts, hoodies, and more -- powered by Fourthwall.</p>
  </a>

  <a href="https://www.youtube.com/@skiylia/join" target="_blank" class="support-card">
    <h3>YouTube Membership</h3>
    <p>Join the channel for exclusive perks and badges.</p>
  </a>

  <a href="https://support.skiylia.dev" target="_blank" class="support-card">
    <h3>Ko-fi</h3>
    <p>Buy me a tea! One-off donations with no subscription.</p>
  </a>
</div>

<style>
.support-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.25rem;
  margin: 1.5rem 0;
}
.support-card {
  display: block;
  background: var(--card-bg, #1e1e1e);
  border-radius: 10px;
  padding: 1.5rem;
  text-decoration: none;
  transition: transform 0.15s, border-color 0.15s;
  border: 1px solid transparent;
}
.support-card:hover {
  transform: translateY(-3px);
  border-color: var(--link-color, #888);
}
.support-card h3 {
  margin: 0 0 0.5rem;
  font-size: 1.1rem;
}
.support-card p {
  margin: 0;
  font-size: 0.9rem;
  opacity: 0.8;
}
</style>