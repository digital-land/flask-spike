import logging
from dataclasses import asdict
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from starlette.responses import JSONResponse, Response

from dl_web.core.models import GeoJSON
from dl_web.data_access.digital_land_queries import (
    fetch_typologies,
    fetch_datasets_with_theme,
    fetch_local_authorities,
)
from dl_web.data_access.entity_queries import EntityQuery
from dl_web.search.enum import Suffix

from dl_web.search.filters import (
    BaseFilters,
    DateFilters,
    SpatialFilters,
    PaginationFilters,
    FormatFilters,
)

from dl_web.core.resources import templates
from dl_web.core.utils import create_dict

router = APIRouter()
logger = logging.getLogger(__name__)


def _geojson_download(geojson: GeoJSON):
    response = Response(geojson.json())
    filename = f"{geojson.properties['entity']}.geojson"
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response


def _get_geojson(data):
    results = [item.geojson for item in data["results"]]
    return results


# The order of the router methods is important! This needs to go ahead of /{entity}
# @router.get("/{entity}.geojson", include_in_schema=False)
# async def get_entity_as_geojson(entity: int):
#     e = await EntityQuery().get(entity)
#     if e is not None and e.geojson is not None:
#         return _geojson_download(e.geojson)
#     else:
#         raise HTTPException(status_code=404, detail="entity not found")


async def get_entity(request: Request, entity: int, extension: Optional[Suffix] = None):
    e = await EntityQuery().get(entity)
    if e is not None:

        if extension is not None and extension.value == "json":
            return e

        if extension is not None and extension.value == "geojson":
            return e.geojson

        # TODO - update template - no longer fully works
        return templates.TemplateResponse(
            "entity.html",
            {
                "request": request,
                "row": e.dict(by_alias=True, exclude={"geojson"}),
                "entity": e.dict(by_alias=True, exclude={"geojson"}),
                "pipeline_name": e.dataset,
                "references": [],
                "breadcrumb": [],
                "schema": None,
                "typology": e.typology,
                "entity_prefix": "",
                "geojson_features": e.geojson if e.geojson is not None else None,
            },
        )
    else:
        raise HTTPException(status_code=404, detail="entity not found")


async def search_entities(
    request: Request,
    # filter entries
    base_filters: BaseFilters = Depends(BaseFilters),
    date_filters: DateFilters = Depends(DateFilters),
    spatial_filters: SpatialFilters = Depends(SpatialFilters),
    pagination_filters: PaginationFilters = Depends(PaginationFilters),
    format_filters: FormatFilters = Depends(FormatFilters),
    extension: Optional[Suffix] = None,
):
    base_params = asdict(base_filters)
    date_params = asdict(date_filters)
    spatial_params = asdict(spatial_filters)
    pagination_params = asdict(pagination_filters)
    format_params = asdict(format_filters)

    params = {
        **base_params,
        **date_params,
        **spatial_params,
        **pagination_params,
        **format_params,
    }

    query = EntityQuery(params=params)

    data = query.execute()

    if extension is not None and extension.value == "json":
        return data

    if extension is not None and extension.value == "geojson":
        return _get_geojson(data)

    # typology facet
    response = await fetch_typologies()
    typologies = [create_dict(response["columns"], row) for row in response["rows"]]
    # dataset facet
    response = await fetch_datasets_with_theme()
    dataset_results = [
        create_dict(response["columns"], row) for row in response["rows"]
    ]
    datasets = [d for d in dataset_results if d["dataset_active"]]
    # local-authority-district facet
    response = await fetch_local_authorities()
    local_authorities = [
        create_dict(response["columns"], row) for row in response["rows"]
    ]

    # default is HTML
    return templates.TemplateResponse(
        "search.html",
        {
            "request": request,
            "data": data,
            "datasets": datasets,
            "local_authorities": local_authorities,
            "typologies": typologies,
            "query": query,
            "active_filters": [
                filter_name
                for filter_name, values in query.params.items()
                if filter_name != "limit" and values is not None
            ],
        },
    )


# Route ordering in important. Match routes with extensions first
router.add_api_route(
    ".{extension}",
    endpoint=search_entities,
    response_class=JSONResponse,
    tags=["Search entity"],
)
router.add_api_route(
    "/",
    endpoint=search_entities,
    responses={
        200: {
            "content": {
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {},
                "application/zip": {},
                "application/x-qgis-project": {},
                "application/geo+json": {},
                "text/json": {},
                "text/csv": {},
                "text/turtle": {},
            },
            "description": "List of entities in one of a number of different formats.",
        }
    },
    response_class=HTMLResponse,
    include_in_schema=False,
)

router.add_api_route(
    "/{entity}.{extension}",
    get_entity,
    response_class=JSONResponse,
    tags=["Get entity"],
)
router.add_api_route(
    "/{entity}",
    endpoint=get_entity,
    response_class=HTMLResponse,
    include_in_schema=False,
)
