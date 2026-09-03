/*
 * History page chart (Chart.js) and milestone timeline filter.
 * Requires Chart.js (loaded via CDN before this script) and
 * window.HIST_DATA (set by a small inline script in history.md).
 */
(function() {
  var histData;

  function pluck(entry, platform, field) {
    return (entry[platform] && entry[platform][field]) || 0;
  }

  function toggleMetric(metric) {
    var btns = document.querySelectorAll('.chart-btn');
    btns.forEach(function(b) { b.classList.remove('active'); });
    var active = document.getElementById('btn-' + metric);
    if (active) active.classList.add('active');
    if (!window.__chart) return;
    window.__chart.data.labels = window.__labelsByMetric[metric] || window.__dates;
    window.__chart.data.datasets = window.__allMetrics[metric] || [];
    window.__chart.update();
  }

  window.toggleMetric = toggleMetric;

  function filterMilestones(type) {
    document.querySelectorAll('.ms-filter-btn').forEach(function(b) {
      b.classList.toggle('active', b.getAttribute('data-filter') === type);
    });
    var items = document.querySelectorAll('.timeline-item.milestone');
    items.forEach(function(item) {
      if (type === 'all') { item.classList.remove('hidden'); return; }
      item.classList.toggle('hidden', item.getAttribute('data-type') !== type);
    });
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

  window.filterMilestones = filterMilestones;

  document.addEventListener('DOMContentLoaded', function() {
    if (typeof Chart === 'undefined' || !window.HIST_DATA) return;
    histData = window.HIST_DATA;

    Chart.defaults.elements.line.tension = 0.3;
    Chart.defaults.elements.point.radius = 0;

    var dates = histData.map(function(h) { return h.date; });
    window.__dates = dates;

    function makeDataset(label, data, color) {
      return {
        label: label,
        data: data,
        borderColor: color,
        backgroundColor: color.replace(')', ',0.05)').replace('rgb', 'rgba'),
      };
    }

    var audienceDatasets = [
      makeDataset('YouTube', histData.map(function(h) { return pluck(h, 'youtube_main', 'subs'); }), '#ff4444'),
      makeDataset('VODs', histData.map(function(h) { return pluck(h, 'youtube_vods', 'subs'); }), '#ff8844'),
      makeDataset('Twitch', histData.map(function(h) { return pluck(h, 'twitch', 'followers'); }), '#a970ff'),
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
      makeDataset('YouTube', histData.map(function(h) { return pluck(h, 'youtube_main', 'views'); }), '#ff4444'),
      makeDataset('VODs', histData.map(function(h) { return pluck(h, 'youtube_vods', 'views'); }), '#ff8844'),
      makeDataset('Twitch', histData.map(function(h) { return pluck(h, 'twitch', 'views'); }), '#a970ff'),
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
      makeDataset('YouTube', histData.map(function(h) { return pluck(h, 'youtube_main', 'videos'); }), '#ff4444'),
      makeDataset('VODs', histData.map(function(h) { return pluck(h, 'youtube_vods', 'videos'); }), '#ff8844'),
    ];
    contentDatasets.push({
      label: 'Total',
      data: histData.map(function(h) { return (pluck(h, 'youtube_main', 'videos') || 0) + (pluck(h, 'youtube_vods', 'videos') || 0); }),
      borderColor: '#2dd4bf', backgroundColor: 'rgba(45,212,191,0.08)',
      borderWidth: 3, pointRadius: 0,
    });

    var ordersDatasets = window.HIST_ORDERS ? [
      makeDataset('Fourthwall', histData.map(function(h) { return pluck(h, 'fourthwall', 'orders'); }), '#c084fc'),
    ] : [];

    var githubDatasets = window.HIST_GITHUB ? [
      makeDataset('Stars', histData.map(function(h) { return pluck(h, 'github', 'stars'); }), '#2dd4bf'),
      makeDataset('Followers', histData.map(function(h) { return pluck(h, 'github', 'followers'); }), '#888'),
      makeDataset('Forks', histData.map(function(h) { return pluck(h, 'github', 'forks'); }), '#c084fc'),
    ] : [];

    var hasLikes = histData.some(function(h) { return pluck(h, 'youtube_main', 'likes') > 0; });
    var hasComments = histData.some(function(h) { return pluck(h, 'youtube_main', 'comments') > 0; });

    /* Cumulative watch time (hours) */
    var watchData = (function() {
      var run = 0;
      return histData.map(function(h) {
        var an = h._analytics;
        if (an && an.watch_time_minutes) run += an.watch_time_minutes;
        return Math.round(run / 60);
      });
    })();

    /* Uploads per month */
    var monthUploads = (function() {
      var months = [];
      var totals = [];
      var lastMonth = null;
      var monthVideos = 0;
      var prev = 0;
      histData.forEach(function(h) {
        var v = pluck(h, 'youtube_main', 'videos');
        var m = (h.date || '').slice(0, 7);
        if (!m) return;
        if (m !== lastMonth) {
          if (lastMonth !== null) { months.push(lastMonth); totals.push(monthVideos); }
          lastMonth = m;
          monthVideos = 0;
        }
        monthVideos += v - prev;
        prev = v;
      });
      if (lastMonth !== null) { months.push(lastMonth); totals.push(monthVideos); }
      return { months: months, totals: totals };
    })();

    window.__allMetrics = {
      audience: audienceDatasets,
      views: viewsDatasets,
      content: contentDatasets,
      orders: ordersDatasets,
      github: githubDatasets,
    };
    if (hasLikes) {
      window.__allMetrics.likes = [
        makeDataset('YouTube', histData.map(function(h) { return pluck(h, 'youtube_main', 'likes'); }), '#ff4444'),
        makeDataset('VODs', histData.map(function(h) { return pluck(h, 'youtube_vods', 'likes'); }), '#ff8844'),
        {
          label: 'Total',
          data: histData.map(function(h) { return (pluck(h, 'youtube_main', 'likes') || 0) + (pluck(h, 'youtube_vods', 'likes') || 0); }),
          borderColor: '#2dd4bf', backgroundColor: 'rgba(45,212,191,0.08)',
          borderWidth: 3, pointRadius: 0,
        },
      ];
    }
    if (hasComments) {
      window.__allMetrics.comments = [
        makeDataset('YouTube', histData.map(function(h) { return pluck(h, 'youtube_main', 'comments'); }), '#ff4444'),
        makeDataset('VODs', histData.map(function(h) { return pluck(h, 'youtube_vods', 'comments'); }), '#ff8844'),
        {
          label: 'Total',
          data: histData.map(function(h) { return (pluck(h, 'youtube_main', 'comments') || 0) + (pluck(h, 'youtube_vods', 'comments') || 0); }),
          borderColor: '#2dd4bf', backgroundColor: 'rgba(45,212,191,0.08)',
          borderWidth: 3, pointRadius: 0,
        },
      ];
    }
    window.__allMetrics.watch = [
      { label: 'Watch Time (h)', data: watchData, borderColor: '#ff8844', backgroundColor: 'rgba(255,136,68,0.05)' },
    ];
    window.__allMetrics.uploads = [
      { label: 'Uploads', data: monthUploads.totals, borderColor: '#2dd4bf', backgroundColor: 'rgba(45,212,191,0.08)', borderWidth: 3, pointRadius: 0 },
    ];

    window.__labelsByMetric = {
      audience: dates,
      views: dates,
      content: dates,
      orders: dates,
      github: dates,
      likes: dates,
      comments: dates,
      watch: dates,
      uploads: monthUploads.months,
    };

    var ctx = document.getElementById('growthChart');
    if (!ctx) return;
    window.__chart = new Chart(ctx.getContext('2d'), {
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
          },
        },
        scales: {
          x: {
            ticks: { color: '#8888aa', maxTicksLimit: 12 },
            grid: { color: 'rgba(45,212,191,0.05)' },
          },
          y: {
            beginAtZero: true,
            ticks: { color: '#8888aa' },
            grid: { color: 'rgba(45,212,191,0.05)' },
          },
        },
      },
    });

    /* Upload heatmap: GitHub-style grid of last 12 months */
    (function renderHeatmap() {
      var container = document.getElementById('upload-heatmap');
      if (!container || !histData || histData.length < 2) return;

      var data = histData;
      var dayVideos = {};
      var prev = 0;
      data.forEach(function(e) {
        var date = (e.date || '').slice(0, 10);
        if (!date) return;
        var v = pluck(e, 'youtube_main', 'videos');
        var delta = v - prev;
        if (delta < 0) delta = 0;
        dayVideos[date] = delta;
        prev = v;
      });

      var now = new Date();
      now.setHours(0, 0, 0, 0);
      var end = new Date(now);
      end.setDate(end.getDate() - (end.getDay() + 6) % 7);
      var start = new Date(end);
      start.setFullYear(start.getFullYear() - 1);
      start.setDate(start.getDate() - start.getDay());

      var maxVideos = 0;
      var cells = {};
      for (var d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
        var ds = d.toISOString().slice(0, 10);
        var count = dayVideos[ds] || 0;
        if (count > maxVideos) maxVideos = count;
        cells[ds] = count;
      }

      if (maxVideos === 0) { container.textContent = 'No upload data yet.'; return; }

      var monthGroups = {};
      for (var d2 = new Date(start); d2 <= end; d2.setDate(d2.getDate() + 1)) {
        var ds2 = d2.toISOString().slice(0, 10);
        var m = ds2.slice(0, 7);
        if (!monthGroups[m]) monthGroups[m] = [];
        monthGroups[m].push(ds2);
      }

      var sortedMonths = Object.keys(monthGroups).sort();
      sortedMonths.forEach(function(mon) {
        var monthDiv = document.createElement('div');
        monthDiv.className = 'heatmap-month';

        var label = document.createElement('div');
        label.className = 'heatmap-month-label';
        var parts = mon.split('-');
        label.textContent = new Date(parts[0], parts[1] - 1).toLocaleString('default', { month: 'short' });
        monthDiv.appendChild(label);

        var days = monthGroups[mon];
        days.forEach(function(ds) {
          var count = cells[ds] || 0;
          var cell = document.createElement('span');
          cell.className = 'heatmap-cell';
          cell.setAttribute('data-date', ds);
          cell.title = ds + ': ' + count + ' video' + (count !== 1 ? 's' : '');
          if (count > 0) {
            var intensity = 0.1 + (count / maxVideos) * 0.8;
            cell.style.background = 'rgba(45,212,191,' + intensity + ')';
          }
          monthDiv.appendChild(cell);
        });

        container.appendChild(monthDiv);
      });
    })();
  });
})();
