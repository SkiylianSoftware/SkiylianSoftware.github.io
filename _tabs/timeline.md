---
layout: page
icon: "fa-solid fa-timeline"
title: Timeline
order: 8
permalink: /timeline/
---

{% assign history = site.data.history %}
{% if history and history.size > 0 %}

<div class="chart-container">
  <canvas id="growthChart"></canvas>
</div>

<div class="chart-controls">
  <button class="chart-btn active" onclick="toggleMetric('subs')" id="btn-subs">Subscribers</button>
  <button class="chart-btn" onclick="toggleMetric('views')" id="btn-views">Views</button>
  <button class="chart-btn" onclick="toggleMetric('videos')" id="btn-videos">Videos</button>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<script>
var history = {{ history | jsonify }};
var dates = history.map(function(h) { return h.date; });
var subsData = history.map(function(h) { return h.subs; });
var viewsData = history.map(function(h) { return h.views; });
var videosData = history.map(function(h) { return h.videos; });

var ctx = document.getElementById('growthChart').getContext('2d');
var chart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: dates,
    datasets: [{
      label: 'Subscribers',
      data: subsData,
      borderColor: '#2dd4bf',
      backgroundColor: 'rgba(45,212,191,0.05)',
      fill: true,
      tension: 0.3,
      pointRadius: 2,
      pointHoverRadius: 6,
      borderWidth: 2,
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: 'rgba(13,13,30,0.9)',
        titleColor: '#c8c8d4',
        bodyColor: '#2dd4bf',
        borderColor: 'rgba(45,212,191,0.3)',
        borderWidth: 1,
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
  var data, label, color;
  if (metric === 'subs') { data = subsData; label = 'Subscribers'; color = '#2dd4bf'; }
  else if (metric === 'views') { data = viewsData; label = 'Views'; color = '#c084fc'; }
  else { data = videosData; label = 'Videos'; color = '#fbbf24'; }
  chart.data.datasets[0].data = data;
  chart.data.datasets[0].label = label;
  chart.data.datasets[0].borderColor = color;
  chart.data.datasets[0].backgroundColor = color.replace(')', ',0.05)').replace('rgb', 'rgba');
  chart.update();
}
</script>

<h2 style="margin-top:2rem;font-size:1rem;">Milestones</h2>
<div class="timeline">
  {% for h in history %}
    {% assign milestone = nil %}
    {% if h.subs == 100 %}{% assign milestone = "100 subscribers!" %}
    {% elsif h.subs == 500 %}{% assign milestone = "500 subscribers!" %}
    {% elsif h.subs == 1000 %}{% assign milestone = "1,000 subscribers!" %}
    {% elsif h.views == 1000 %}{% assign milestone = "1,000 views!" %}
    {% elsif h.views == 10000 %}{% assign milestone = "10,000 views!" %}
    {% endif %}
    {% if milestone %}
      <div class="timeline-item milestone">
        <span class="tl-date">{{ h.date }}</span>
        <span class="tl-icon">&#11088;</span>
        <span class="tl-text">{{ milestone }} ({{ h.subs }} subs, {{ h.views }} views)</span>
      </div>
    {% else %}
      <div class="timeline-item">
        <span class="tl-date">{{ h.date }}</span>
        <span class="tl-dot"></span>
        <span class="tl-text">{{ h.subs }} subs &middot; {{ h.views }} views &middot; {{ h.videos }} videos</span>
      </div>
    {% endif %}
  {% endfor %}
</div>

{% else %}
  <p>No historical data yet. Data will appear once the tracking pipeline runs a few times.</p>
{% endif %}

<style>
.chart-container {
  width: 100%;
  height: 300px;
  margin: 1.5rem 0;
  padding: 1rem;
  background: var(--card-bg, #1e1e1e);
  border: 1px solid rgba(45,212,191,0.1);
  border-radius: 10px;
}
.chart-controls {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}
.chart-btn {
  padding: 0.3rem 0.75rem;
  border-radius: 6px;
  border: 1px solid rgba(45,212,191,0.2);
  background: transparent;
  color: #8888aa;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.15s;
}
.chart-btn:hover { border-color: rgba(45,212,191,0.5); color: #c8c8d4; }
.chart-btn.active { background: rgba(45,212,191,0.15); border-color: #2dd4bf; color: #2dd4bf; }

.timeline {
  position: relative;
  margin: 1rem 0;
  padding-left: 2rem;
}
.timeline::before {
  content: "";
  position: absolute;
  left: 0.7rem;
  top: 0;
  bottom: 0;
  width: 2px;
  background: rgba(45,212,191,0.15);
}
.timeline-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0;
  font-size: 0.85rem;
}
.timeline-item.milestone {
  background: rgba(45,212,191,0.06);
  border-radius: 8px;
  padding: 0.5rem 0.75rem;
  margin: 0.25rem 0;
}
.tl-date { min-width: 6em; opacity: 0.6; font-size: 0.8rem; }
.tl-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: rgba(45,212,191,0.3);
  flex-shrink: 0;
}
.tl-icon { flex-shrink: 0; }
.tl-text { opacity: 0.85; }
.milestone .tl-text { color: #2dd4bf; font-weight: 500; }
</style>