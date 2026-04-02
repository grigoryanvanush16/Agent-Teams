# Google Sheets MCP — Full Tool Reference

All tools use the prefix `mcp__googlesheets__`. Use ToolSearch to load a tool before calling it.

## Table of Contents

1. [Creating Spreadsheets](#creating-spreadsheets)
2. [Reading Data](#reading-data)
3. [Writing Data](#writing-data)
4. [Structure Management](#structure-management)
5. [Formatting & Filtering](#formatting--filtering)
6. [Clearing Data](#clearing-data)
7. [Charts](#charts)
8. [SQL Queries](#sql-queries)
9. [Analytics](#analytics)
10. [Metadata](#metadata)

---

## Creating Spreadsheets

### create_google_sheet1

Creates an empty spreadsheet in Google Drive.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| title | string | yes | Spreadsheet title |

Returns: `spreadsheet_id`, sheet info.

### sheet_from_json

Creates a new spreadsheet and populates it from JSON. First item's keys become headers.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| title | string | yes | Spreadsheet title |
| sheet_json | array of objects | yes | `[{"Name": "Alice", "Age": 30}, ...]` |
| sheet_name | string | yes | Tab name (e.g. "Sheet1") |

---

## Reading Data

### batch_get

Retrieves cell values from one or more ranges.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| spreadsheet_id | string | yes | Spreadsheet ID |
| ranges | array of strings | no | A1 ranges. Omit for all data from first sheet. |

### spreadsheets_values_batch_get_by_data_filter

Returns values matching data filters (A1 or grid range).

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| spreadsheetId | string | yes | Spreadsheet ID |
| dataFilters | array | yes | `[{"a1Range": "Sheet1!A1:B5"}]` or gridRange |
| majorDimension | string | no | ROWS or COLUMNS |
| valueRenderOption | string | no | FORMATTED_VALUE, UNFORMATTED_VALUE, FORMULA |
| dateTimeRenderOption | string | no | SERIAL_NUMBER or FORMATTED_STRING |

### get_spreadsheet_info

Returns spreadsheet metadata (sheets, properties) without cell data.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| spreadsheet_id | string | yes | Spreadsheet ID |

### get_spreadsheet_by_data_filter

Returns spreadsheet data filtered by criteria.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| spreadsheetId | string | yes | Spreadsheet ID |
| dataFilters | array | yes | A1, gridRange, or developerMetadataLookup |
| includeGridData | boolean | no | Include cell data |

### get_sheet_names

Lists all tab names in a spreadsheet.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| spreadsheet_id | string | yes | Spreadsheet ID |

### find_worksheet_by_title

Finds a worksheet by exact case-sensitive title.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| spreadsheet_id | string | yes | Spreadsheet ID |
| title | string | yes | Exact sheet name |

### list_tables

Discovers all tables using heuristic analysis.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| spreadsheet_id | string | yes | Spreadsheet ID |
| min_rows | integer | no | Min data rows (default 2) |
| min_columns | integer | no | Min columns (default 1) |
| min_confidence | number | no | 0.0-1.0 (default 0.5) |

### get_table_schema

Analyzes table structure and infers column types. Call after `list_tables`.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| spreadsheet_id | string | yes | Spreadsheet ID |
| table_name | string | yes | Table name from list_tables, or "auto" |
| sheet_name | string | no | Sheet name if ambiguous |
| sample_size | integer | no | Rows to sample (default 50, max 1000) |

### lookup_spreadsheet_row

Finds first row where a cell exactly matches a query.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| spreadsheet_id | string | yes | Spreadsheet ID |
| query | string | yes | Exact value to find |
| range | string | no | A1 range to search (default: first sheet) |
| case_sensitive | boolean | no | Default false |

### search_spreadsheets

Search for spreadsheets in Google Drive.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| query | string | no | `"name contains 'budget'"`, `"fullText contains 'sales'"` |
| max_results | integer | no | 1-1000 (default 10) |
| order_by | string | no | e.g. "modifiedTime desc" |
| created_after | string | no | RFC 3339 date |
| modified_after | string | no | RFC 3339 date |
| starred_only | boolean | no | Default false |
| shared_with_me | boolean | no | Default false |
| include_trashed | boolean | no | Default false |

---

## Writing Data

### spreadsheets_values_append

Appends rows to the end of a table.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| spreadsheetId | string | yes | Spreadsheet ID |
| range | string | yes | A1 range (e.g. "Sheet1!A1") |
| values | 2D array | yes | `[["a","b"], ["c","d"]]` |
| valueInputOption | string | yes | USER_ENTERED or RAW |
| insertDataOption | string | no | OVERWRITE or INSERT_ROWS |
| majorDimension | string | no | ROWS or COLUMNS |
| includeValuesInResponse | boolean | no | Default false |

### batch_update

Updates a specific range with values, or appends if `first_cell_location` is omitted.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| spreadsheet_id | string | yes | Spreadsheet ID |
| sheet_name | string | yes | Tab name |
| values | 2D array | yes | The data |
| first_cell_location | string | no | A1 cell (e.g. "A1"). Omit to append. |
| valueInputOption | string | no | USER_ENTERED (default) or RAW |

### batch_update_values_by_data_filter

Updates values in ranges matching data filters.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| spreadsheetId | string | yes | Spreadsheet ID |
| valueInputOption | string | yes | USER_ENTERED or RAW |
| data | array | yes | Objects with `dataFilter`, `values`, `majorDimension` |
| includeValuesInResponse | boolean | no | Default false |

Each data item: `{dataFilter: {a1Range: "Sheet1!A1:B2"}, values: [[...]], majorDimension: "ROWS"}`

---

## Structure Management

### add_sheet

Adds a new tab to a spreadsheet.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| spreadsheetId | string | yes | Spreadsheet ID |
| properties | object | no | title, index, sheetId, hidden, gridProperties (rowCount, columnCount, frozenRowCount, frozenColumnCount), tabColorStyle |

### delete_sheet

Removes a tab.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| spreadsheetId | string | yes | Spreadsheet ID |
| sheet_id | integer | yes | Sheet ID (not name) |

### spreadsheets_sheets_copy_to

Copies a sheet to another spreadsheet.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| spreadsheet_id | string | yes | Source spreadsheet ID |
| sheet_id | integer | yes | Sheet ID to copy |
| destination_spreadsheet_id | string | yes | Target spreadsheet ID |

### update_sheet_properties

Updates tab properties (title, visibility, color, grid settings).

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| spreadsheetId | string | yes | Spreadsheet ID |
| updateSheetProperties.fields | string | yes | FieldMask: "title", "hidden", "*", etc. |
| updateSheetProperties.properties | object | yes | Must include `sheetId` + fields to update |

### update_spreadsheet_properties

Updates spreadsheet-level settings.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| spreadsheetId | string | yes | Spreadsheet ID |
| fields | string | yes | FieldMask: "title", "locale", "*" |
| properties | object | yes | title, locale, timeZone, autoRecalc, defaultFormat, spreadsheetTheme |

### insert_dimension

Inserts empty rows or columns at a position.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| spreadsheet_id | string | yes | Spreadsheet ID |
| insert_dimension.range | object | yes | `{sheet_id, dimension: "ROWS"/"COLUMNS", start_index, end_index}` |
| insert_dimension.inherit_from_before | boolean | no | Inherit formatting from row/col before |

Count = end_index - start_index.

### append_dimension

Appends empty rows or columns at the end.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| spreadsheet_id | string | yes | Spreadsheet ID |
| sheet_id | integer | yes | Sheet ID |
| dimension | string | yes | ROWS or COLUMNS |
| length | integer | yes | How many to add |

### delete_dimension

Deletes a range of rows or columns.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| spreadsheet_id | string | yes | Spreadsheet ID |
| delete_dimension_request.range | object | yes | `{sheet_id, dimension, start_index, end_index}` |

### create_spreadsheet_row

Inserts a single empty row.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| spreadsheet_id | string | yes | Spreadsheet ID |
| sheet_id | integer | yes | Sheet ID |
| insert_index | integer | no | 0-based position (default 0) |
| inherit_from_before | boolean | no | Default false |

### create_spreadsheet_column

Inserts a single empty column.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| spreadsheet_id | string | yes | Spreadsheet ID |
| sheet_id | integer | yes | Sheet ID |
| insert_index | integer | no | 0-based position (default 0) |
| inherit_from_before | boolean | no | Default false |

---

## Formatting & Filtering

### format_cell

Applies text and background formatting to a range.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| spreadsheet_id | string | yes | Spreadsheet ID |
| worksheet_id | integer | yes | Sheet ID (use get_spreadsheet_info to find) |
| start_row_index | integer | yes | 0-based start row |
| end_row_index | integer | yes | 0-based end row (exclusive) |
| start_column_index | integer | yes | 0-based start column |
| end_column_index | integer | yes | 0-based end column (exclusive) |
| bold | boolean | no | Default false |
| italic | boolean | no | Default false |
| underline | boolean | no | Default false |
| strikethrough | boolean | no | Default false |
| fontSize | integer | no | Points (default 10) |
| red | number | no | Background R 0.0-1.0 (default 0.9) |
| green | number | no | Background G 0.0-1.0 (default 0.9) |
| blue | number | no | Background B 0.0-1.0 (default 0.9) |

### set_basic_filter

Sets a filter on a sheet (sort and filter criteria).

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| spreadsheetId | string | yes | Spreadsheet ID |
| filter.range | object | yes | `{sheet_id}` + optional start/end row/column |
| filter.criteria | object | no | Column index → FilterCriteria (hiddenValues, condition) |
| filter.sortSpecs | array | no | `[{dimensionIndex, sortOrder: "ASCENDING"/"DESCENDING"}]` |

**Condition types** for criteria: NUMBER_GREATER, NUMBER_LESS, TEXT_CONTAINS, TEXT_EQ, DATE_BEFORE, DATE_AFTER, CUSTOM_FORMULA, etc.

### clear_basic_filter

Removes a basic filter from a sheet.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| spreadsheetId | string | yes | Spreadsheet ID |
| sheet_id | integer | yes | Sheet ID |

---

## Clearing Data

### clear_values

Clears cell content from a range (preserves formatting).

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| spreadsheet_id | string | yes | Spreadsheet ID |
| range | string | yes | A1 range |

### spreadsheets_values_batch_clear

Clears multiple ranges at once.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| spreadsheet_id | string | yes | Spreadsheet ID |
| ranges | array of strings | yes | A1 ranges |

### spreadsheets_values_batch_clear_by_data_filter

Clears ranges matching data filters.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| spreadsheetId | string | yes | Spreadsheet ID |
| dataFilters | array | yes | A1, gridRange, or developerMetadataLookup |

---

## Charts

### create_chart

Creates a chart on a sheet.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| spreadsheet_id | string | yes | Spreadsheet ID |
| chart_type | string | yes | BAR, LINE, AREA, COLUMN, SCATTER, COMBO, STEPPED_AREA |
| data_range | string | yes | A1 range (e.g. "A1:C10") |
| sheet_id | integer | no | Sheet ID (default 0) |
| title | string | no | Chart title |
| subtitle | string | no | Chart subtitle |
| x_axis_title | string | no | X-axis label |
| y_axis_title | string | no | Y-axis label |
| legend_position | string | no | BOTTOM_LEGEND, TOP_LEGEND, LEFT_LEGEND, RIGHT_LEGEND, NO_LEGEND |
| background_red | number | no | 0.0-1.0 |
| background_green | number | no | 0.0-1.0 |
| background_blue | number | no | 0.0-1.0 |

---

## SQL Queries

### execute_sql

Execute SQL queries against spreadsheet tables. Supports SELECT, INSERT, UPDATE, DELETE.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| spreadsheet_id | string | yes | Spreadsheet ID |
| sql | string | yes | SQL query. Quote table names with spaces. |
| dry_run | boolean | no | Preview without applying (default false) |
| delete_method | string | no | "clear" (default) or "remove_rows" |

### query_table

SQL-like SELECT queries with table discovery. Call `get_table_schema` first.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| spreadsheet_id | string | yes | Spreadsheet ID |
| sql | string | yes | SELECT query |
| include_formulas | boolean | no | Return formulas instead of values |

---

## Analytics

### aggregate_column_data

Searches rows by column value and aggregates another column.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| spreadsheet_id | string | yes | Spreadsheet ID |
| sheet_name | string | yes | Tab name |
| search_column | string | yes | Column letter or header name |
| search_value | string | yes | Value to match |
| target_column | string | yes | Column to aggregate |
| operation | string | yes | sum, average, count, min, max, percentage |
| case_sensitive | boolean | no | Default true |
| has_header_row | boolean | no | Default true |
| percentage_total | number | no | Denominator for percentage |

---

## Metadata

### search_developer_metadata

Searches for developer metadata entries.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| spreadsheetId | string | yes | Spreadsheet ID |
| dataFilters | array | yes | Filters (a1Range must be single row/column) |
