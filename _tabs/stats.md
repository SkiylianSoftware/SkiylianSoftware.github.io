---
layout: page
icon: "fa-solid fa-chart-simple"
title: Stats
order: 7
permalink: /stats/
---

{% assign meta = site.data.site_meta %}

<div class="stats-grid">
  <div class="stat-card accent-turquoise">
    <span class="stat-value">{{ meta.subscriber_count }}</span>
    <span class="stat-label">YouTube Subscribers</span>
  </div>
  <div class="stat-card accent-purple">
    <span class="stat-value">{{ meta.view_count }}</span>
    <span class="stat-label">Total Views</span>
  </div>
  <div class="stat-card accent-turquoise">
    <span class="stat-value">{{ meta.video_count }}</span>
    <span class="stat-label">Videos Uploaded</span>
  </div>
  <div class="stat-card accent-purple">
    <span class="stat-value">{{ meta.published_at | truncate: 4, "" }}</span>
    <span class="stat-label">Channel Since</span>
  </div>
</div>

{% if meta.published_at %}
  {% assign now_epoch = site.time | date: "%s" | plus: 0 %}
  {% assign chan_epoch = meta.published_at | date: "%s" | plus: 0 %}
  {% assign channel_age_seconds = now_epoch | minus: chan_epoch %}
  {% assign channel_age_days = channel_age_seconds | divided_by: 86400 %}
  {% assign channel_age_years = channel_age_days | divided_by: 365 %}
  <div class="insight-box">
    <p>Channel has been going for <strong>{{ channel_age_years }} years</strong> ({{ channel_age_days }} days).</p>
    {% if meta.video_count and channel_age_days > 0 %}
      {% assign vpm = meta.video_count | times: 30.0 | divided_by: channel_age_days | round: 1 %}
      <p>That's roughly <strong>{{ vpm }} videos per month</strong>.</p>
    {% endif %}
  </div>
{% endif %}

{% assign videos = site.data.youtube_main.videos %}
{% if videos.size > 0 %}
  {% assign total_watch_seconds = 0 %}
  {% assign total_views = 0 %}
  {% for v in videos %}
    {% assign total_watch_seconds = total_watch_seconds | plus: v.duration_seconds %}
    {% assign total_views = total_views | plus: v.view_count %}
  {% endfor %}
  {% assign total_watch_hours = total_watch_seconds | divided_by: 3600 %}
  {% assign most_viewed = videos | sort: "view_count" | last %}

  <h2 class="stats-subtitle">Content Breakdown</h2>
  <div class="stats-grid">
    <div class="stat-card accent-turquoise">
      <span class="stat-value">{{ total_watch_hours }}h</span>
      <span class="stat-label">Total Content Published</span>
    </div>
    <div class="stat-card accent-purple">
      <span class="stat-value">{{ total_views }}</span>
      <span class="stat-label">All-time Video Views</span>
    </div>
    {% if most_viewed %}
      <div class="stat-card wide">
        <span class="stat-label">Most Viewed</span>
        <span class="stat-most-title">{{ most_viewed.title }}</span>
        <span class="stat-value-sm">{{ most_viewed.view_count }} views</span>
      </div>
    {% endif %}
  </div>
{% endif %}

<div class="insight-box">
  <h3>Twitch</h3>
  {% if site.data.twitch_stats %}
    <p>Followers: <strong>{{ site.data.twitch_stats.follower_count | default: "?" }}</strong></p>
  {% else %}
    <p>Twitch stats not available yet. Follow at <a href="https://live.skiylia.dev">live.skiylia.dev</a>.</p>
  {% endif %}
</div>

{% assign vods = site.data.youtube_vods.videos %}
{% if vods.size > 0 %}
  <h2 class="stats-subtitle">VODs Channel</h2>
  <div class="stats-grid">
    <div class="stat-card accent-turquoise">
      <span class="stat-value">{{ vods.size }}</span>
      <span class="stat-label">Stream Archives</span>
    </div>
  </div>
{% endif %}

{% assign gh = site.data.github %}
{% if gh %}
  <h2 class="stats-subtitle">GitHub</h2>
  <div class="stats-grid">
    <div class="stat-card accent-turquoise">
      <span class="stat-value">{{ gh.public_repos }}</span>
      <span class="stat-label">Public Repos</span>
    </div>
    <div class="stat-card accent-purple">
      <span class="stat-value">{{ gh.total_stars }}</span>
      <span class="stat-label">Total Stars</span>
    </div>
    <div class="stat-card accent-turquoise">
      <span class="stat-value">{{ gh.total_forks }}</span>
      <span class="stat-label">Forks</span>
    </div>
  </div>
{% endif %}

<style>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 1rem;
  margin: 1.5rem 0;
}
.stat-card {
  background: var(--card-bg, #1e1e1e);
  border-radius: 10px;
  padding: 1.25rem;
  text-align: center;
  border: 1px solid rgba(45,212,191,0.1);
}
.stat-card.accent-purple { border-color: rgba(192,132,252,0.15); }
.stat-card.wide { grid-column: 1 / -1; }
.stat-value {
  display: block;
  font-size: 1.75rem;
  font-weight: 700;
  color: #2dd4bf;
  line-height: 1.2;
}
.accent-purple .stat-value { color: #c084fc; }
.stat-value-sm {
  display: block;
  font-size: 1.1rem;
  font-weight: 600;
  color: #2dd4bf;
  margin-top: 0.25rem;
}
.stat-label {
  display: block;
  font-size: 0.8rem;
  opacity: 0.65;
  margin-top: 0.25rem;
}
.stat-most-title {
  display: block;
  font-size: 0.85rem;
  margin-top: 0.3rem;
  opacity: 0.8;
}
.stats-subtitle {
  margin: 1.5rem 0 0.5rem;
  font-size: 1rem;
  border-bottom: 1px solid var(--border-color, #333);
  padding-bottom: 0.3rem;
}
.insight-box {
  background: var(--card-bg, #1e1e1e);
  border: 1px solid rgba(45,212,191,0.1);
  border-radius: 10px;
  padding: 1.25rem;
  margin: 1rem 0;
  font-size: 0.9rem;
}
.insight-box h3 { margin: 0 0 0.5rem; font-size: 1rem; }
.insight-box p { margin: 0.3rem 0; }

.repo-list {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  margin: 0.5rem 0 1rem;
}
.repo-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0.75rem;
  background: var(--card-bg, #1e1e1e);
  border: 1px solid rgba(45,212,191,0.08);
  border-radius: 8px;
  text-decoration: none;
  color: inherit;
  font-size: 0.85rem;
  transition: border-color 0.15s;
}
.repo-item:hover {
  border-color: rgba(45,212,191,0.3);
}
.repo-name { font-weight: 500; }
.repo-meta { font-size: 0.8rem; opacity: 0.65; }
</style>