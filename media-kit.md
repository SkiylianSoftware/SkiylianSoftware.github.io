---
layout: page
title: Media Kit
permalink: /media-kit/
---

{% assign meta = site.data.site_meta %}
{% assign videos = site.data.youtube_main.videos %}
{% assign total_views = 0 %}
{% assign total_likes = 0 %}
{% assign total_seconds = 0 %}
{% for v in videos %}
  {% assign total_views = total_views | plus: v.view_count %}
  {% assign total_likes = total_likes | plus: v.like_count %}
  {% assign total_seconds = total_seconds | plus: v.duration_seconds %}
{% endfor %}
{% assign total_hours = total_seconds | divided_by: 3600 %}

<div class="mk-outer">
  <div class="mk-header">
    <div class="mk-header-text">
      <h1>Media Kit</h1>
      <p class="mk-tagline">Skye / @skiylia &mdash; Trains, automation, and far too many tangents</p>
    </div>
    <p class="mk-updated">Last updated: {{ meta.fetched_at | date: "%d %B %Y" }}</p>
  </div>

  <div class="mk-section">
    <h2>About the Channel</h2>
    <p>{{ meta.description }}</p>
    <p>The channel sits at the intersection of ambitious engineering and genuine cosy chaos. Think marathon train sim sessions, modded Minecraft space programs, programming infrastructure projects, and a lot of time spent rating mochas and visiting rail exhibitions.</p>
  </div>

  <div class="mk-section">
    <h2>Audience</h2>
    <p>Software engineers, automation enthusiasts, train likers, space program enjoyers, and general lovers of engineering chaos. Viewers come for the projects and stay for the tangents.</p>
    <p>Scheduling is Saturday-focused with mid-week casual content. My audience values authenticity and will absolutely call out anything that doesn't fit.</p>
  </div>

  <div class="mk-stats-row">
    <div class="mk-stat"><span class="mk-num">{{ meta.subscriber_count | round }}</span><span class="mk-lbl">Subscribers</span></div>
    <div class="mk-stat accent"><span class="mk-num">{{ meta.view_count }}</span><span class="mk-lbl">Total Views</span></div>
    <div class="mk-stat"><span class="mk-num">{{ meta.video_count }}</span><span class="mk-lbl">Videos</span></div>
    <div class="mk-stat accent"><span class="mk-num">{{ total_views | divided_by: videos.size | default: 0 }}</span><span class="mk-lbl">Avg Views / Video</span></div>
    <div class="mk-stat"><span class="mk-num">{{ total_hours }}h</span><span class="mk-lbl">Content Published</span></div>
    <div class="mk-stat accent"><span class="mk-num">{{ total_likes }}</span><span class="mk-lbl">Total Likes</span></div>
  </div>

  <div class="mk-section">
    <h2>Content Pillars</h2>
    <div class="mk-pillars">
      <div class="mk-pillar">
        <span class="pillar-icon">&#x1F684;</span>
        <strong>Train & Transport Sims</strong>
        <span class="pillar-desc">Skiylian Transport (Transport Fever 2), station design, rail logistics</span>
      </div>
      <div class="mk-pillar">
        <span class="pillar-icon">&#x1F680;</span>
        <strong>Space & Engineering</strong>
        <span class="pillar-desc">Kerbal Space Program with Real Solar System, automation scripts, rocket design</span>
      </div>
      <div class="mk-pillar">
        <span class="pillar-icon">&#x1F3AE;</span>
        <strong>Modded Minecraft</strong>
        <span class="pillar-desc">Astral Skiy custom modpack, Create mod builds, space exploration</span>
      </div>
      <div class="mk-pillar">
        <span class="pillar-icon">&#x1F916;</span>
        <strong>Infrastructure Programming</strong>
        <span class="pillar-desc">YouTube automation tools, Python scripts, calendar sync, video pipeline</span>
      </div>
    </div>
  </div>

  <div class="mk-section">
    <h2>Available Partnerships</h2>
    <ul class="mk-list">
      <li>Dedicated video segments &mdash; in-context demonstrations within regular uploads</li>
      <li>Stream integrations &mdash; on-stream mentions, overlays, sponsored segments during Twitch broadcasts</li>
      <li>Description & end screen placements &mdash; links, logos, and call-to-actions</li>
      <li>Cross-promotion &mdash; mutual membership or content collaborations</li>
    </ul>
  </div>

  <div class="mk-section">
    <h2>Disclosure & Ethics</h2>
    <p>I follow UK advertising guidelines. Every sponsorship is announced verbally at the start of the video and contained in a clearly denoted section that viewers can easily skip. I retain full creative control over scripting and presentation. Exclusivity clauses, strict NDAs, and pre-written scripts are not offered.</p>
  </div>

  <div class="mk-logos" id="mk-logos">
    <p class="logos-placeholder">When partners are on board, their logos will appear here.</p>
  </div>

  <div class="mk-footer">
    <p>Interested in working together?</p>
    <a href="mailto:skiyliansoftware@gmail.com?subject=Partnership%20Inquiry" class="btn btn-primary">skiyliansoftware@gmail.com</a>
    <p class="mk-footer-links">YouTube: <a href="https://watch.skiylia.dev">watch.skiylia.dev</a> &middot; Twitch: <a href="https://live.skiylia.dev">live.skiylia.dev</a> &middot; GitHub: <a href="https://code.skiylia.dev">code.skiylia.dev</a></p>
  </div>
</div>

<style>
.mk-outer {
  max-width: 700px;
  margin: 0 auto;
  padding: 2rem 0;
}
.mk-header {
  border-bottom: 2px solid rgba(45, 212, 191, 0.15);
  padding-bottom: 1rem;
  margin-bottom: 2rem;
}
.mk-header h1 {
  font-size: 1.5rem;
  margin: 0;
}
.mk-tagline {
  font-size: 0.9rem;
  opacity: 0.7;
  margin: 0.3rem 0 0;
}
.mk-updated {
  font-size: 0.78rem;
  opacity: 0.4;
  margin: 0.5rem 0 0;
}
.mk-section {
  margin: 1.5rem 0;
}
.mk-section h2 {
  font-size: 1.05rem;
  margin: 0 0 0.6rem;
  border-bottom: 1px solid rgba(45, 212, 191, 0.08);
  padding-bottom: 0.3rem;
}
.mk-section p {
  font-size: 0.9rem;
  line-height: 1.6;
  opacity: 0.85;
  margin: 0.4rem 0;
}
.mk-stats-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.8rem;
  margin: 2rem 0;
  justify-content: center;
}
.mk-stat {
  background: rgba(13, 13, 30, 0.8);
  border: 1px solid rgba(45, 212, 191, 0.1);
  border-radius: 10px;
  padding: 1rem 1.25rem;
  text-align: center;
  min-width: 100px;
  flex: 1;
}
.mk-stat.accent { border-color: rgba(192, 132, 252, 0.15); }
.mk-num {
  display: block;
  font-size: 1.3rem;
  font-weight: 700;
  color: #2dd4bf;
  line-height: 1.2;
}
.mk-stat.accent .mk-num { color: #c084fc; }
.mk-lbl {
  display: block;
  font-size: 0.75rem;
  opacity: 0.6;
  margin-top: 0.2rem;
}
.mk-pillars {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 0.8rem;
  margin: 0.8rem 0;
}
.mk-pillar {
  background: rgba(13, 13, 30, 0.8);
  border: 1px solid rgba(45, 212, 191, 0.06);
  border-radius: 8px;
  padding: 0.8rem 1rem;
  font-size: 0.85rem;
}
.pillar-icon { margin-right: 0.3rem; }
.pillar-desc {
  display: block;
  font-size: 0.8rem;
  opacity: 0.6;
  margin-top: 0.2rem;
}
.mk-list {
  padding-left: 1.2rem;
}
.mk-list li {
  margin: 0.5rem 0;
  font-size: 0.9rem;
  opacity: 0.85;
  line-height: 1.5;
}
.mk-logos {
  margin: 2rem 0;
  padding: 1.5rem;
  border: 1px dashed rgba(45, 212, 191, 0.12);
  border-radius: 10px;
  text-align: center;
}
.logos-placeholder {
  font-size: 0.85rem;
  opacity: 0.35;
  margin: 0;
  font-style: italic;
}
.mk-footer {
  margin: 2rem 0;
  padding: 1.5rem;
  border: 1px solid rgba(45, 212, 191, 0.1);
  border-radius: 10px;
  text-align: center;
  background: rgba(45, 212, 191, 0.02);
}
.mk-footer p { margin: 0 0 0.8rem; font-size: 1rem; }
.mk-footer-links { margin-top: 0.8rem !important; font-size: 0.8rem !important; }
.mk-footer-links a { color: #c084fc; }

@media print {
  #sidebar, #topbar-wrapper, #panel-wrapper, #tail-wrapper, .modal { display: none !important; }
  #main-wrapper { max-width: 100% !important; }
  .mk-outer { max-width: 100%; padding: 0; }
  .mk-stat { break-inside: avoid; }
  body { background: #fff !important; color: #000 !important; }
}
</style>