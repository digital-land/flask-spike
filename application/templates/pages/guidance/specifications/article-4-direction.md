**Version:** 1.2.2<br/>
**Published:** 11 September 2023

This is guidance on how to meet the [article 4 direction technical specification](https://digital-land.github.io/specification/specification/article-4-direction/).

---

There are 2 datasets you must provide for article 4 directions:

- [article 4 direction dataset](#{{ 'article 4 direction dataset' | slugify }})
- [article 4 direction area dataset](#{{ 'Article 4 direction area' | slugify }})

Format
------

You can provide data in one of these formats:

-   CSV
-   GeoJSON
-   GML
-   Geopackage

These may be uploaded to a single URL, or served via an OGC WFS or ArcGIS API.

Field names
-----------

You can provide fields names using hyphens, underscores or spaces.

For example:

- `start-date`
- `start_date`
- `start date`

These are all valid, and any uppercase characters will be converted to lowercase.

---

## Article 4 direction dataset

This dataset is about article 4 directions. These are directions from local planning authorities to withdraw specified permitted development rights across a defined area.

The dataset must contain at least one entry (row) for each article 4 direction.
It must containing the following fields (columns):

### reference

A reference or ID for each article 4 direction that is:

- unique within your dataset
- permanent - it doesn’t change when the dataset is updated

If you don’t use a reference already, you will need to create one. This can be a short set of letters or numbers.

Example: `A4D1`

### name

The official name of the article 4 direction.

Example: `Old Market`

### description

Optional short description of the article 4 direction’s purpose.

Example: The railways arches should not be demolished or have their use changed from commercial to residential.

### document-url

The URL of an authoritative order or notice designating the article 4 direction.

Example: `http://www.LPAwebsite.org.uk/article4direction1.pdf`

### documentation-url

The URL of the webpage on your website that introduces the document.

Each document should be linked to from a documentation webpage that includes a short description of the data and the document you’re linking to. Each article 4 direction should have a unique URL. This means you can create a separate page for each one, or you could list several on one page. If you do that, there must be a separate anchor link (fragment identifier) for each one.

This means each section of your page should have its own URL. Most publishing systems will allow you to use a hashtag to create the identifiers for each article 4 direction you list - as in the examples shown.

Example:

One article 4 direction per page:

`http://www.LPAwebsite.org.uk/data/article4directions/smithroad`

More than one article 4 direction per page with an anchor link for each one:

`http://www.LPAwebsite.org.uk/data/article4directions#smithroad`

`http://www.LPAwebsite.org.uk/data/article4directions#broadhousepark`

### notes

Optional text on how this data was made or produced, or how it can be interpreted.

### start-date

The date that the article 4 direction came into force, written in `YYYY-MM-DD` format.

Example: `1984-03-28`

### end-date

Where the article 4 direction is [no longer valid](https://standards.planning-data.dev/principles/#we-shouldn%E2%80%99t-delete-entries-in-a-register), this should be the date that it was no longer in effect, written in `YYYY-MM-DD` format. If this does not apply, leave the cell blank.

Example: `1999-01-20`

### entry-date

The date the entity was last updated.

If the entity has never been updated, enter the same date as start-date.

Write in `YYYY-MM-DD` format.

Example: `2022-12-20`

---

## Article 4 direction area

This dataset is about the geometry that each article 4 direction refers to.

The dataset must contain at least one entry (row) for each article 4 direction area.

It must containing the following fields (columns):

### reference

A reference or ID for each article 4 direction area that is:

- unique within your dataset
- permanent - it doesn’t change when the dataset is updated

If you don’t use a reference already, you will need to create one. This can be a short set of letters or numbers.

Example: `A4Da1`

### name

The official name of the article 4 direction.
Example: Old Market

### geometry

The boundary for the article 4 direction area as a single polygon or multipolygon value. All points in the polygon must be in the WGS84 coordinate reference system.

If you’re providing geometry in a CSV, geometry should be in well-known text (WKT).

Example: `MULTIPOLYGON (((1.188829 51.23478,1.188376 51.234909,1.188381 51.234917,1.187912 51.235022...`

If you’re providing geometry in a GeoJSON, GML or Geopackage, use the associated geometry format.

### uprn

If the geometry is the boundary of a building, you can provide the Unique Property Reference Number (UPRN). Find the UPRN on GeoPlace.

If you provide the UPRN, you must also provide the address text.

### address-text

If the geometry is the boundary of a building, you can provide the address of the article 4 direction, written as text.

If you provide the address text, you must also provide the UPRN.

Example: `100 High Street, Bath`

### article-4-direction

The reference for the article 4 direction used in the article 4 direction dataset.

Example: `A4D1`

### permitted-development-rights

A list of the permitted development rights withdrawn by the article 4 direction.

Separate the rights in the list using semicolons.

Only use rights from our [permitted development right dataset](https://www.planning.data.gov.uk/dataset/permitted-development-right). If the area withdraws a permitted development right that is not in our dataset, email [digitalland@communities.gov.uk](digitalland@communities.gov.uk).

Example: `3D;3M;11B`

### documentation-url

An optional URL of a document providing the authoritative source of the boundary. For example, a PDF containing a map of the area, indicated with a red-line boundary.

### notes

Optional text on how this data was made or produced, or how it can be interpreted.

### start-date

The date that the article 4 direction came into force, written in `YYYY-MM-DD` format.

Example: `1984-03-28`

### end-date

If applicable, the date that the article 4 direction was no longer in effect, written in `YYYY-MM-DD` format. If this does not apply, leave the cell blank.

Example: `1999-01-20`

### entry-date

The date the entity was last updated.

If the entity has never been updated, enter the same date as start-date.

Write in `YYYY-MM-DD` format.

Example: `2022-12-20`
