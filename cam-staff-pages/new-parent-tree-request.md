---
title: New Parent Tree Request
layout: default
parent: New Data Requests
grand_parent: CAM Staff Pages
---

# {{ page.title }}

Use this form to request a new Parent Tree. The CAMTREES Database Administrator
will review the information before anything is added to the database.

{% comment %}
The questions and labels live in _data/request_forms.yml. The shared Requested
By section lives in _data/request_form_sections.yml.
{% endcomment %}
{% assign request_form = site.data.request_forms.new_parent_tree %}
{% include data_request_form.html form=request_form %}
