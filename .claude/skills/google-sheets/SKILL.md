---
name: google-sheets
description: Work with Google Sheets via MCP — create spreadsheets, read/write data, format cells, build charts, run SQL queries, manage sheets and filters. Use this skill whenever the user mentions Google Sheets, spreadsheets, Google таблицы, or wants to create/edit/format/query tabular data in Google Drive. Also trigger when the user asks to export data to a sheet, build a dashboard in Sheets, or interact with any existing Google Spreadsheet by ID or URL.
---

# Google Sheets MCP Skill

This skill provides complete guidance for working with Google Sheets through the MCP integration. All tools have the prefix `mcp__googlesheets__`.

## Authentication

Before using any tool, authentication is required. Call `mcp__googlesheets__authenticate` first — it will return a URL for the user to authorize in their browser. Once authorized, all tools become available automatically.

## Quick Reference: Choosing the Right Tool

### Creating spreadsheets
| Goal | Tool |
|------|------|
| Create empty spreadsheet | `create_google_sheet1` |
| Create spreadsheet from JSON data | `sheet_from_json` |

### Reading data
| Goal | Tool |
|------|------|
| Get cell values by range | `batch_get` |
| Get values by filter criteria | `spreadsheets_values_batch_get_by_data_filter` |
| Get spreadsheet metadata (no data) | `get_spreadsheet_info` |
| Get filtered spreadsheet data | `get_spreadsheet_by_data_filter` |
| List sheet/tab names | `get_sheet_names` |
| Find a sheet by title | `find_worksheet_by_title` |
| Discover tables in a spreadsheet | `list_tables` |
| Get table column types | `get_table_schema` |
| Find a row by value | `lookup_spreadsheet_row` |
| Search spreadsheets in Drive | `search_spreadsheets` |

### Writing data
| Goal | Tool |
|------|------|
| Append rows to end of table | `spreadsheets_values_append` |
| Update specific range | `batch_update` |
| Update by data filter | `batch_update_values_by_data_filter` |

### Structure management
| Goal | Tool |
|------|------|
| Add new sheet/tab | `add_sheet` |
| Delete a sheet/tab | `delete_sheet` |
| Copy sheet to another spreadsheet | `spreadsheets_sheets_copy_to` |
| Update sheet properties (title, color) | `update_sheet_properties` |
| Update spreadsheet properties (title, locale) | `update_spreadsheet_properties` |
| Insert empty rows/columns at position | `insert_dimension` |
| Append empty rows/columns at end | `append_dimension` |
| Delete rows/columns | `delete_dimension` |
| Insert single row | `create_spreadsheet_row` |
| Insert single column | `create_spreadsheet_column` |

### Formatting & filtering
| Goal | Tool |
|------|------|
| Format cells (bold, color, size) | `format_cell` |
| Set basic filter (sort/filter) | `set_basic_filter` |
| Remove basic filter | `clear_basic_filter` |

### Clearing data
| Goal | Tool |
|------|------|
| Clear a range (keep formatting) | `clear_values` |
| Clear multiple ranges | `spreadsheets_values_batch_clear` |
| Clear ranges by data filter | `spreadsheets_values_batch_clear_by_data_filter` |

### Charts
| Goal | Tool |
|------|------|
| Create a chart | `create_chart` |

### SQL queries
| Goal | Tool |
|------|------|
| Run SELECT/INSERT/UPDATE/DELETE | `execute_sql` |
| Run SELECT with table discovery | `query_table` |

### Analytics
| Goal | Tool |
|------|------|
| Aggregate column (sum, avg, count...) | `aggregate_column_data` |

### Metadata
| Goal | Tool |
|------|------|
| Search developer metadata | `search_developer_metadata` |

## Common Workflows

### 1. Create a spreadsheet and populate it

```
1. create_google_sheet1(title="My Report")  →  get spreadsheet_id
2. spreadsheets_values_append(spreadsheetId, range="Sheet1!A1", values=[[headers], [row1], [row2]...])
3. format_cell(...)  →  style the header row
```

Or in one step with `sheet_from_json(title, sheet_json=[{col: val}, ...], sheet_name="Data")`.

### 2. Read and query existing data

```
1. get_sheet_names(spreadsheet_id)  →  see available tabs
2. batch_get(spreadsheet_id, ranges=["Sheet1!A1:Z"])  →  read all data
   OR
   list_tables(spreadsheet_id)  →  discover tables
   get_table_schema(spreadsheet_id, table_name)  →  see columns/types
   query_table(spreadsheet_id, sql="SELECT * FROM \"TableName\" WHERE ...")
```

### 3. Format a table nicely

```
1. format_cell(header row: bold=true, fontSize=11, dark background)
2. format_cell(alternating rows: light background for zebra striping)
3. format_cell(accent columns: different background colors)
```

Colors use RGB floats 0.0-1.0. For dark header with white text, use low RGB values (e.g. red=0.16, green=0.16, blue=0.26).

### 4. Build a chart

```
1. create_chart(spreadsheet_id, chart_type="COLUMN", data_range="Sheet1!A1:C10", title="Sales")
```

Chart types: BAR, LINE, AREA, COLUMN, SCATTER, COMBO, STEPPED_AREA.

### 5. SQL-based operations

`execute_sql` supports full SQL: SELECT, INSERT, UPDATE, DELETE.
Table names with spaces must be quoted: `"My Table"`.

```sql
SELECT * FROM "Sales_Data" WHERE revenue > 1000 ORDER BY date DESC LIMIT 10
INSERT INTO "Customers" (name, email) VALUES ('John', 'john@example.com')
UPDATE "Inventory" SET quantity = quantity - 10 WHERE sku = 'ABC123'
DELETE FROM "Old_Data" WHERE date < '2023-01-01'
```

## Key Concepts

- **spreadsheet_id**: The long string from the URL `docs.google.com/spreadsheets/d/{THIS_PART}/edit`
- **sheet_id** (integer): Numeric ID of a tab within the spreadsheet (0 for first sheet). Found via `get_spreadsheet_info`.
- **A1 notation**: Range like `Sheet1!A1:C10`, `A:A` (whole column), `1:1` (whole row)
- **Grid indices**: 0-based, exclusive end. Row 0 = first row, column 0 = column A.
- **valueInputOption**: `USER_ENTERED` (parses like typed input) or `RAW` (stores as-is). Prefer `USER_ENTERED` for formulas and auto-formatting.

## Detailed Tool Documentation

For full parameter details of each tool, read `references/tools-reference.md`.
