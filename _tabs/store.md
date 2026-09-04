---
layout: page
icon: "fa-solid fa-store"
title: Store
order: 12
permalink: /store/
group: media
---

{% include banner.html %}

{% assign store = site.data.fourthwall %}
{% if store.products and store.products.size > 0 %}
<div class="store-intro">
  <p>Merch straight from the channel, powered by Fourthwall. Every order keeps the trains running.</p>
  {% if store.total_orders %}
  <p class="store-metric-card"><i class="fas fa-box"></i> {{ store.total_orders }} orders shipped</p>
  {% endif %}
</div>

<div class="product-grid">
  {% for p in store.products %}
  <a href="{{ p.url }}" target="_blank" rel="noopener" class="product-card btn">
    {% if p.thumbnail %}<div class="product-thumb" style="background-image: url('{{ p.thumbnail }}')"></div>{% endif %}
    <div class="product-info">
      <span class="product-name">{{ p.name }}</span>
      {% if p.price %}<span class="product-price">{{ p.price }} {{ p.currency }}</span>{% endif %}
    </div>
  </a>
  {% endfor %}
</div>

<p class="text-center"><a href="https://store.skiylia.dev" target="_blank" rel="noopener" class="btn">Open the full store &rarr;</a></p>
{% else %}
<p class="empty-state">The store shelf is being restocked. Check back soon!</p>
{% endif %}