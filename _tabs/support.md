---
layout: page
icon: "fa-solid fa-heart"
title: Support
order: 8
permalink: /support/
---

<div class="support-hero">
  <p>This whole operation runs on tea, chaos, and the kindness of folks like you. If my content brings you joy, there are a few ways to keep the trains running on time (and the tangents flowing).</p>
</div>

{% if site.data.fourthwall.total_orders or site.data.twitch_stats.follower_count %}
<div class="support-metrics">
  {% assign fw = site.data.fourthwall %}
  {% if fw.total_orders %}
  <div class="metric-card">
    <i class="fas fa-box"></i>
    <span class="metric-value">{{ fw.total_orders }}</span>
    <span class="metric-label">Merch orders</span>
  </div>
  {% endif %}
  {% assign twitch = site.data.twitch_stats %}
  {% if twitch.follower_count and twitch.follower_count > 0 %}
  <div class="metric-card">
    <i class="fab fa-twitch"></i>
    <span class="metric-value">{{ twitch.follower_count }}</span>
    <span class="metric-label">Twitch followers</span>
  </div>
  {% endif %}
</div>
{% endif %}

<div class="support-grid">
  <a href="https://store.skiylia.dev" target="_blank" rel="noopener" class="support-card card-merch btn">
    <div class="card-icon"><i class="fas fa-tshirt"></i></div>
    <div class="card-body">
      <h3>Merch Store</h3>
      <p>{% if site.data.fourthwall.products.size > 0 %}Featuring {% for p in site.data.fourthwall.products limit:3 %}{{ p.name }}{% unless forloop.last %}, {% endunless %}{% endfor %} and more;{% else %}Cool merch;{% endif %} powered by Fourthwall.</p>
      <span class="card-cta">Browse the store &rarr;</span>
    </div>
  </a>

  <a href="https://support.skiylia.dev" target="_blank" rel="noopener" class="support-card card-kofi btn">
    <div class="card-icon"><i class="fas fa-mug-hot"></i></div>
    <div class="card-body">
      <h3>Ko-fi</h3>
      <p>Buy me a tea! One-off donations with no subscription; perfect if you just want to say thanks after a video.</p>
      <span class="card-cta">Buy me a tea &rarr;</span>
    </div>
  </a>

  {% assign yt_memberships = site.data.site_meta.memberships_available | default: false %}
  {% if yt_memberships %}
  <a href="https://www.youtube.com/@skiylia/join" target="_blank" rel="noopener" class="support-card card-yt btn">
    <div class="card-icon"><i class="fab fa-youtube"></i></div>
    <div class="card-body">
      <h3>YouTube Membership</h3>
      <p>Join the channel on YouTube for exclusive badges, emotes, and other perks. Your support goes directly into better content.</p>
      <span class="card-cta">Become a member &rarr;</span>
    </div>
  </a>
  {% endif %}

  {% assign bt = site.data.twitch_stats.broadcaster_type | default: "" %}
  {% if bt == "affiliate" or bt == "partner" %}
  <a href="https://www.twitch.tv/subs/skiylia" target="_blank" rel="noopener" class="support-card card-twitch btn">
    <div class="card-icon"><i class="fab fa-twitch"></i></div>
    <div class="card-body">
      <h3>Twitch Subscription</h3>
      <p>Subscribe on Twitch for ad-free viewing, custom emotes, and badge perks during live streams.</p>
      <span class="card-cta">Subscribe &rarr;</span>
    </div>
  </a>
  {% endif %}
</div>

<div class="support-free">
  <h2>Free ways to support</h2>
  <div class="free-grid">
    <a href="https://www.youtube.com/@skiylia?sub_confirmation=1" target="_blank" rel="noopener" class="free-card btn">
      <i class="fab fa-youtube" style="color: #ff4444;"></i>
      <div>
        <strong>Subscribe on YouTube</strong>
        <span>Hit subscribe and ring the bell; it helps more than you'd think.</span>
      </div>
    </a>
    <a href="https://live.skiylia.dev" target="_blank" rel="noopener" class="free-card btn">
      <i class="fab fa-twitch" style="color: #a970ff;"></i>
      <div>
        <strong>Follow on Twitch</strong>
        <span>Follow for free and get notified when I go live.</span>
      </div>
    </a>
  </div>
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
      <p>More games to explore means more variety in content; more trains, more automation, more chaos.</p>
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
  <div>
    <p>No matter how you choose to support; whether it's a membership, a Ko-fi, or just watching and sharing; I genuinely appreciate it. This little corner of the internet exists because of you.</p>
    <p class="support-signoff">- Skye</p>
  </div>
</div>
