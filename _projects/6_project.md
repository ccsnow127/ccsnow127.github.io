---
layout: page
title: Large Multimodal Model Prompting with Gemini
description: Multimodal Prompting and Parameter Control
img: assets/img/Multimodal/gemeni-intro.png
importance: 1
category: LMM
related_publications: true
---

{::nomarkdown}
{% assign jupyter_path = "L2_colab_prompting_and_parameters.ipynb" | relative_url %}
{% capture notebook_exists %}{% file_exists L2_colab_prompting_and_parameters.ipynb %}{% endcapture %}
{% if notebook_exists == "true" %}
{% jupyter_notebook jupyter_path %}
{% else %} 

<p>Sorry, the notebook you are looking for does not exist.</p>
{% endif %}
{:/nomarkdown}
