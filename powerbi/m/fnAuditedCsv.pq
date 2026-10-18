// Strict CSV import; run the Python checksum preflight before every Desktop refresh.
(fileName as text, schema as list, expectedRows as number, expectedTotal as nullable number) as table =>
let
    Root = Text.TrimEnd(pRepositoryRoot, {"/", "\"}),
    Path = Root & "/data/processed/eda/168665c92a8a2ff91598/" & fileName,
    Raw = Csv.Document(File.Contents(Path), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Raw, [PromoteAllScalars=true]),
    Names = List.Transform(schema, each [Name]),
    CheckedHeaders = if Table.ColumnNames(Promoted) = Names then Promoted
        else error Error.Record("SchemaMismatch", fileName, Table.ColumnNames(Promoted)),
    Parse = (v as nullable text, spec as record) as any =>
        if v = null or v = "" then
            if spec[Nullable] then null else error Error.Record("RequiredValue", fileName, spec[Name])
        else if spec[Kind] = "text" then v
        else if spec[Kind] = "integer" then
            let n = Number.FromText(v, "en-US") in
                if n = Number.RoundTowardZero(n) then Int64.From(n)
                else error Error.Record("NonIntegralValue", fileName, spec[Name])
        else if spec[Kind] = "decimal" then Number.FromText(v, "en-US")
        else if spec[Kind] = "boolean" then
            if v = "True" then true else if v = "False" then false
            else error Error.Record("InvalidBoolean", fileName, spec[Name])
        else if spec[Kind] = "date" then Date.FromText(v, [Format="yyyy-MM-dd", Culture="en-US"])
        else error Error.Record("UnknownType", fileName, spec[Kind]),
    KindType = (kind as text) as type =>
        if kind = "integer" then Int64.Type
        else if kind = "decimal" then type nullable number
        else if kind = "boolean" then type nullable logical
        else if kind = "date" then type nullable date
        else type nullable text,
    Typed = Table.TransformColumns(CheckedHeaders,
        List.Transform(schema, (spec) => {spec[Name], (v) => Parse(v, spec), KindType(spec[Kind])})),
    Buffered = Table.Buffer(Typed),
    Errors = Table.SelectRowsWithErrors(Buffered),
    CheckedRows = if Table.RowCount(Errors) <> 0 then
            error Error.Record("InvalidValues", fileName, Table.RowCount(Errors))
        else if Table.RowCount(Buffered) <> expectedRows then
            error Error.Record("RowCountMismatch", fileName, Table.RowCount(Buffered))
        else Buffered,
    Result = if expectedTotal = null then CheckedRows
        else if List.Sum(Table.Column(CheckedRows, "reported_record_count")) <> expectedTotal then
            error Error.Record("FactTotalMismatch", fileName, expectedTotal)
        else CheckedRows
in
    Result
