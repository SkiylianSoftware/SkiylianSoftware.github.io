---
layout: page
icon: "fa-solid fa-chart-simple"
title: Dashboard
order: 7
permalink: /dashboard/
group: stats
---

{% include stale-banner.html %}

<p class="stats-freshness"><a href="/history/">Full history &amp; milestones</a> &middot; <a href="/year/">Year in Review</a></p>

{% assign meta = site.data.site_meta %}
{% assign videos = site.data.youtube_main.videos %}
{% assign vods_list = site.data.youtube_vods.videos %}
{% assign twitch = site.data.twitch_stats %}
{% assign gh = site.data.github %}
{% assign store = site.data.fourthwall %}

{% assign has_vods = false %}
{% if vods_list.size > 0 or meta.vods_subscriber_count %}{% assign has_vods = true %}{% endif %}

{% if videos.size > 0 %}
  {% assign first_video = videos | sort: "published" | first %}
  {% assign total_watch_seconds = 0 %}
  {% assign total_video_views = 0 %}
  {% assign total_likes = 0 %}
  {% assign yt_start = nil %}
  {% for v in videos %}
    {% assign total_watch_seconds = total_watch_seconds | plus: v.duration_seconds %}
    {% assign total_video_views = total_video_views | plus: v.view_count %}
    {% assign total_likes = total_likes | plus: v.like_count %}
    {% assign vp = v.published | date: "%Y-%m-%d" %}
    {% if yt_start == nil or vp < yt_start %}{% assign yt_start = vp %}{% endif %}
  {% endfor %}
  {% if total_watch_seconds > 0 %}
    {% assign total_watch_hours = total_watch_seconds | divided_by: 3600 %}
  {% else %}
    {% assign total_watch_hours = 0 %}
  {% endif %}
  {% assign most_viewed = videos | sort: "view_count" | last %}
  {% assign most_liked = videos | sort: "like_count" | last %}
  {% assign avg_views = total_video_views | divided_by: videos.size %}
  {% if yt_start %}
    {% assign yt_start_ts = yt_start | date: "%s" %}
    {% assign now_ts = site.time | date: "%s" %}
    {% assign yt_age_days = now_ts | minus: yt_start_ts | divided_by: 86400 %}
    {% assign yt_age_years = yt_age_days | divided_by: 365 %}
    {% assign vpm = meta.video_count | times: 30 | divided_by: yt_age_days %}
  {% endif %}
{% endif %}

{% if twitch.created_at %}
  {% assign twitch_start_ts = twitch.created_at | date: "%s" %}
  {% assign now_ts_t = site.time | date: "%s" %}
  {% assign twitch_age_days = now_ts_t | minus: twitch_start_ts | divided_by: 86400 %}
  {% assign twitch_age_years = twitch_age_days | divided_by: 365 %}
{% endif %}

{% assign hist = site.data.history %}
{% if hist.size > 1 %}
{% assign last_hist = hist.last %}
{% assign month_ago_ts = site.time | date: "%s" | minus: 2592000 %}
{% assign anchor_h = nil %}
{% for e in hist reversed %}
  {% assign e_ts = e.date | date: "%s" | plus: 0 %}
  {% if e_ts >= month_ago_ts %}{% assign anchor_h = e %}{% else %}{% break %}{% endif %}
{% endfor %}
{% if anchor_h == nil %}{% assign anchor_h = hist.first %}{% endif %}
{% assign m_subs_d = last_hist.youtube_main.subs | minus: anchor_h.youtube_main.subs %}
{% assign m_views_d = last_hist.youtube_main.views | minus: anchor_h.youtube_main.views %}
{% assign m_videos_d = last_hist.youtube_main.videos | minus: anchor_h.youtube_main.videos %}
{% assign m_watch = 0 %}
{% for e in hist reversed %}
  {% assign e_ts = e.date | date: "%s" | plus: 0 %}
  {% if e_ts < month_ago_ts %}{% break %}{% endif %}
  {% if e._analytics.watch_time_minutes %}{% assign m_watch = m_watch | plus: e._analytics.watch_time_minutes %}{% endif %}
{% endfor %}
{% assign m_watch_h = m_watch | divided_by: 60 %}
{% assign m_avg_view = m_views_d | divided_by: 30 %}
{% endif %}

<!-- Combined Overview -->
<p class="stats-freshness">Data refreshed {{ site.data.history.last.date | default: "" | truncate: 10, "" }}</p>
<div class="motd-box">
  <i class="fas fa-chart-line motd-icon"></i>
  <span>
    {% if hist and hist.size > 1 %}
    In the last 30 days the channel gained <strong>{% if m_subs_d >= 0 %}+{% endif %}{{ m_subs_d }}</strong> subscribers, <strong>{% if m_views_d >= 0 %}+{% endif %}{{ m_views_d }}</strong> views ({% if m_avg_view >= 0 %}+{% endif %}{{ m_avg_view }}/day) and <strong>{% if m_videos_d >= 0 %}+{% endif %}{{ m_videos_d }}</strong> videos, for <strong>{{ m_watch_h }}h</strong> of viewer watch time.
    {% if most_viewed %}<div class="video-mention"><span class="mini-thumb" style="background-image:url('{{ most_viewed.thumbnail }}')" role="img" aria-label="{{ most_viewed.title }}"></span><span>Currently most-watched: <strong>{{ most_viewed.title }}</strong> ({{ most_viewed.view_count }} views).</span></div>{% endif %}
    {% else %}
    Stats will populate here as the tracking pipeline starts collecting history.
    {% endif %}
  </span>
</div>
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

<!-- Upcoming Milestones -->
{% assign fm = site.data.future_milestones %}
{% if fm %}
<h2 class="stats-subtitle">Upcoming Milestones</h2>
<div class="stats-grid">
  {% for pair in fm %}
  {% assign mkey = pair[0] %}
  {% assign mval = pair[1] %}
  {% if mval and mval.next %}
  <div class="stat-card ms-upcoming ms-{{ mkey }}">
    <span class="stat-value">{{ mval.next }}</span>
    <span class="stat-label">{{ mkey | capitalize }} ({{ mval.current }})</span>
    {% if mval.eta and mval.eta != "" %}
    <span class="stat-eta">~{{ mval.eta | date: "%b %Y" }}</span>
    {% else %}
    <span class="stat-eta">pacing unknown</span>
    {% endif %}
  </div>
  {% endif %}
  {% endfor %}
</div>
{% endif %}

<!-- Last 30 Days delta -->
{% assign history = site.data.history %}
{% if history.size > 1 %}
{% assign thirty_ago = site.time | date: "%s" | minus: 2592000 %}
{% assign last_entry = history.last %}
{% assign anchor_entry = nil %}
{% for e in history reversed %}
  {% assign e_epoch = e.date | date: "%s" | plus: 0 %}
  {% if e_epoch >= thirty_ago %}
    {% assign anchor_entry = e %}
  {% else %}
    {% break %}
  {% endif %}
{% endfor %}
{% if anchor_entry == nil %}{% assign anchor_entry = history.first %}{% endif %}
{% assign delta_subs = last_entry.youtube_main.subs | minus: anchor_entry.youtube_main.subs %}
{% assign delta_views = last_entry.youtube_main.views | minus: anchor_entry.youtube_main.views %}
{% assign delta_videos = last_entry.youtube_main.videos | minus: anchor_entry.youtube_main.videos %}
{% assign delta_watch = 0 %}
{% for e in site.data.history reversed %}
  {% assign e_epoch = e.date | date: "%s" | plus: 0 %}
  {% if e_epoch < thirty_ago %}{% break %}{% endif %}
  {% if e._analytics.watch_time_minutes %}
    {% assign delta_watch = delta_watch | plus: e._analytics.watch_time_minutes %}
  {% endif %}
{% endfor %}
{% assign delta_watch_h = delta_watch | divided_by: 60 %}
<h2 class="stats-subtitle">Last 30 Days</h2>
<div class="stats-grid">
  <div class="stat-card">
    <span class="stat-value{% if delta_subs >= 0 %} stat-positive{% else %} stat-negative{% endif %}">{% if delta_subs >= 0 %}+{% endif %}{{ delta_subs }}</span>
    <span class="stat-label">Subs</span>
  </div>
  <div class="stat-card accent-purple">
    <span class="stat-value{% if delta_views >= 0 %} stat-positive{% else %} stat-negative{% endif %}">{% if delta_views >= 0 %}+{% endif %}{{ delta_views }}</span>
    <span class="stat-label">Views</span>
  </div>
  <div class="stat-card">
    <span class="stat-value{% if delta_videos >= 0 %} stat-positive{% else %} stat-negative{% endif %}">{% if delta_videos >= 0 %}+{% endif %}{{ delta_videos }}</span>
    <span class="stat-label">Videos</span>
  </div>
  <div class="stat-card accent-purple">
    <span class="stat-value">{{ delta_watch_h }}h</span>
    <span class="stat-label">Viewer Watch Time (30d)</span>
  </div>
</div>
{% endif %}

<!-- YouTube -->
{% if videos.size > 0 %}
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
    {% if yt_age_years %}
    <div class="stat-card">
      <span class="stat-value">{{ yt_age_years }}y</span>
      <span class="stat-label">Content Age</span>
    </div>
    {% endif %}
    {% if vpm %}
    <div class="stat-card accent-purple">
      <span class="stat-value">{{ vpm }}</span>
      <span class="stat-label">Videos/Month</span>
    </div>
    {% endif %}
    <div class="stat-card">
      <a href="https://www.youtube.com/watch?v={{ first_video.video_id }}" target="_blank" rel="noopener" style="color: inherit; text-decoration: none;">
        <span class="video-mention"><span class="mini-thumb" style="background-image:url('{{ first_video.thumbnail }}')" role="img" aria-label="{{ first_video.title }}"></span></span>
        <span class="stat-value">{{ yt_start }}</span>
        <span class="stat-label">First Video</span>
      </a>
    </div>
    {% if meta.memberships_available %}
    <div class="stat-card accent-purple">
      <span class="stat-value">&#10003;</span>
      <span class="stat-label">Memberships</span>
    </div>
    {% endif %}
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
  {% if twitch.broadcaster_type and twitch.broadcaster_type != "" %}
  <div class="stat-card">
    <span class="stat-value">{{ twitch.broadcaster_type | capitalize }}</span>
    <span class="stat-label">Status</span>
  </div>
  {% else %}
  <div class="stat-card">
    <span class="stat-value">Standard</span>
    <span class="stat-label">Status</span>
  </div>
  {% endif %}
  {% if twitch_age_years %}
  <div class="stat-card accent-purple">
    <span class="stat-value">{{ twitch_age_years }}y</span>
    <span class="stat-label">Account Age</span>
  </div>
  {% endif %}
  {% if twitch.stream_count and twitch.stream_count > 0 %}
  <div class="stat-card">
    <span class="stat-value">{{ twitch.stream_count }}</span>
    <span class="stat-label">Streams</span>
  </div>
  {% endif %}
</div>

<!-- Store -->
{% if store.products and store.products.size > 0 %}
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
