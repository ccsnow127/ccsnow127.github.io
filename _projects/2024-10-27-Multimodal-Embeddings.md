---
layout: page
title: Multimodal RAG (1)
description: Multimodal Embeddings 
img: assets/img/Multimodal/arc-lmm-rag.png
importance: 1
category: LMM
related_publications: true
---

{::nomarkdown}
{% assign jupyter_path = "assets/jupyter/L2_Multimodal_Embeddings.ipynb" | relative_url %}
{% capture notebook_exists %}{% file_exists assets/jupyter/L2_Multimodal_Embeddings.ipynb %}{% endcapture %}
{% if notebook_exists == "true" %}
{% jupyter_notebook jupyter_path %}
{% else %}

<p>Sorry, the notebook you are looking for does not exist.</p>
{% endif %}
{:/nomarkdown}
