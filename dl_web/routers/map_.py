import json
import logging

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse


from dl_web.core.templates import templates
from dl_web.data_access.digital_land_queries import fetch_datasets_with_typology
from dl_web.data_access.entity_queries import fetch_entity_count


router = APIRouter()
logger = logging.getLogger(__name__)


async def filter_no_data(datasets):
    active_datasets_response = await fetch_entity_count()
    active_datasets = {d[0]: d[1] for d in active_datasets_response["rows"]}

    return [datasets[d] for d in datasets.keys() if d in active_datasets.keys()]


@router.get("/", response_class=HTMLResponse)
async def get_map(request: Request):
    geography_datasets = await fetch_datasets_with_typology("geography")
    active_geography_datasets = await filter_no_data(geography_datasets)

    for dataset in active_geography_datasets:
        print(dataset["name"], dataset["paint_options"])
        if dataset["paint_options"] != "":
            dataset["paint_options"] = json.loads(dataset["paint_options"])

    return templates.TemplateResponse(
        "national-map.html", {"request": request, "layers": active_geography_datasets}
    )
