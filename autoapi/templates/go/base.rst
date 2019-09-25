{% if obj.display %}

.. {{ obj.ref_type }}:: {{ obj.name }}

{% macro render() %}{{ obj.docstring }}{% endmacro %}
{{ render()|indent(3) }}

{% if obj.children %}
    {% for child in obj.children|sort %}
{% macro render_child() %}{{ child.render() }}{% endmacro %}
{{ render_child()|indent(4) }}
    {% endfor %}
{% endif %}

{% endif %}
