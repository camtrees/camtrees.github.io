---
title: New Hub Request
layout: default
parent: New Data Requests
grand_parent: CAM Staff Pages
---

# {{ page.title }}

Use this form to request a new CAM Hub. The CAMTREES Database Administrator will
review the information before anything is added to the database.

{% comment %}
The questions and labels live in _data/request_forms.yml. Keeping this page
small makes all New Data Request pages consistent and easier to maintain.
{% endcomment %}
{% assign request_form = site.data.request_forms.new_hub %}
{% include data_request_form.html form=request_form %}
