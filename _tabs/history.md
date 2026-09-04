---
layout: page
icon: "fa-solid fa-timeline"
title: History
order: 6
permalink: /history/
group: stats
---

{% include stale-banner.html %}

<div class="history-toolbar">
  <span class="history-toolbar-label">Growth over time</span>
  <a href="/year/" class="btn btn-outline-primary tag-btn">Year in Review</a>
  <a href="/dashboard/" class="btn btn-outline-primary tag-btn">Dashboard</a>
</div>

{% assign history = site.data.history %}
{% if history and history.size > 0 %}

<div class="chart-container">
  <canvas id="growthChart"></canvas>
</div>

<div class="chart-controls">
  <button class="chart-btn active" onclick="toggleMetric('audience')" id="btn-audience">Audience</button>
  <button class="chart-btn" onclick="toggleMetric('views')" id="btn-views">Views</button>
  <button class="chart-btn" onclick="toggleMetric('content')" id="btn-content">Content</button>
  {% if site.data.fourthwall.products.size > 0 %}
  <button class="chart-btn" onclick="toggleMetric('orders')" id="btn-orders">Orders</button>
  {% endif %}
  {% assign has_github = history | map: "github" | compact | size %}
  {% if has_github > 0 %}
  <button class="chart-btn" onclick="toggleMetric('github')" id="btn-github">GitHub</button>
  {% endif %}
  {% if history.last.youtube_main.likes > 0 %}
  <button class="chart-btn" onclick="toggleMetric('likes')" id="btn-likes">Likes</button>
  {% endif %}
  {% if history.last.youtube_main.comments > 0 %}
  <button class="chart-btn" onclick="toggleMetric('comments')" id="btn-comments">Comments</button>
  {% endif %}
  {% assign has_watch = history | map: "_analytics" | compact | size %}
  {% if has_watch > 0 %}
  <button class="chart-btn" onclick="toggleMetric('watch')" id="btn-watch">Watch Time</button>
  {% endif %}
  {% if history.last.youtube_main.videos > 0 %}
  <button class="chart-btn" onclick="toggleMetric('uploads')" id="btn-uploads">Uploads/Month</button>
  {% endif %}
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<script>
window.HIST_DATA = {{ history | jsonify }};
window.HIST_GITHUB = {% if has_github > 0 %}true{% else %}false{% endif %};
window.HIST_ORDERS = {% if site.data.fourthwall.products.size > 0 %}true{% else %}false{% endif %};
</script>
<script src="{{ '/assets/js/history.js' | relative_url }}" defer></script>

<h2 class="milestones-heading">Milestones</h2>
<p class="milestones-note">&#9881;&#65039; Powers of three (ternary) are my primary counting system. Powers of two (binary) and round numbers also tracked. <a href="/about">Why ternary?</a></p>

<div class="ms-filter-bar" id="ms-filter-bar">
  <button class="ms-filter-btn active" data-filter="all">All</button>
  <button class="ms-filter-btn" data-filter="subs">Subs</button>
  <button class="ms-filter-btn" data-filter="views">Views</button>
  <button class="ms-filter-btn" data-filter="videos">Videos</button>
  <button class="ms-filter-btn" data-filter="game">Games</button>
  <button class="ms-filter-btn" data-filter="watch">Watch Time</button>
  <button class="ms-filter-btn" data-filter="content">Content</button>
  <button class="ms-filter-btn" data-filter="likes">Likes</button>
  <button class="ms-filter-btn" data-filter="comments">Comments</button>
  <button class="ms-filter-btn" data-filter="other">Other</button>
</div>

<script>
document.getElementById('ms-filter-bar').addEventListener('click', function(e) {
  var btn = e.target.closest('.ms-filter-btn');
  if (btn) filterMilestones(btn.getAttribute('data-filter'));
});
</script>

{% assign milestones = site.data.milestones %}
{% assign ms_keys = milestones.reached %}
{% if ms_keys %}
<div class="timeline">
  {% assign prev_month = "" %}
  {% for item in ms_keys %}
    {% assign key = item[0] %}
    {% assign date = item[1] | truncate: 10, "" %}
    {% assign month = date | truncate: 7, "" %}
    {% if month != prev_month %}
    <div class="month-divider">{{ date | date: "%B %Y" }}</div>
    {% assign prev_month = month %}
    {% endif %}
    {% assign icon = "&#9679;" %}
    {% assign mclass = "" %}
    {% assign link = nil %}
    {% assign link_meta = milestones.links[key] %}
    {% assign display = key %}

    {% if key contains "video_first_likes_" %}
      {% assign icon = "&#128077;" %}{% assign mclass = "ms-likes" %}{% assign link = nil %}
      {% assign val = key | remove: "video_first_likes_" %}
      {% capture d %}First video to {{ val }} likes{% endcapture %}{% assign display = d %}
    {% elsif key contains "video_first_comments_" %}
      {% assign icon = "&#128172;" %}{% assign mclass = "ms-comments" %}{% assign link = nil %}
      {% assign val = key | remove: "video_first_comments_" %}
      {% capture d %}First video to {{ val }} comments{% endcapture %}{% assign display = d %}
    {% elsif key contains "video_first_" %}
      {% assign icon = "&#127916;" %}{% assign mclass = "ms-video-first" %}{% assign link = nil %}
      {% assign val = key | remove: "video_first_" %}
      {% capture d %}First video to {{ val }} views{% endcapture %}{% assign display = d %}
    {% elsif key contains "game_" %}
      {% assign icon = "&#127918;" %}{% assign mclass = "ms-game" %}
      {% assign rest = key | remove_first: "game_" %}
      {% if rest contains "_ep_" %}
        {% assign parts = rest | split: "_ep_" %}
        {% capture d %}{{ parts[1] }} episodes in {{ parts[0] }}{% endcapture %}{% assign display = d %}
        {% assign mclass = "ms-videos" %}
      {% elsif rest contains "_upload_" %}
        {% assign parts = rest | split: "_upload_" %}
        {% capture d %}{{ parts[1] }} hours uploaded in {{ parts[0] }}{% endcapture %}{% assign display = d %}
        {% assign mclass = "ms-upload" %}
      {% elsif rest contains "_started" %}
        {% assign g = rest | remove: "_started" %}
        {% assign mclass = "ms-started" %}
        {% assign gname = link_meta.series_name | default: g %}
        {% capture d %}{{ gname }} ({{ g }}) started{% endcapture %}{% assign display = d %}
      {% elsif rest contains "_views_" %}
        {% assign parts = rest | split: "_views_" %}
        {% capture d %}{{ parts[1] }} views across {{ parts[0] }}{% endcapture %}{% assign display = d %}
        {% assign mclass = "ms-views" %}
      {% elsif rest contains "_hours_" %}
        {% assign parts = rest | split: "_hours_" %}
        {% capture d %}{{ parts[1] }} hours watched in {{ parts[0] }}{% endcapture %}{% assign display = d %}
        {% assign mclass = "ms-hours" %}
      {% elsif rest contains "_return_" %}
        {% assign parts = rest | split: "_return_" %}
        {% capture d %}Back to {{ parts[0] }} after {{ parts[1] }} days{% endcapture %}{% assign display = d %}
      {% endif %}
      {% assign game_slug = rest | split: "_" | first | slugify %}
      {% assign link = "/games#" | append: game_slug %}
    {% elsif key contains "series_" %}
      {% assign icon = "&#127918;" %}{% assign mclass = "ms-game" %}
      {% assign rest = key | remove_first: "series_" %}
      {% if rest contains "_views_" %}
        {% assign parts = rest | split: "_views_" %}
        {% capture d %}{{ parts[1] }} views in {{ parts[0] }}{% endcapture %}{% assign display = d %}
        {% assign mclass = "ms-views" %}
      {% elsif rest contains "_hours_" %}
        {% assign parts = rest | split: "_hours_" %}
        {% capture d %}{{ parts[1] }} hours watched in {{ parts[0] }}{% endcapture %}{% assign display = d %}
        {% assign mclass = "ms-hours" %}
      {% elsif rest contains "_upload_" %}
        {% assign parts = rest | split: "_upload_" %}
        {% capture d %}{{ parts[1] }} hours uploaded in {{ parts[0] }}{% endcapture %}{% assign display = d %}
        {% assign mclass = "ms-upload" %}
      {% elsif rest contains "_return_" %}
        {% assign parts = rest | split: "_return_" %}
        {% capture d %}Back to {{ parts[0] }} after {{ parts[1] }} days{% endcapture %}{% assign display = d %}
      {% endif %}
    {% elsif key contains "age_" %}
      {% assign icon = "&#127800;" %}{% assign mclass = "ms-age" %}{% assign link = "/" %}
      {% assign display = key | remove: "age_" | append: " days old (main)" %}
    {% elsif key contains "anniversary_" %}
      {% assign icon = "&#127800;" %}{% assign mclass = "ms-age" %}{% assign link = "/about" %}
    {% elsif key contains "hiatus_vods_" %}
      {% assign icon = "&#127987;" %}{% assign mclass = "ms-hiatus" %}{% assign link = "/videos" %}
      {% assign val = key | remove: "hiatus_vods_" %}
      {% capture d %}VODs hiatus ended after {{ val }} days{% endcapture %}{% assign display = d %}
    {% elsif key contains "hiatus_" %}
      {% assign icon = "&#127987;" %}{% assign mclass = "ms-hiatus" %}{% assign link = "/videos" %}
      {% assign val = key | remove: "hiatus_" %}
      {% capture d %}Returned after hiatus of {{ val }} days{% endcapture %}{% assign display = d %}
    {% elsif key contains "streak_vods_" %}
      {% assign icon = "&#128293;" %}{% assign mclass = "ms-streak" %}{% assign link = "/videos" %}
      {% assign val = key | remove: "streak_vods_" %}
      {% capture d %}{{ val }}-week VODs upload streak{% endcapture %}{% assign display = d %}
    {% elsif key contains "streak_" %}
      {% assign icon = "&#128293;" %}{% assign mclass = "ms-streak" %}{% assign link = "/videos" %}
      {% assign val = key | remove: "streak_" %}
      {% capture d %}{{ val }}-week upload streak (main){% endcapture %}{% assign display = d %}
    {% elsif key contains "youtube_hours_" %}
      {% assign icon = '<i class="fab fa-youtube" style="color:#FF0000"></i>' %}{% assign mclass = "ms-hours" %}{% assign link = "/videos" %}
      {% assign val = key | remove: "youtube_hours_" %}
      {% capture d %}{{ val }} hours watched on YouTube{% endcapture %}{% assign display = d %}
    {% elsif key contains "twitch_hours_" %}
      {% assign icon = '<i class="fab fa-twitch" style="color:#9146FF"></i>' %}{% assign mclass = "ms-hours" %}{% assign link = "/streams" %}
      {% assign val = key | remove: "twitch_hours_" %}
      {% capture d %}{{ val }} hours watched on Twitch{% endcapture %}{% assign display = d %}
    {% elsif key contains "combined_hours_" %}
      {% assign icon = "&#9200;" %}{% assign mclass = "ms-hours" %}{% assign link = "/videos" %}
      {% assign val = key | remove: "combined_hours_" %}
      {% capture d %}{{ val }} hours watched across all channels{% endcapture %}{% assign display = d %}
    {% elsif key contains "youtube_upload_" %}
      {% assign icon = "&#128221;" %}{% assign mclass = "ms-upload" %}{% assign link = "/videos" %}
      {% assign val = key | remove: "youtube_upload_" %}
      {% capture d %}{{ val }} hours uploaded on YouTube{% endcapture %}{% assign display = d %}
    {% elsif key contains "vods_upload_" %}
      {% assign icon = "&#128221;" %}{% assign mclass = "ms-upload" %}{% assign link = "/videos" %}
      {% assign val = key | remove: "vods_upload_" %}
      {% capture d %}{{ val }} hours uploaded on VODs{% endcapture %}{% assign display = d %}
    {% elsif key contains "combined_upload_" %}
      {% assign icon = "&#128221;" %}{% assign mclass = "ms-upload" %}{% assign link = "/videos" %}
      {% assign val = key | remove: "combined_upload_" %}
      {% capture d %}{{ val }} hours uploaded across all channels{% endcapture %}{% assign display = d %}
    {% else %}
      {% assign pparts = key | split: "_" %}
      {% assign val = pparts | last %}
      {% assign ptype = pparts[0] %}
      {% if key contains "views" %}{% assign icon = "&#128065;" %}{% assign mclass = "ms-views" %}{% assign link = "/videos" %}
      {% elsif key contains "videos" %}{% assign icon = "&#127916;" %}{% assign mclass = "ms-videos" %}{% assign link = "/videos" %}
      {% elsif key contains "likes" %}{% assign icon = "&#128077;" %}{% assign mclass = "ms-likes" %}{% assign link = "/videos" %}
      {% elsif key contains "comments" %}{% assign icon = "&#128172;" %}{% assign mclass = "ms-comments" %}{% assign link = "/videos" %}
      {% elsif key contains "twitch_followers" %}{% assign icon = "&#127987;" %}{% assign mclass = "ms-subs" %}{% assign link = "/streams" %}
      {% elsif key contains "twitch_views" %}{% assign icon = "&#128065;" %}{% assign mclass = "ms-views" %}{% assign link = "/streams" %}
      {% elsif key contains "store_orders" %}{% assign icon = "&#128092;" %}{% assign mclass = "ms-subs" %}{% assign link = "/support" %}
      {% else %}{% assign icon = "&#11088;" %}{% assign mclass = "ms-subs" %}{% assign link = "/about" %}
      {% endif %}
      {% if key contains "likes" %}
        {% if key contains "youtube_" %}
          {% capture d %}{{ val }} likes on YouTube{% endcapture %}{% assign display = d %}
        {% elsif key contains "vods_" %}
          {% capture d %}{{ val }} likes on VODs{% endcapture %}{% assign display = d %}
        {% elsif key contains "combined_" %}
          {% capture d %}{{ val }} likes across all channels{% endcapture %}{% assign display = d %}
        {% else %}
          {% capture d %}{{ val }} likes{% endcapture %}{% assign display = d %}
        {% endif %}
      {% elsif key contains "comments" %}
        {% if key contains "youtube_" %}
          {% capture d %}{{ val }} comments on YouTube{% endcapture %}{% assign display = d %}
        {% elsif key contains "vods_" %}
          {% capture d %}{{ val }} comments on VODs{% endcapture %}{% assign display = d %}
        {% elsif key contains "combined_" %}
          {% capture d %}{{ val }} comments across all channels{% endcapture %}{% assign display = d %}
        {% else %}
          {% capture d %}{{ val }} comments{% endcapture %}{% assign display = d %}
        {% endif %}
      {% elsif key contains "twitch_followers" %}
        {% capture d %}{{ val }} Twitch followers{% endcapture %}{% assign display = d %}
      {% elsif key contains "twitch_views" %}
        {% capture d %}{{ val }} Twitch views{% endcapture %}{% assign display = d %}
      {% elsif key contains "store_orders" %}
        {% capture d %}{{ val }} store orders{% endcapture %}{% assign display = d %}
      {% else %}
        {% capture d %}{{ val }} {{ ptype }}{% endcapture %}{% assign display = d %}
      {% endif %}
    {% endif %}

    {% if mclass == "ms-subs" %}{% assign dtype = "subs" %}
    {% elsif mclass == "ms-views" %}{% assign dtype = "views" %}
    {% elsif mclass == "ms-videos" %}{% assign dtype = "videos" %}
    {% elsif mclass == "ms-game" or mclass == "ms-started" %}{% assign dtype = "game" %}
    {% elsif mclass == "ms-age" or mclass == "ms-hiatus" or mclass == "ms-streak" %}{% assign dtype = "other" %}
    {% elsif mclass == "ms-video-first" %}{% assign dtype = "views" %}
    {% elsif mclass == "ms-hours" %}{% assign dtype = "watch" %}
    {% elsif mclass == "ms-upload" %}{% assign dtype = "content" %}
    {% elsif mclass == "ms-likes" %}{% assign dtype = "likes" %}
    {% elsif mclass == "ms-comments" %}{% assign dtype = "comments" %}
    {% else %}{% assign dtype = "other" %}
    {% endif %}

    {% if link_meta %}{% assign link = link_meta.url %}{% endif %}

    {% if link_meta.msg %}
      {% assign display = link_meta.msg %}
    {% elsif link_meta.text and key contains "video_first_" %}
      {% assign display = display | append: ": " | append: link_meta.text %}
    {% endif %}

    {% assign has_thumb = link_meta.thumb %}
    {% assign tag = "div" %}
    {% if link %}{% assign tag = "a" %}{% endif %}
    <{{ tag }} {% if link %}href="{{ link }}"{% endif %} class="timeline-item milestone {{ mclass }}" data-type="{{ dtype }}">
      {% if has_thumb %}
      <span class="tl-thumb" style="background-image: url('{{ has_thumb }}')"></span>
      {% else %}
      <span class="tl-icon">{{ icon }}</span>
      {% endif %}
      <span class="tl-body">
        <span class="tl-date">{{ date }}</span>
        <span class="tl-text">{{ display }}</span>
      </span>
    </{{ tag }}>
  {% endfor %}
</div>
{% else %}
<div class="timeline-empty">
  <p>No milestone data yet. They'll appear here as thresholds are crossed during the data pipeline runs.</p>
</div>
{% endif %}

{% else %}
<div class="timeline-empty">
  <p>No historical data yet. The chart and timeline will populate as the daily tracking pipeline collects data over the coming days.</p>
</div>
{% endif %}