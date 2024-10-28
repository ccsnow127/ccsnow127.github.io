---
layout: page
title: Multimodal RAG (3)
description: Multimodal Retrieval from Vector Stores
img: assets/img/Multimodal/arc-lmm-rag.png
importance: 1
category: LMM
related_publications: true
---

{::nomarkdown}
{% assign jupyter_path = "assets/jupyter/L4_Multimodal_Retrieval_from_Vector_Stores.ipynb" | relative_url %}
{% capture notebook_exists %}{% file_exists assets/jupyter/L4_Multimodal_Retrieval_from_Vector_Stores.ipynb %}{% endcapture %}
{% if notebook_exists == "true" %}
{% jupyter_notebook jupyter_path %}
{% else %}

<p>Sorry, the notebook you are looking for does not exist.</p>
{% endif %}
{:/nomarkdown}