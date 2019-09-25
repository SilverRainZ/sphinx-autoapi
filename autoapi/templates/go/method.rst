 {% set ns = namespace() %}
 {% set argjoin = joiner(', ') %}

 {# Creating the parameters line #}
 {% set ns.params = '' %}
 {% for param in obj.parameters %}
     {% set ns.params = ns.params ~ argjoin() ~ param.name ~ ' ' ~ param.type %}
 {% endfor %}

 {# Creating the results line #}
 {% set ns.results = '' %}
 {% for result in obj.results %}
     {% set ns.results = ns.results ~ argjoin() ~ result.name ~ ' ' ~ result.type %}
 {% endfor %}

.. {{ obj.ref_type }}:: ({{ obj.receiver }}) {{ obj.name }}({{ ns.params }}) (ns.results)

{% macro render() %}{{ obj.docstring }}{% endmacro %}
{{ render()|indent(4) }}

{# Don't define parameter description here, that can be done in the block
above #}
{% for param in obj.parameters %}
:param {{ param.name }}:
:type {{ param.name }}: {{ param.type }}
{% endfor %}

{% for result in obj.results %}
:rtype: {{ result.type }}
{% endfor %}
