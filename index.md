---
layout: default
title: Home
---

# LLM Dev Highlights

Welcome to the LLM Dev Highlights. Below are the daily development reports.

## vLLM Reports

<ul>
  {% assign reports = site.pages | where_exp: "item", "item.path contains 'logs/vllm/daily/'" | sort: 'date' | reverse %}
  {% for report in reports %}
    <li>
      <a href="{{ report.url | relative_url }}">{{ report.title | default: report.name }}</a>
      <span style="color: #888; font-size: 0.85em; margin-left: 10px;">
        {{ report.date | date: "%Y-%m-%d" }}
      </span>
    </li>
  {% endfor %}
</ul>
