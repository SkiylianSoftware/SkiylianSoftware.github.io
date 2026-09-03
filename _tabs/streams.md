---
layout: page
icon: "fa-brands fa-twitch"
title: Streams
order: 3
permalink: /streams/
group: media
---

{% assign twitch_sched = site.data.twitch_schedule.segments %}
{% assign now_epoch = site.time | date: "%s" | plus: 0 %}
{% assign week_from_now = now_epoch | plus: 604800 %}

<div id="live-status" class="live-section">
        <div id="offline-panel" class="offline-panel">
            <div class="offline-icon"><i class="fas fa-circle"></i></div>
            <div class="offline-text">
                <h2>Currently Offline</h2>
                <p>Not streaming right now.</p>
                <p>Browse <a href="/videos" class="btn">videos</a> or check <a href="/streams" class="btn">past
                        VODs</a></p>
            </div>
        </div>
        <div id="live-embed" class="live-embed" style="display: none;">
            <div class="live-badge">LIVE</div>
            <div class="live-platform-tabs">
                <button class="live-tab active" data-platform="twitch" onclick="switchLivePlatform('twitch')">Twitch</button>
                <button class="live-tab" data-platform="youtube" onclick="switchLivePlatform('youtube')">YouTube</button>
            </div>
            <div id="twitch-player-container"></div>
            <div id="youtube-player-container" style="display: none;">
                <iframe id="youtube-live-iframe" width="100%" height="480"
                    src="https://www.youtube.com/embed/live_stream?channel=UC4s4eXHuzj7OxwJXgiZgAYw&autoplay=1"
                    allow="autoplay; encrypted-media" allowfullscreen></iframe>
            </div>
        </div>
    </div>

<div class="section-break"></div>

{% if twitch_sched and twitch_sched.size > 0 %}
{% assign shown = 0 %}
<div class="section-break"></div>
<div class="widget-card">
  <h3 class="widget-title"><i class="fas fa-calendar-alt"></i> Upcoming Streams</h3>
  <div class="widget-body">
    {% for s in twitch_sched limit: 10 %}
    {% assign s_epoch = s.start_time | date: "%s" | plus: 0 %}
    {% if s_epoch > now_epoch and s_epoch < week_from_now %}
    {% assign shown = shown | plus: 1 %}
    {% assign start = s.start_time | date: "%A" %}
    <div class="schedule-item">
      <div class="schedule-row">
        <span class="schedule-day">{{ start }}</span>
        <span class="schedule-time"><time class="schedule-utc" datetime="{{ s.start_time }}">{{ s.start_time | date: "%H:%M" }}</time></span>
      </div>
      <span class="schedule-type">{{ s.category | default: s.title | truncate: 50 }}</span>
    </div>
    {% endif %}
    {% endfor %}
    {% if shown == 0 %}
    <p class="schedule-none">No streams scheduled this week.</p>
    {% endif %}
  </div>
</div>
{% endif %}

<div class="section-break"></div>

{% assign clips = site.data.twitch_clips.clips %}
{% if clips.size > 0 %}
<h2 class="section-title">Recent Clips</h2>
<div class="clips-grid">
  {% for clip in clips limit: 12 %}
  <div class="clip-card" onclick="openClip(this)" data-clip-id="{{ clip.id }}" data-title="{{ clip.title | escape }}"
       data-views="{{ clip.view_count }}" data-duration="{{ clip.duration_seconds }}"
       data-game="{{ clip.game_name }}" data-created="{{ clip.created_at }}">
    <div class="thumb-wrap">
      <img src="{{ clip.thumbnail }}" alt="{{ clip.title }}" loading="lazy">
      <div class="play-overlay"><i class="fas fa-play"></i></div>
      {% if clip.duration_seconds > 0 %}<span class="duration-badge">{{ clip.duration_seconds }}s</span>{% endif %}
    </div>
    <div class="card-body">
      <h3>{{ clip.title }}</h3>
      <div class="meta-row">
        {% if clip.view_count %}<span class="views">{{ clip.view_count }} views</span>{% endif %}
        {% if clip.game_name %}<span class="clips-game">{{ clip.game_name }}</span>{% endif %}
      </div>
    </div>
  </div>
  {% endfor %}
</div>
{% endif %}

<h2 class="section-title">Stream Archives</h2>

{% assign vods = "" | split: "," %}
{% assign yt_vods = site.data.youtube_vods.videos %}
{% assign tw_vods = site.data.twitch_vods.videos %}
{% if yt_vods %}{% assign vods = vods | concat: yt_vods %}{% endif %}
{% if tw_vods %}{% assign vods = vods | concat: tw_vods %}{% endif %}
{% assign vods = vods | sort: "published" | reverse %}
{% if vods.size > 0 %}
<div id="stream-grid" class="video-grid" data-paged="12">
  {% for vod in vods %}
  <div class="video-card" data-video-id="{{ vod.video_id }}" data-title="{{ vod.title | escape }}" data-url="{{ vod.url }}" data-platform="{{ vod.platform | default: 'youtube' }}"
      data-published="{{ vod.published }}" data-views="{{ vod.view_count | default: 0 }}"
      data-duration="{{ vod.duration_seconds | default: 0 }}"
      data-likes="{{ vod.like_count | default: 0 }}" data-comments="{{ vod.comment_count | default: 0 }}"
      data-series="{% if vod.series %}{{ vod.series.series_name | escape }}{% endif %}"
      data-series-slug="{% if vod.series %}{{ vod.series.series_name | slugify }}{% endif %}"
      data-game="{% if vod.series %}{{ vod.series.game | escape }}{% endif %}"
      data-game-slug="{% if vod.series %}{{ vod.series.game | slugify }}{% endif %}"
      data-description="{{ vod.description | escape }}"
      onclick="openPlayer(this)">
    <div class="thumb-wrap">
      <img src="{{ vod.thumbnail }}" alt="{{ vod.title }}" loading="lazy">
      <div class="play-overlay"><i class="fas fa-play"></i></div>
      {% if vod.duration_seconds and vod.duration_seconds > 0 %}
      <span class="duration-badge">{{ vod.duration_seconds | divided_by: 3600 }}:{{ vod.duration_seconds | modulo: 3600 | divided_by: 60 | prepend: '00' | slice: -2, 2 }}:{{ vod.duration_seconds | modulo: 60 | prepend: '00' | slice: -2, 2 }}</span>
      {% endif %}
    </div>
    <div class="card-body">
      <h3>{{ vod.title }}</h3>
      <div class="meta-row">
        {% if vod.published %}
        <span class="meta-date"><time datetime="{{ vod.published }}">{{ vod.published | date: "%d %b %Y" }}</time>
          <span class="reltime" datetime="{{ vod.published }}"></span></span>
        {% endif %}
        {% if vod.view_count and vod.view_count > 0 %}
        <span class="views">{{ vod.view_count }} views</span>
        {% endif %}
      </div>
      {% if vod.description %}
      <p class="video-desc">{{ vod.description | truncate: 120 }}</p>
      {% endif %}
    </div>
  </div>
  {% endfor %}
</div>
{% else %}
<div class="streams-empty">
  <div class="empty-icon"><i class="fas fa-video"></i></div>
  <h3>No VODs Yet</h3>
  <p>Stream archives will appear here once I go live and save the broadcast.</p>
  <div class="streams-empty-links">
    <a href="https://live.skiylia.dev" class="btn" target="_blank"><i class="fab fa-twitch"></i> Watch on Twitch</a>
    <a href="https://vods.skiylia.dev" class="btn" target="_blank"><i class="fab fa-youtube"></i> Browse VODs</a>
  </div>
</div>
{% endif %}

{% include video-modal.html %}


