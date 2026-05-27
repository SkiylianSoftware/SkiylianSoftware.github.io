---
layout: page
icon: "fa-solid fa-timeline"
title: History
order: 6
permalink: /history/
group: stats
---

{% assign history = site.data.history %}
{% if history and history.size > 0 %}
{{ history.size | prepend: 'History entries: ' | append: ' (first: ' | append: history.first.date | append: ', last: ' | append: history.last.date | append: ')' }}

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
  {% if history[0].github %}
  <button class="chart-btn" onclick="toggleMetric('github')" id="btn-github">GitHub</button>
  {% endif %}
  {% if history.last.youtube_main.likes > 0 %}
  <button class="chart-btn" onclick="toggleMetric('likes')" id="btn-likes">Likes</button>
  {% endif %}
  {% if history.last.youtube_main.comments > 0 %}
  <button class="chart-btn" onclick="toggleMetric('comments')" id="btn-comments">Comments</button>
  {% endif %}
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<script>
var histData = {{ history | jsonify }};
console.log('Chart debug: entries=' + histData.length, 'first=' + histData[0].date, 'last=' + histData[histData.length-1].date);
console.log('Sample entry:', JSON.stringify(histData[Math.floor(histData.length/2)]));

Chart.defaults.elements.line.tension = 0.3;
Chart.defaults.elements.point.radius = 0;

var dates = histData.map(function(h) { return h.date; });

function pluck(entry, platform, field) {
  return (entry[platform] && entry[platform][field]) || 0;
}

var audienceDatasets = [
  { label: 'YouTube', data: histData.map(function(h) { return pluck(h, 'youtube_main', 'subs'); }), borderColor: '#ff4444', backgroundColor: 'rgba(255,68,68,0.05)' },
  { label: 'VODs', data: histData.map(function(h) { return pluck(h, 'youtube_vods', 'subs'); }), borderColor: '#ff8844', backgroundColor: 'rgba(255,136,68,0.05)' },
  { label: 'Twitch', data: histData.map(function(h) { return pluck(h, 'twitch', 'followers'); }), borderColor: '#a970ff', backgroundColor: 'rgba(169,112,255,0.05)' },
];
audienceDatasets.push({
  label: 'Total',
  data: histData.map(function(h) {
    return (pluck(h, 'youtube_main', 'subs') || 0) + (pluck(h, 'youtube_vods', 'subs') || 0) + (pluck(h, 'twitch', 'followers') || 0);
  }),
  borderColor: '#2dd4bf', backgroundColor: 'rgba(45,212,191,0.08)',
  borderWidth: 3, pointRadius: 0,
});

var viewsDatasets = [
  { label: 'YouTube', data: histData.map(function(h) { return pluck(h, 'youtube_main', 'views'); }), borderColor: '#ff4444', backgroundColor: 'rgba(255,68,68,0.05)' },
  { label: 'VODs', data: histData.map(function(h) { return pluck(h, 'youtube_vods', 'views'); }), borderColor: '#ff8844', backgroundColor: 'rgba(255,136,68,0.05)' },
  { label: 'Twitch', data: histData.map(function(h) { return pluck(h, 'twitch', 'views'); }), borderColor: '#a970ff', backgroundColor: 'rgba(169,112,255,0.05)' },
];
viewsDatasets.push({
  label: 'Total',
  data: histData.map(function(h) {
    return (pluck(h, 'youtube_main', 'views') || 0) + (pluck(h, 'youtube_vods', 'views') || 0) + (pluck(h, 'twitch', 'views') || 0);
  }),
  borderColor: '#2dd4bf', backgroundColor: 'rgba(45,212,191,0.08)',
  borderWidth: 3, pointRadius: 0,
});

var contentDatasets = [
  { label: 'YouTube', data: histData.map(function(h) { return pluck(h, 'youtube_main', 'videos'); }), borderColor: '#ff4444', backgroundColor: 'rgba(255,68,68,0.05)' },
  { label: 'VODs', data: histData.map(function(h) { return pluck(h, 'youtube_vods', 'videos'); }), borderColor: '#ff8844', backgroundColor: 'rgba(255,136,68,0.05)' },
];
contentDatasets.push({
  label: 'Total',
  data: histData.map(function(h) {
    return (pluck(h, 'youtube_main', 'videos') || 0) + (pluck(h, 'youtube_vods', 'videos') || 0);
  }),
  borderColor: '#2dd4bf', backgroundColor: 'rgba(45,212,191,0.08)',
  borderWidth: 3, pointRadius: 0,
});

{% if site.data.fourthwall.products.size > 0 %}
var ordersDatasets = [
  { label: 'Fourthwall', data: histData.map(function(h) { return pluck(h, 'fourthwall', 'orders'); }), borderColor: '#c084fc', backgroundColor: 'rgba(192,132,252,0.05)' },
];
{% else %}
var ordersDatasets = [];
{% endif %}

var githubDatasets = [];
{% if history[0].github %}
githubDatasets = [
  { label: 'Stars', data: histData.map(function(h) { return pluck(h, 'github', 'stars'); }), borderColor: '#2dd4bf', backgroundColor: 'rgba(45,212,191,0.05)' },
  { label: 'Followers', data: histData.map(function(h) { return pluck(h, 'github', 'followers'); }), borderColor: '#888', backgroundColor: 'rgba(136,136,136,0.05)' },
  { label: 'Forks', data: histData.map(function(h) { return pluck(h, 'github', 'forks'); }), borderColor: '#c084fc', backgroundColor: 'rgba(192,132,252,0.05)' },
];
{% endif %}

var allMetrics = {
  audience: audienceDatasets,
  views: viewsDatasets,
  content: contentDatasets,
  orders: ordersDatasets,
  github: githubDatasets,
  likes: [
    { label: 'YouTube', data: histData.map(function(h) { return pluck(h, 'youtube_main', 'likes'); }), borderColor: '#ff4444', backgroundColor: 'rgba(255,68,68,0.05)' },
    { label: 'VODs', data: histData.map(function(h) { return pluck(h, 'youtube_vods', 'likes'); }), borderColor: '#ff8844', backgroundColor: 'rgba(255,136,68,0.05)' },
    { label: 'Total', data: histData.map(function(h) { return (pluck(h, 'youtube_main', 'likes') || 0) + (pluck(h, 'youtube_vods', 'likes') || 0); }), borderColor: '#2dd4bf', backgroundColor: 'rgba(45,212,191,0.08)', borderWidth: 3, pointRadius: 0 },
  ],
  comments: [
    { label: 'YouTube', data: histData.map(function(h) { return pluck(h, 'youtube_main', 'comments'); }), borderColor: '#ff4444', backgroundColor: 'rgba(255,68,68,0.05)' },
    { label: 'VODs', data: histData.map(function(h) { return pluck(h, 'youtube_vods', 'comments'); }), borderColor: '#ff8844', backgroundColor: 'rgba(255,136,68,0.05)' },
    { label: 'Total', data: histData.map(function(h) { return (pluck(h, 'youtube_main', 'comments') || 0) + (pluck(h, 'youtube_vods', 'comments') || 0); }), borderColor: '#2dd4bf', backgroundColor: 'rgba(45,212,191,0.08)', borderWidth: 3, pointRadius: 0 },
  ],
};

console.log('Audience dataset length:', audienceDatasets[0].data.length, 'sample:', audienceDatasets[0].data.slice(0,5));
console.log('Dates length:', dates.length, 'sample:', dates.slice(0,5));
console.log('Non-zero subs count:', audienceDatasets[0].data.filter(function(v){return v>0;}).length);
console.log('Max subs:', Math.max.apply(null, audienceDatasets[0].data));

var ctx = document.getElementById('growthChart').getContext('2d');
var chart = new Chart(ctx, {
  type: 'line',
  data: { labels: dates, datasets: audienceDatasets },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: 'index', intersect: false },
    plugins: {
      legend: {
        labels: { color: '#8888aa', font: { size: 12 }, usePointStyle: true, padding: 16 },
      },
      tooltip: {
        backgroundColor: 'rgba(13,13,30,0.9)',
        titleColor: '#c8c8d4',
        bodyColor: '#c8c8d4',
        borderColor: 'rgba(45,212,191,0.3)',
        borderWidth: 1,
        padding: 10,
      }
    },
    scales: {
      x: {
        ticks: { color: '#8888aa', maxTicksLimit: 12 },
        grid: { color: 'rgba(45,212,191,0.05)' }
      },
      y: {
        beginAtZero: true,
        ticks: { color: '#8888aa' },
        grid: { color: 'rgba(45,212,191,0.05)' }
      }
    }
  }
});

function toggleMetric(metric) {
  document.querySelectorAll('.chart-btn').forEach(function(b) { b.classList.remove('active'); });
  document.getElementById('btn-' + metric).classList.add('active');
  chart.data.datasets = allMetrics[metric];
  chart.update();
}
</script>

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
function filterMilestones(type) {
  document.querySelectorAll('.ms-filter-btn').forEach(function(b) { b.classList.toggle('active', b.dataset.filter === type); });
  var items = document.querySelectorAll('.timeline-item.milestone');
  items.forEach(function(item) {
    if (type === 'all') { item.classList.remove('hidden'); return; }
    var dtype = item.getAttribute('data-type');
    item.classList.toggle('hidden', dtype !== type);
  });
  /* Hide month dividers with no visible milestones */
  document.querySelectorAll('.month-divider').forEach(function(div) {
    var sib = div.nextElementSibling;
    var hasVisible = false;
    while (sib && !sib.classList.contains('month-divider')) {
      if (!sib.classList.contains('hidden')) { hasVisible = true; break; }
      sib = sib.nextElementSibling;
    }
    div.style.display = hasVisible ? '' : 'none';
  });
}
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

    {% if key contains "game_" %}
      {% assign icon = "&#127918;" %}{% assign mclass = "ms-game" %}
      {% assign rest = key | remove_first: "game_" %}
      {% if rest contains "_ep_" %}
        {% assign parts = rest | split: "_ep_" %}
        {% assign gname = link_meta.series_name | default: parts[0] %}
        {% capture d %}{{ parts[1] }} episodes in {{ gname }}{% endcapture %}{% assign display = d %}
      {% elsif rest contains "_upload_" %}
        {% assign parts = rest | split: "_upload_" %}
        {% assign gname = link_meta.series_name | default: parts[0] %}
        {% capture d %}{{ parts[1] }} hours uploaded in {{ gname }}{% endcapture %}{% assign display = d %}
      {% elsif rest contains "_started" %}
        {% assign g = rest | remove: "_started" %}
        {% assign mclass = "ms-started" %}
        {% assign started_meta = milestones.links[key] %}
        {% if started_meta.series_name %}
          {% capture d %}{{ started_meta.series_name }} ({{ g }}) started{% endcapture %}{% assign display = d %}
        {% elsif started_meta.icon %}
          {% capture d %}{{ g }} series started{% endcapture %}{% assign display = d %}
        {% else %}
          {% capture d %}{{ g }} series started{% endcapture %}{% assign display = d %}
        {% endif %}
      {% elsif rest contains "_views_" %}
        {% assign parts = rest | split: "_views_" %}
        {% assign gname = link_meta.series_name | default: parts[0] %}
        {% capture d %}{{ parts[1] }} views across {{ gname }}{% endcapture %}{% assign display = d %}
      {% elsif rest contains "_hours_" %}
        {% assign parts = rest | split: "_hours_" %}
        {% assign gname = link_meta.series_name | default: parts[0] %}
        {% capture d %}{{ parts[1] }} hours watched in {{ gname }}{% endcapture %}{% assign display = d %}
      {% elsif rest contains "_return_" %}
        {% assign parts = rest | split: "_return_" %}
        {% assign gname = link_meta.series_name | default: parts[0] %}
        {% capture d %}Back to {{ gname }} after {{ parts[1] }} days{% endcapture %}{% assign display = d %}
      {% endif %}
      {% assign game_slug = rest | split: "_" | first | slugify %}
      {% assign link = "/games#" | append: game_slug %}
    {% elsif key contains "series_" %}
      {% assign icon = "&#127918;" %}{% assign mclass = "ms-game" %}
      {% assign rest = key | remove_first: "series_" %}
      {% if rest contains "_views_" %}
        {% assign parts = rest | split: "_views_" %}
        {% capture d %}{{ parts[1] }} views in {{ parts[0] }}{% endcapture %}{% assign display = d %}
      {% elsif rest contains "_hours_" %}
        {% assign parts = rest | split: "_hours_" %}
        {% capture d %}{{ parts[1] }} hours watched in {{ parts[0] }}{% endcapture %}{% assign display = d %}
      {% elsif rest contains "_upload_" %}
        {% assign parts = rest | split: "_upload_" %}
        {% capture d %}{{ parts[1] }} hours uploaded in {{ parts[0] }}{% endcapture %}{% assign display = d %}
      {% elsif rest contains "_return_" %}
        {% assign parts = rest | split: "_return_" %}
        {% capture d %}Back to {{ parts[0] }} after {{ parts[1] }} days{% endcapture %}{% assign display = d %}
      {% endif %}
    {% elsif key contains "age_" %}
      {% assign icon = "&#127800;" %}{% assign mclass = "ms-age" %}{% assign link = "/" %}
      {% assign display = key | remove: "age_" | append: " days old" %}
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
      {% capture d %}{{ val }}-week upload streak{% endcapture %}{% assign display = d %}
    {% elsif key contains "video_first_likes_" %}
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
    {% elsif key contains "youtube_hours_" %}
      {% assign icon = "&#9200;" %}{% assign mclass = "ms-hours" %}{% assign link = "/videos" %}
      {% assign val = key | remove: "youtube_hours_" %}
      {% capture d %}{{ val }} hours watched on YouTube{% endcapture %}{% assign display = d %}
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

    {% if key contains "video_first_" and link_meta.text %}
      {% capture d %}First video to {{ val }} views: {{ link_meta.text }}{% endcapture %}{% assign display = d %}
    {% elsif key contains "_ep_" and link_meta.override %}
      {% assign display = link_meta.override %}
    {% elsif link_meta.msg %}
      {% assign display = link_meta.msg %}
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