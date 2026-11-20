# Django busca los modelos en este archivo. Los modelos reales viven en
# infrastructure/models/ (adaptador secundario, un archivo por tabla);
# aquí solo se importan para que Django los registre.
# El panel de administración se configura en la semana 3.
from veterinaria.infrastructure.models import *  # noqa: F401,F403
