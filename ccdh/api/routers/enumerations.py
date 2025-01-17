from fastapi import APIRouter, HTTPException
from linkml_runtime.linkml_model import EnumDefinition, PermissibleValue
from linkml_runtime.dumpers.yaml_dumper import YAMLDumper
from starlette.responses import Response

from ccdh.api.utils import uri_to_curie
from ccdh.config import neo4j_graph
from ccdh.db.mdr_graph import MdrGraph

mdr_graph = MdrGraph(neo4j_graph())

router = APIRouter(
    prefix='/enumerations',
    tags=['Enumerations'],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get('/{name}',
            response_model_exclude_none=True,
            response_model_exclude_unset=True,
            response_class=Response,
            responses={
                200: {
                    "content": {
                        'application/x-yaml': {}
                    },
                    "description": "Return the Enumerations",
                }
            })
async def get_enumeration(name: str, value_only: bool = False) -> Response:
    if len(name.split('.')) != 3:
        raise HTTPException(status_code=404, detail='Enumeration not found.')
    system, entity, attribute = name.split('.')
    enum = EnumDefinition(name=name, description=f'Autogenerated Enumeration for {system} {entity} {attribute}')
    enum.permissible_values = []
    if value_only:
        values = mdr_graph.find_permissible_values_of(system, entity, attribute)
        for v in values:
            enum.permissible_values.append(PermissibleValue(text=v['pref_label'], description=v['description']))
    else:
        concepts, values = mdr_graph.find_concept_references_and_permissible_values_of(system, entity, attribute)
        for v in values:
            node_attributes = v['node_attributes']
            contexts = []
            for attr in node_attributes:
                contexts.append(f'{attr["system"]}.{attr["entity"]}.{attr["attribute"]}')
            extensions = {'CCDH:context': '; '.join(contexts)}
            pv = PermissibleValue(text=v['pref_label'], description=v['description'])
            enum.permissible_values.append(pv)
        for concept in concepts:
            concept = dict(concept['cr'])
            pv = PermissibleValue(meaning=uri_to_curie(concept['uri']), description=concept['designation'], text=concept['code'])
            enum.permissible_values.append(pv)
    return Response(content=YAMLDumper().dumps(enum), media_type="application/x-yaml")



