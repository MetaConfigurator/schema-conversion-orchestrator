"""Serve a local browser UI for annotating evaluation review CSVs.

Usage:

    python eval/annotate_outputs.py

The UI edits ``eval/results/orchestrator_outputs/review/*.csv`` in place.
"""

from __future__ import annotations

import argparse
import json
import shutil
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from annotation_model import AnnotationModel, EDGE_CSV, FINAL_CSV


INDEX_HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Orchestrator Annotation</title>
<style>
:root{--bg:#f5f6f8;--panel:#fff;--line:#d9dee7;--text:#1f2933;--muted:#667085;--accent:#315f9c;--soft:#e7eef8;--g:#238443;--l:#b7791f;--i:#b42318}
*{box-sizing:border-box} body{margin:0;background:var(--bg);color:var(--text);font:14px/1.4 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
header{position:sticky;top:0;z-index:10;display:flex;align-items:center;gap:16px;padding:12px 18px;background:var(--panel);border-bottom:1px solid var(--line)}
h1{margin:0;font-size:18px;font-weight:650;white-space:nowrap} button,select,input{font:inherit;border:1px solid var(--line);background:#fff;color:var(--text);border-radius:6px;min-height:32px}
button{padding:0 12px;cursor:pointer} button.primary{background:var(--accent);border-color:var(--accent);color:#fff} button:disabled{opacity:.45;cursor:default}
select,input{padding:0 9px}.toolbar{display:flex;align-items:center;gap:8px;flex-wrap:wrap;width:100%}.toolbar input[type=search]{min-width:260px;flex:1}
.pill{display:inline-flex;align-items:center;justify-content:center;min-width:24px;height:24px;border-radius:999px;padding:0 8px;font-weight:650;font-size:12px;background:#eef1f5;color:var(--muted)}
.pill.G{background:#e7f5ec;color:var(--g)}.pill.L{background:#fff4dd;color:var(--l)}.pill.I{background:#fee7e4;color:var(--i)}
main{padding:16px}.table-wrap{background:var(--panel);border:1px solid var(--line);border-radius:8px;overflow:auto;height:calc(100vh - 86px)}
table{width:100%;border-collapse:collapse;table-layout:fixed} th,td{border-bottom:1px solid var(--line);padding:7px 9px;text-align:left;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;vertical-align:middle}
th{position:sticky;top:0;z-index:2;background:#f8fafc;color:#475467;font-size:12px;font-weight:650} tr{cursor:pointer} tbody tr:hover{background:var(--soft)}
.status-col{width:64px}.short-col{width:110px}.medium-col{width:180px}.long-col{width:340px}.hidden{display:none!important}
.detail{display:none;height:calc(100vh - 86px);grid-template-rows:auto 1fr;gap:12px}.detail.active{display:grid}
.detail-head{display:grid;grid-template-columns:1fr auto;gap:12px;align-items:start;background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:12px}
.titleline{display:flex;align-items:center;gap:10px;min-width:0;margin-bottom:8px}.titleline strong{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:15px}
.meta{display:flex;flex-wrap:wrap;gap:8px 14px;color:var(--muted);font-size:12px}.meta span{max-width:560px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.controls{display:grid;grid-template-columns:auto minmax(320px,520px) auto auto;gap:8px;align-items:center}.controls input{width:100%}
.code-grid{min-height:0;display:grid;grid-template-columns:1fr 1fr;gap:12px}.pane{min-width:0;min-height:0;background:var(--panel);border:1px solid var(--line);border-radius:8px;display:grid;grid-template-rows:auto 1fr;overflow:hidden}
.pane h2{display:flex;align-items:center;justify-content:space-between;gap:12px;margin:0;padding:9px 12px;border-bottom:1px solid var(--line);font-size:13px;font-weight:650;color:#475467;background:#f8fafc}
.path-label{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-weight:500;color:var(--muted)} pre{margin:0;padding:12px;overflow:auto;white-space:pre;font:12px/1.45 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;tab-size:2}.error{color:var(--i)}
@media(max-width:1000px){.detail-head,.code-grid{grid-template-columns:1fr}.controls{grid-template-columns:1fr 1fr}.controls input{grid-column:1/-1}}
</style>
</head>
<body>
<header>
  <h1>Output Annotation</h1>
  <div id="tableToolbar" class="toolbar">
    <select id="kind"><option value="final">Final outputs</option><option value="edge">Edge outputs</option></select>
    <select id="statusFilter"><option value="all">All statuses</option><option value="blank">Unannotated</option><option value="G">G</option><option value="L">L</option><option value="I">I</option></select>
    <input id="search" type="search" placeholder="Filter by language, file, path, converter, notes">
    <span id="count" class="pill"></span>
  </div>
  <div id="detailToolbar" class="toolbar hidden">
    <button id="backToTable">Table</button><button id="prev">Back</button><button id="next" class="primary">Next</button><span id="saveState" class="pill">Saved</span>
  </div>
</header>
<main>
  <section id="tableView" class="table-wrap"><table><thead id="thead"></thead><tbody id="tbody"></tbody></table></section>
  <section id="detailView" class="detail">
    <div class="detail-head">
      <div><div class="titleline"><span id="detailStatus" class="pill"></span><strong id="detailTitle"></strong></div><div id="detailMeta" class="meta"></div></div>
      <div class="controls"><select id="annotation"><option value="">Blank</option><option value="G">G</option><option value="L">L</option><option value="I">I</option></select><input id="notes" type="text" placeholder="Notes / comments"><button id="save">Save</button><button id="closeDetail">Close</button></div>
    </div>
    <div class="code-grid">
      <article class="pane"><h2><span>Relevant input</span><span id="inputPath" class="path-label"></span></h2><pre id="inputContent"></pre></article>
      <article class="pane"><h2><span>Produced output</span><span id="outputPath" class="path-label"></span></h2><pre id="outputContent"></pre></article>
    </div>
  </section>
</main>
<script>
const state={kind:"final",rows:[],filtered:[],selected:-1,timer:null};
const columns={final:[["status","Status","status-col"],["source_language","Source","short-col"],["target_language","Target","short-col"],["input_file","Input","long-col"],["path_rank","Rank","short-col"],["path_count","Paths","short-col"],["path_signature","Path","long-col"],["notes","Notes","long-col"]],edge:[["status","Status","status-col"],["edge_source_language","Edge source","short-col"],["edge_target_language","Edge target","short-col"],["converter_name","Converter","medium-col"],["library","Library","medium-col"],["input_file","Case","long-col"],["path_id","Path","short-col"],["step_index","Step","short-col"],["notes","Notes","long-col"]]};
const $=id=>document.getElementById(id);
function esc(v){return String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]))}
function pill(v){return `<span class="pill ${v||""}">${esc(v||"-")}</span>`}
async function api(path,opt){const r=await fetch(path,opt);if(!r.ok)throw new Error(await r.text()||r.statusText);return r.json()}
function rowQuery(){return new URLSearchParams({kind:$("kind").value,status:$("statusFilter").value,search:$("search").value})}
async function loadRows(){state.kind=$("kind").value;const data=await api(`/api/rows?${rowQuery()}`);state.rows=data.rows;state.filtered=data.rows;state.total=data.total;renderTable()}
function applyFilter(){loadRows().catch(showError)}
function renderTable(){const cols=columns[state.kind];$("thead").innerHTML="<tr>"+cols.map(([_,l,c])=>`<th class="${c}">${esc(l)}</th>`).join("")+"</tr>";$("tbody").innerHTML=state.filtered.map((r,i)=>`<tr data-i="${i}">`+cols.map(([k,_,c])=>`<td class="${c}" title="${esc(r[k])}">${k==="status"?pill(r[k]):esc(r[k])}</td>`).join("")+"</tr>").join("");$("count").textContent=`${state.filtered.length}/${state.total}`;document.querySelectorAll("tbody tr").forEach(tr=>tr.onclick=()=>openDetail(Number(tr.dataset.i)))}
function navigableIndex(from,dir){for(let i=from+dir;i>=0&&i<state.filtered.length;i+=dir){if((state.filtered[i].status||"")!=="I")return i}return -1}
async function navigate(dir){const r=state.filtered[state.selected];if(!r)return;const params=rowQuery();params.set("row",r.__rowid);params.set("direction",String(dir));const data=await api(`/api/navigate?${params}`);if(data.row_id===null)return;const i=state.filtered.findIndex(row=>row.__rowid===data.row_id);if(i>=0)await openDetail(i)}
async function openDetail(i){const r=state.filtered[i];if(!r)return;state.selected=i;$("tableView").classList.add("hidden");$("tableToolbar").classList.add("hidden");$("detailToolbar").classList.remove("hidden");$("detailView").classList.add("active");$("annotation").value=r.status||"";$("notes").value=r.notes||"";setStatus(r.status||"");$("prev").disabled=navigableIndex(i,-1)<0;$("next").disabled=navigableIndex(i,1)<0;$("saveState").textContent="Saved";renderMeta(r);const f=await api(`/api/files?kind=${state.kind}&row=${r.__rowid}`);$("inputPath").textContent=f.input_path||"";$("outputPath").textContent=f.output_path||"";$("inputContent").textContent=f.input_content||"";$("outputContent").textContent=f.output_content||"";$("inputContent").classList.toggle("error",!!f.input_error);$("outputContent").classList.toggle("error",!!f.output_error)}
function renderMeta(r){$("detailTitle").textContent=state.kind==="edge"?`${r.edge_source_language} -> ${r.edge_target_language} via ${r.converter_name}`:`${r.source_language} -> ${r.target_language} ${r.path_id}`;const fields=state.kind==="edge"?["input_file","path_id","step_index","edge_signature","input_path","output_path"]:["input_file","path_rank","path_count","path_signature","output_path"];$("detailMeta").innerHTML=fields.map(k=>`<span title="${esc(r[k])}"><strong>${esc(k)}:</strong> ${esc(r[k])}</span>`).join("")}
function setStatus(v){$("detailStatus").className=`pill ${v||""}`;$("detailStatus").textContent=v||"-"}
async function saveCurrent(){const r=state.filtered[state.selected];if(!r)return;const status=$("annotation").value,notes=$("notes").value;$("saveState").textContent="Saving";await api("/api/annotation",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({kind:state.kind,row:r.__rowid,status,notes})});r.status=status;r.notes=notes;const src=state.rows.find(x=>x.__rowid===r.__rowid);if(src){src.status=status;src.notes=notes}setStatus(status);$("saveState").textContent="Saved"}
function scheduleSave(){$("saveState").textContent="Edited";clearTimeout(state.timer);state.timer=setTimeout(()=>saveCurrent().catch(showError),450)}
function closeDetail(){$("detailView").classList.remove("active");$("detailToolbar").classList.add("hidden");$("tableToolbar").classList.remove("hidden");$("tableView").classList.remove("hidden");applyFilter()}
function showError(e){$("saveState").textContent="Error";alert(e.message||String(e))}
$("kind").onchange=()=>loadRows().catch(showError);$("statusFilter").onchange=applyFilter;$("search").oninput=applyFilter;$("annotation").onchange=()=>saveCurrent().catch(showError);$("notes").oninput=scheduleSave;$("save").onclick=()=>saveCurrent().catch(showError);$("closeDetail").onclick=closeDetail;$("backToTable").onclick=closeDetail;$("prev").onclick=()=>navigate(-1).catch(showError);$("next").onclick=()=>navigate(1).catch(showError);document.onkeydown=e=>{if(!$("detailView").classList.contains("active"))return;if(e.key==="Escape")closeDetail();if(e.key==="ArrowLeft"&&!$("prev").disabled)navigate(-1).catch(showError);if(e.key==="ArrowRight"&&!$("next").disabled)navigate(1).catch(showError)};
loadRows().catch(showError);
</script>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    model: AnnotationModel

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/":
                self._send(INDEX_HTML, "text/html; charset=utf-8")
                return
            query = parse_qs(parsed.query)
            kind = query.get("kind", ["final"])[0]
            if parsed.path == "/api/rows":
                status_filter = query.get("status", ["all"])[0]
                search = query.get("search", [""])[0]
                total = len(self.model.read_rows(kind)[1])
                rows = self.model.rows(kind, status_filter=status_filter, search=search)
                self._json({"rows": rows, "total": total})
                return
            if parsed.path == "/api/files":
                self._json(self.model.comparison(kind, query.get("row", ["0"])[0]))
                return
            if parsed.path == "/api/navigate":
                row_id = self.model.navigable_row_id(
                    kind=kind,
                    current_row_id=query.get("row", ["0"])[0],
                    direction=int(query.get("direction", ["1"])[0]),
                    status_filter=query.get("status", ["all"])[0],
                    search=query.get("search", [""])[0],
                    skip_invalid=True,
                )
                self._json({"row_id": row_id})
                return
            self.send_error(404)
        except Exception as exc:  # noqa: BLE001
            self.send_error(400, str(exc))

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/annotation":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            self.model.update(
                payload["kind"],
                int(payload["row"]),
                payload.get("status", ""),
                payload.get("notes", ""),
            )
            self._json({"ok": True})
        except Exception as exc:  # noqa: BLE001
            self.send_error(400, str(exc))

    def log_message(self, fmt: str, *args) -> None:
        print(f"{self.address_string()} - {fmt % args}")

    def _json(self, payload: object) -> None:
        self._send(json.dumps(payload), "application/json; charset=utf-8")

    def _send(self, body: str, content_type: str) -> None:
        encoded = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(encoded)


def serve(args: argparse.Namespace) -> None:
    Handler.model = AnnotationModel(args.final_csv, args.edge_csv)
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    url = f"http://{args.host}:{args.port}"
    print(f"Serving annotation UI at {url}")
    print("Press Ctrl+C to stop.")
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def clipped(text: str, max_lines: int, width: int) -> str:
    lines = text.splitlines()
    shown = lines[:max_lines]
    clipped_lines = [line[:width] + ("..." if len(line) > width else "") for line in shown]
    if len(lines) > max_lines:
        clipped_lines.append(f"... ({len(lines) - max_lines} more lines)")
    return "\n".join(clipped_lines)


def print_entry(model: AnnotationModel, kind: str, row_id: str, max_lines: int) -> None:
    row = model.row(kind, row_id)
    comparison = model.comparison(kind, row_id)
    width = shutil.get_terminal_size((120, 24)).columns
    content_width = max(60, min(140, width - 4))

    print("\n" + "=" * content_width)
    print(f"{kind.upper()} row {row_id}: {model.title(kind, row)}")
    print(f"status={row.get('status') or '-'}  notes={row.get('notes') or '-'}")
    for field in model.meta_fields(kind):
        print(f"{field}: {row.get(field, '')}")
    print("-" * content_width)
    print(f"INPUT: {comparison['input_path']}")
    print(clipped(str(comparison["input_content"]), max_lines, content_width))
    print("-" * content_width)
    print(f"OUTPUT: {comparison['output_path']}")
    print(clipped(str(comparison["output_content"]), max_lines, content_width))


def first_navigable_row(
    model: AnnotationModel,
    kind: str,
    status_filter: str,
    search: str,
    multi_hop_only: bool,
) -> str | None:
    for row in model.rows(
        kind,
        status_filter=status_filter,
        search=search,
        multi_hop_only=multi_hop_only,
    ):
        if row.get("status", "") != "I":
            return row["__rowid"]
    return None


def cli(args: argparse.Namespace) -> None:
    model = AnnotationModel(args.final_csv, args.edge_csv)
    kind = args.kind
    row_id = args.row
    if row_id is None:
        row_id = first_navigable_row(model, kind, args.status, args.search, args.multi_hop_only)
    if row_id is None:
        raise SystemExit("No non-invalid rows match the selected filters.")

    print("Commands: n/next, b/back, g/l/i/blank, note <text>, show, q/quit")
    while True:
        print_entry(model, kind, row_id, args.lines)
        command = input("\nannotation> ").strip()
        lower = command.lower()
        if lower in {"q", "quit", "exit"}:
            break
        if lower in {"n", "next", ""}:
            next_id = model.navigable_row_id(
                kind,
                row_id,
                1,
                args.status,
                args.search,
                skip_invalid=True,
                multi_hop_only=args.multi_hop_only,
            )
            if next_id is None:
                print("No next non-invalid row.")
            else:
                row_id = next_id
            continue
        if lower in {"b", "back", "prev", "previous"}:
            prev_id = model.navigable_row_id(
                kind,
                row_id,
                -1,
                args.status,
                args.search,
                skip_invalid=True,
                multi_hop_only=args.multi_hop_only,
            )
            if prev_id is None:
                print("No previous non-invalid row.")
            else:
                row_id = prev_id
            continue
        if lower in {"g", "l", "i", "blank"}:
            status = "" if lower == "blank" else lower.upper()
            row = model.row(kind, row_id)
            model.update(kind, row_id, status, row.get("notes", ""))
            print(f"Saved status={status or '-'}")
            continue
        if lower.startswith("note "):
            row = model.row(kind, row_id)
            model.update(kind, row_id, row.get("status", ""), command[5:].strip())
            print("Saved note.")
            continue
        if lower == "show":
            continue
        print("Unknown command. Use n, b, g, l, i, blank, note <text>, show, or q.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Annotate G/L/I evaluation outputs.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--final-csv", type=Path, default=FINAL_CSV)
    parser.add_argument("--edge-csv", type=Path, default=EDGE_CSV)
    parser.add_argument("--no-browser", action="store_true")
    subparsers = parser.add_subparsers(dest="mode")

    cli_parser = subparsers.add_parser("cli", help="review annotations in the terminal")
    cli_parser.add_argument("--kind", choices=["final", "edge"], default="final")
    cli_parser.add_argument("--row", default=None, help="starting row id")
    cli_parser.add_argument("--status", choices=["all", "blank", "G", "L", "I"], default="all")
    cli_parser.add_argument("--search", default="")
    cli_parser.add_argument("--lines", type=int, default=80, help="maximum lines shown per file")
    cli_parser.add_argument(
        "--multi-hop-only",
        action="store_true",
        help="skip rows whose path_signature contains only one converter step",
    )

    args = parser.parse_args()
    if args.mode == "cli":
        cli(args)
    else:
        serve(args)


if __name__ == "__main__":
    main()
