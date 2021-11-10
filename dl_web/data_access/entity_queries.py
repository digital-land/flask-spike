import json
import logging

from digital_land.view_model import JSONQueryHelper
from decimal import Decimal
from dl_web.core.utils import fetch
from dl_web.search.enum import EntriesOption, DateOption, GeometryRelation
from dl_web.settings import get_settings

logger = logging.getLogger(__name__)


# TBD: replace string concatenation with sqlite3 ? expressions ..
def sqlescape(s):
    if s is None:
        return ""
    return s.translate(
        s.maketrans(
            {
                "'": "''",
                '"': "",
                "\\": "",
                "%": "",
                "\0": "",
                "\n": " ",
                "\r": " ",
                "\x08": " ",
                "\x09": " ",
                "\x1a": " ",
            }
        )
    )


class EntityJson:

    # TODO add the following?
    # "organisation_entity",
    # "prefix",

    fields = [
        "entity",
        "name",
        "reference",
        "dataset",
        "json",
        "entry_date",
        "start_date",
        "end_date",
        "typology",
    ]

    @staticmethod
    def to_json(data):
        data_dict = {}
        for key, val in data.items():
            if key in __class__.fields and val:
                data_dict[key] = val
        if "geojson" in data and data.get("geojson") is not None:
            geojson = json.loads(data["geojson"])
            properties = {}
            for field in __class__.fields:
                if field in data and field != "json" and data.get(field) is not None:
                    # TODO - skipping the json for now, but hould we unpack all the json as properties?
                    properties[field] = data[field]
            geojson["properties"] = properties
            data_dict["geojson"] = geojson
        return data_dict


class EntityQuery:
    lists = ["typology", "dataset", "entity", "prefix", "reference"]

    def __init__(self, params: dict = {}):
        datasette_url = get_settings().DATASETTE_URL
        self.url_base = f"{datasette_url}/entity"
        self.params = self.normalised_params(params)

    def normalised_params(self, params):
        # remove empty parameters
        params = {k: v for k, v in params.items() if v is not None}

        # sort/unique list parameters
        for lst in self.lists:
            if lst in params:
                params[lst] = sorted(set(params[lst]))

        return params

    def where_column(self, params):
        sql = where = ""
        for col in ["typology", "dataset", "entity", "prefix", "reference"]:
            if col in params and params[col]:
                sql += (
                    where
                    + "("
                    + " OR ".join(
                        [
                            "entity.%s = '%s'" % (col, sqlescape(value))
                            for value in params[col]
                        ]
                    )
                    + ")"
                )
                where = " AND "
        return sql

    def where_curie(self, params):
        sql = where = ""
        if "curie" in params and params["curie"]:
            sql += (
                where
                + "("
                + " OR ".join(
                    [
                        "(entity.prefix = '{c[0]}' AND entity.reference = '{c[1]}')".format(
                            c=c.split(":") + ["", ""]
                        )
                        for c in params["curie"]
                    ]
                )
                + ")"
            )
        return sql

    def where_entries(self, params):
        option = params.get("entries", EntriesOption.all)
        if option == EntriesOption.current:
            return " entity.end_date is ''"
        if option == EntriesOption.historical:
            return " entity.end_date is not ''"

    def get_date(self, params, param):
        if param in params:
            d = params[param]
            params[param + "_year"] = d.year
            params[param + "_month"] = d.month
            params[param + "_day"] = d.day
            return d.isoformat()

        try:
            year = int(params.get(param + "_year", 0))
            if year:
                month = int(params.setdefault(param + "_month", 1))
                day = int(params.setdefault(param + "_day", 1))
                return "%04d-%02d-%02d" % (year, month, day)
        except ValueError:
            return

    def where_date(self, params):
        sql = where = ""
        for col in ["start_date", "end_date", "entry_date"]:
            param = "entry_" + col
            value = self.get_date(params, param)
            match = params.get(param + "_match", "")
            if match:
                if match == DateOption.empty:
                    sql += where + " entity.%s = ''" % col
                    where = " AND "
                elif value:
                    operator = {
                        DateOption.match: "=",
                        DateOption.before: "<",
                        DateOption.since: ">=",
                    }[match]
                    sql += where + "(entity.%s != '' AND entity.%s %s '%s') " % (
                        col,
                        col,
                        operator,
                        sqlescape(value),
                    )
                    where = " AND "
        return sql

    # a single point maybe provided as longitude and latitude params
    def get_point(self, params):
        for field in ["longitude", "latitude"]:
            try:
                params[field] = "%.6f" % round(Decimal(params[field]), 6)
            except (KeyError, TypeError):
                return

        return "POINT(%s %s)" % (params["longitude"], params["latitude"])

    def where_geometry(self, params):
        values = []

        point = self.get_point(params)
        if point:
            values.append("GeomFromText('%s')" % sqlescape(point))

        for geometry in params.get("geometry", []):
            values.append("GeomFromText('%s')" % sqlescape(geometry))

        for entity in params.get("geometry_entity", []):
            values.append(
                "(SELECT geometry_geom from geometry where entity = '%s')"
                % sqlescape(entity)
            )

        for reference in params.get("geometry_reference", []):
            values.append(
                """
                  (SELECT geometry_geom from geometry where entity =
                      (SELECT entity from entity where reference = '%s' group by entity))
                """
                % sqlescape(reference)
            )

        if not values:
            return

        sql = ""
        where = "entity.entity = geometry.entity AND ("
        match = params.get("geometry_match", GeometryRelation.within).value
        for value in values:
            sql += (
                where
                + "(geometry.geometry_geom IS NOT NULL AND %s(geometry.geometry_geom, %s))"
                % (match, value)
            )
            where = " OR "
            sql += where + "%s(geometry.point_geom, %s)" % (match, value)
        return sql + ")"

    def pagination(self, params):
        sql = ""
        if params.get("next_entity", ""):
            sql += " entity.entity > %s" % (sqlescape(str(params["next_entity"])))
        sql += " ORDER BY entity.entity"
        sql += " LIMIT %s" % (sqlescape(str(params.get("limit", 10))))
        return sql

    def sql(self, count=False):
        if count:
            sql = "SELECT DISTINCT COUNT(*) as _count"
        else:
            sql = "SELECT entity.*, geometry.geojson"
        sql += (
            " FROM entity LEFT OUTER JOIN geometry on entity.entity = geometry.entity"
        )

        where = " WHERE "
        for part in [
            "column",
            "curie",
            "entries",
            "date",
            "geometry",
        ]:
            clause = getattr(self, "where_" + part)(self.params)
            if clause:
                sql += where + clause
                where = " AND "

        sql += self.pagination(self.params)
        print(sql)
        return sql

    def url(self, sql):
        return JSONQueryHelper.make_url(self.url_base + ".json", params={"sql": sql})

    def response(self, data, count):
        results = []
        for row in data.get("rows", []):
            results.append(EntityJson.to_json(row))

        response = {
            "query": self.params,
            "count": count,
            "results": results,
        }
        return response

    def execute(self):
        r = JSONQueryHelper.get(self.url(self.sql(count=True))).json()
        if "rows" not in r or not len(r["rows"]):
            count = 0
        else:
            count = r["rows"][0]["_count"]
        data = JSONQueryHelper.get(self.url(self.sql())).json()
        return self.response(data, count)

    # TBD: remove, doesn't belong here ..
    # I think it could belong here. It's a bit like the sqlalchemy api
    # where the Model.get(id) returns the thing by primary key which you get for free
    async def get(self, entity_id: int):
        sql = f"SELECT * FROM entity e LEFT OUTER JOIN geometry g on e.entity = g.entity WHERE (e.entity = {entity_id})"
        url = JSONQueryHelper.make_url(f"{self.url_base}.json", params={"sql": sql})
        logger.info(f"get entity: {url}")
        resp = await fetch(url)
        if len(resp["rows"]) > 0:
            e = resp["rows"][0]
            return EntityJson.to_json(e)
        else:
            return None
