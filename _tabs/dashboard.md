---
layout: page
icon: "fa-solid fa-chart-simple"
title: Dashboard
order: 7
permalink: /dashboard/
group: stats
---

{% assign meta = site.data.site_meta %}
{% assign videos = site.data.youtube_main.videos %}
{% assign vods_list = site.data.youtube_vods.videos %}
{% assign twitch = site.data.twitch_stats %}
{% assign gh = site.data.github %}
{% assign store = site.data.fourthwall %}

{% assign has_vods = false %}
{% if vods_list.size > 0 or meta.vods_subscriber_count %}{% assign has_vods = true %}{% endif %}

<!-- Combined Overview -->
<h2 class="stats-subtitle">Overview</h2>
{% assign yt_subs = meta.subscriber_count | default: 0 %}
{% assign vods_subs = meta.vods_subscriber_count | default: 0 %}
{% assign twitch_followers = twitch.follower_count | default: 0 %}
{% assign total_audience = yt_subs | plus: vods_subs | plus: twitch_followers %}
{% assign yt_views = meta.view_count | default: 0 %}
{% assign vods_views = meta.vods_view_count | default: 0 %}
{% assign twitch_views = twitch.view_count | default: 0 %}
{% assign total_views_all = yt_views | plus: vods_views | plus: twitch_views %}
{% assign yt_vids = meta.video_count | default: 0 %}
{% assign vods_vids = vods_list.size %}
{% assign total_vids = yt_vids | plus: vods_vids %}
<div class="stats-grid">
  <div class="stat-card">
    <span class="stat-value">{{ total_audience }}</span>
    <span class="stat-label">Total Audience</span>
  </div>
  <div class="stat-card accent-purple">
    <span class="stat-value">{{ total_views_all }}</span>
    <span class="stat-label">Total Views</span>
  </div>
  <div class="stat-card accent-purple">
    <span class="stat-value">{{ meta.subscriber_count }}</span>
    <span class="stat-label">YouTube Subs</span>
  </div>
  <div class="stat-card">
    <span class="stat-value">{{ meta.view_count }}</span>
    <span class="stat-label">YouTube Views</span>
  </div>
  <div class="stat-card accent-purple">
    <span class="stat-value">{{ twitch.follower_count | default: "?" }}</span>
    <span class="stat-label">Twitch Followers</span>
  </div>
  {% if store.total_orders %}
  <div class="stat-card">
    <span class="stat-value">{{ store.total_orders }}</span>
    <span class="stat-label">Store Orders</span>
  </div>
  {% endif %}
</div>

<!-- YouTube -->
{% if videos.size > 0 %}
  {% assign total_watch_seconds = 0 %}
  {% assign total_video_views = 0 %}
  {% assign total_likes = 0 %}
  {% for v in videos %}
    {% assign total_watch_seconds = total_watch_seconds | plus: v.duration_seconds %}
    {% assign total_video_views = total_video_views | plus: v.view_count %}
    {% assign total_likes = total_likes | plus: v.like_count %}
  {% endfor %}
  {% assign total_watch_hours = total_watch_seconds | divided_by: 3600 %}
  {% assign most_viewed = videos | sort: "view_count" | last %}
  {% assign most_liked = videos | sort: "like_count" | last %}
  {% assign avg_views = total_video_views | divided_by: videos.size %}

  <h2 class="stats-subtitle">YouTube</h2>
  <div class="stats-grid">
    <div class="stat-card">
      <span class="stat-value">{{ meta.video_count }}</span>
      <span class="stat-label">Videos</span>
    </div>
    <div class="stat-card accent-purple">
      <span class="stat-value">{{ total_watch_hours }}h</span>
      <span class="stat-label">Total Runtime</span>
    </div>
    <div class="stat-card accent-purple">
      <span class="stat-value">{{ total_video_views }}</span>
      <span class="stat-label">Video Views</span>
    </div>
    <div class="stat-card">
      <span class="stat-value">{{ total_likes }}</span>
      <span class="stat-label">Likes</span>
    </div>
    <div class="stat-card accent-purple">
      <span class="stat-value">{{ avg_views }}</span>
      <span class="stat-label">Avg Views/Video</span>
    </div>
    <div class="stat-card">
      <span class="stat-value">{{ yt_age_years }}y</span>
      <span class="stat-label">Content Age</span>
    </div>
    {% if yt_age_days and yt_age_days > 0 %}
    {% assign vpm = meta.video_count | times: 30.0 | divided_by: yt_age_days | round: 1 %}
    <div class="stat-card accent-purple">
      <span class="stat-value">{{ vpm }}</span>
      <span class="stat-label">Videos/Month</span>
    </div>
    {% endif %}
    <div class="stat-card">
      <span class="stat-value">{{ yt_start | date: "%Y" }}</span>
      <span class="stat-label">First Video</span>
    </div>
  </div>

  <div class="stats-grid-two">
    {% if most_viewed %}
    <div class="stat-card wide">
      <span class="stat-label">Most Viewed</span>
      <span class="stat-most-title">{{ most_viewed.title }}</span>
      <span class="stat-value-sm">{{ most_viewed.view_count }} views</span>
    </div>
    {% endif %}
    {% if most_liked and most_liked.like_count > 0 %}
    <div class="stat-card wide accent-purple">
      <span class="stat-label">Most Liked</span>
      <span class="stat-most-title">{{ most_liked.title }}</span>
      <span class="stat-value-sm">{{ most_liked.like_count }} likes</span>
    </div>
    {% endif %}
  </div>
{% endif %}

<!-- YouTube VODs -->
{% if has_vods %}
  <h2 class="stats-subtitle">YouTube VODs</h2>
  <div class="stats-grid">
    <div class="stat-card">
      <span class="stat-value">{{ meta.vods_subscriber_count | default: "?" }}</span>
      <span class="stat-label">Subscribers</span>
    </div>
    <div class="stat-card accent-purple">
      <span class="stat-value">{{ meta.vods_view_count | default: "?" }}</span>
      <span class="stat-label">Views</span>
    </div>
    <div class="stat-card">
      <span class="stat-value">{{ vods_list.size }}</span>
      <span class="stat-label">Archives</span>
    </div>
    {% if meta.vods_published_at %}
    <div class="stat-card accent-purple">
      <span class="stat-value">{{ meta.vods_published_at | truncate: 4, "" }}</span>
      <span class="stat-label">Since</span>
    </div>
    {% endif %}
  </div>
{% endif %}

<!-- Twitch -->
<h2 class="stats-subtitle">Twitch</h2>
<div class="stats-grid">
  <div class="stat-card">
    <span class="stat-value">{{ twitch.follower_count | default: "?" }}</span>
    <span class="stat-label">Followers</span>
  </div>
  {% if twitch.view_count %}
  <div class="stat-card accent-purple">
    <span class="stat-value">{{ twitch.view_count }}</span>
    <span class="stat-label">Channel Views</span>
  </div>
  {% endif %}
  {% if twitch.broadcaster_type %}
  <div class="stat-card">
    <span class="stat-value">{{ twitch.broadcaster_type | capitalize }}</span>
    <span class="stat-label">Status</span>
  </div>
  {% endif %}
{% if twitch_age_years %}
  <div class="stat-card accent-purple">
    <span class="stat-value">{{ twitch_age_years }}y</span>
    <span class="stat-label">Account Age</span>
  </div>
  {% endif %}

<!-- Store -->
{% if store %}
  <h2 class="stats-subtitle">Store</h2>
  <div class="stats-grid">
    <div class="stat-card">
      <span class="stat-value">{{ store.total_orders | default: 0 }}</span>
      <span class="stat-label">Total Orders</span>
    </div>
    {% if store.shop and store.shop.domain %}
    <div class="stat-card wide accent-purple">
      <span class="stat-label">Shop</span>
      <a href="https://{{ store.shop.domain }}" target="_blank" rel="noopener" class="stat-value-sm" style="color: inherit; text-decoration: none;">{{ store.shop.name | default: store.shop.domain }}</a>
    </div>
    {% endif %}
  </div>
  {% if store.products and store.products.size > 0 %}
  <div class="stats-grid-two">
    {% for p in store.products %}
    <a href="{{ p.url }}" target="_blank" rel="noopener" class="stat-card wide btn" style="text-align: left;">
      <span class="stat-label">{{ p.name }}</span>
      {% if p.price %}
      <span class="stat-value-sm">{{ p.price }} {{ p.currency }}</span>
      {% endif %}
    </a>
    {% endfor %}
  </div>
  {% endif %}
{% endif %}

<!-- GitHub -->
{% if gh %}
  <h2 class="stats-subtitle">GitHub</h2>
  <div class="stats-grid">
    <div class="stat-card">
      <span class="stat-value">{{ gh.public_repos }}</span>
      <span class="stat-label">Repos</span>
    </div>
    <div class="stat-card accent-purple">
      <span class="stat-value">{{ gh.total_stars }}</span>
      <span class="stat-label">Stars</span>
    </div>
    <div class="stat-card accent-purple">
      <span class="stat-value">{{ gh.total_forks }}</span>
      <span class="stat-label">Forks</span>
    </div>
    <div class="stat-card">
      <span class="stat-value">{{ gh.followers }}</span>
      <span class="stat-label">Followers</span>
    </div>
  </div>
  {% if gh.top_repos and gh.top_repos.size > 0 %}
  <div class="stats-grid-two">
    {% for r in gh.top_repos limit: 5 %}
    <a href="{{ r.url }}" target="_blank" rel="noopener" class="stat-card wide btn" style="text-align: left;">
      <span class="stat-label">{{ r.name }}</span>
      <span class="stat-value-sm">{{ r.stars }} stars &middot; {{ r.forks }} forks</span>
    </a>
    {% endfor %}
  </div>
  {% endif %}
{% endif %}