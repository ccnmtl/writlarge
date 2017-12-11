# Uses django-extensions and graphviz to render a model representation
# Not including the setup in the master branch, as it is not really needed
# http://django-extensions.readthedocs.io/en/latest/graph_models.html

./manage.py graph_models main -g -v 0 -X User -x created_by,last_modified_by,created_at,modified_at -o scripts/models.png