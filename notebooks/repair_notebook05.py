"""Repair notebook 05 locally without altering its existing checkpoint or frozen inputs.
Usage: python repair_notebook05.py
       python repair_notebook05.py path/to/05_yearly_citations.ipynb
Writes a separate 05_yearly_citations_fixed.ipynb; original is unchanged.
"""
from pathlib import Path
import ast
import sys
import nbformat

ENGINE = '\n# Canonical-ID repair, v2. Reuses portfolio checkpoints; legacy citation rows remain archived.\nALIAS_REPAIR_VERSION = \'canonical_alias_v2\'\nALIAS_MAP = {}\nunresolved_by_author = {}\n\nconn.executescript("""\nCREATE TABLE IF NOT EXISTS work_aliases_v2(\n old_id TEXT PRIMARY KEY,canonical_id TEXT,status TEXT NOT NULL,source TEXT NOT NULL,checked_at TEXT NOT NULL);\nCREATE TABLE IF NOT EXISTS query_restarts_v2(\n restart_id INTEGER PRIMARY KEY,task TEXT NOT NULL,reason TEXT NOT NULL,at TEXT NOT NULL);\nCREATE TABLE IF NOT EXISTS retired_items_v2(\n restart_id INTEGER,task TEXT,id TEXT,year INTEGER,author_ids TEXT);\nCREATE TABLE IF NOT EXISTS retired_edges_v2(\n restart_id INTEGER,task TEXT,citing TEXT,cited TEXT,year INTEGER);\nCREATE TEMP TABLE IF NOT EXISTS active_citation_tasks_v2(id TEXT PRIMARY KEY);\n""")\n\ndef _repair_backup():\n    row = conn.execute("SELECT value FROM metadata WHERE key=\'alias_repair_backup_v2\'").fetchone()\n    if row: return\n    conn.commit()\n    stamp = datetime.now(timezone.utc).strftime(\'%Y%m%dT%H%M%S%fZ\')\n    destination = DB_PATH.with_name(\'citation_collection_before_alias_v2_\' + stamp + \'.sqlite\')\n    backup = sqlite3.connect(destination)\n    try: conn.backup(backup)\n    finally: backup.close()\n    with conn:\n        conn.execute("INSERT INTO metadata VALUES(\'alias_repair_backup_v2\',?)", (str(destination.name),))\n_repair_backup()\n\n# Diagnostic successes contain IDs only. Their origin is retained in the audit.\n_alias_file = STATE_DIR / \'target_alias_diagnostic.json\'\nif _alias_file.exists():\n    _imported = json.loads(_alias_file.read_text(encoding=\'utf-8\'))\n    if not isinstance(_imported, dict): raise RuntimeError(\'Unexpected diagnostic alias-file format.\')\n    with conn:\n        for _old, _canonical in _imported.items():\n            if nid(_old) and nid(_canonical):\n                conn.execute(\'INSERT OR IGNORE INTO work_aliases_v2 VALUES(?,?,?,?,?)\',\n                    (nid(_old), nid(_canonical), \'resolved\', \'saved_diagnostic_lookup\', now()))\n# These two 404s were explicitly returned in the user\'s completed diagnostic run.\n# They remain missing coverage, not deleted publications or zero-citation records.\nwith conn:\n    for _old in (\'W101060335\', \'W101505544\'):\n        conn.execute(\'INSERT OR IGNORE INTO work_aliases_v2 VALUES(?,?,?,?,?)\',\n            (_old, None, \'unresolved_404\', \'user_reported_diagnostic_404\', now()))\n    # Only old citation tasks are superseded. Their items/edges are NOT deleted.\n    for _row in conn.execute("SELECT id,payload FROM tasks WHERE kind=\'citations\'").fetchall():\n        if json.loads(_row[\'payload\']).get(\'alias_policy\') != ALIAS_REPAIR_VERSION:\n            conn.execute("UPDATE tasks SET status=\'superseded\' WHERE id=?", (_row[\'id\'],))\n\n# Shared accounting for every HTTP attempt, including retry and single-ID lookup.\n# Single-record reads are conservatively charged to the local request cap too.\ndef _json_get_v2(path, params=None, allow_404=False):\n    global requests_this_run\n    for attempt in range(4):\n        used_today = conn.execute(\'SELECT COUNT(*) AS n FROM request_ledger WHERE utc_day=?\', (day(),)).fetchone()[\'n\']\n        if requests_this_run >= MAX_REQUESTS_PER_RUN:\n            raise StopCollection(\'Per-run request cap reached; checkpoints saved.\')\n        if used_today >= MAX_REQUESTS_PER_UTC_DAY:\n            raise StopCollection(\'Local UTC-day request cap reached; resume after reset.\')\n        with conn:\n            cursor = conn.execute(\'INSERT INTO request_ledger VALUES(?,?,?)\', (day(), now(), \'attempted\'))\n            ledger_id = cursor.lastrowid\n        requests_this_run += 1\n        time.sleep(REQUEST_INTERVAL_SECONDS)\n        try:\n            response = session.get(\'https://api.openalex.org/\' + path, params=params, timeout=(15, 120))\n        except requests.RequestException:\n            if attempt == 3: raise StopCollection(\'Network failure; progress saved; credentials not logged.\')\n            time.sleep(min(30, 2 ** (attempt + 1))); continue\n        with conn:\n            conn.execute(\'UPDATE request_ledger SET status=? WHERE rowid=?\', (str(response.status_code), ledger_id))\n        code = response.status_code\n        if code == 404 and allow_404: return None\n        if code in (401, 403, 429):\n            raise StopCollection(\'HTTP \' + str(code) + \': check authentication/budget/rate limit; no automatic retry.\')\n        if code >= 500:\n            if attempt == 3: raise StopCollection(\'Repeated HTTP \' + str(code) + \'; resume later. Progress saved.\')\n            time.sleep(min(30, 2 ** (attempt + 1))); continue\n        if code != 200: raise StopCollection(\'HTTP \' + str(code) + \': query needs inspection; no response body or credentials logged.\')\n        try: result = response.json()\n        except ValueError: raise StopCollection(\'Invalid JSON response; progress saved.\')\n        if not isinstance(result, dict): raise StopCollection(\'Unexpected JSON response type.\')\n        return result\n    raise StopCollection(\'Retry limit reached.\')\n\ndef request_page(params):\n    return _json_get_v2(\'works\', params)\n\ndef reload_alias_map_v2():\n    global ALIAS_MAP\n    ALIAS_MAP = {r[\'old_id\']: r[\'canonical_id\'] for r in conn.execute(\n        "SELECT old_id,canonical_id FROM work_aliases_v2 WHERE status=\'resolved\'")}\n\ndef canonical_id_v2(wid):\n    current = nid(wid)\n    if current is None: return None\n    seen = set()\n    while current in ALIAS_MAP and ALIAS_MAP[current] != current:\n        if current in seen: raise RuntimeError(\'Cycle in stored work aliases; inspect work_aliases_v2.\')\n        seen.add(current); current = ALIAS_MAP[current]\n    return current\n\ndef _resolve_single_v2(old_id):\n    result = _json_get_v2(\'works/\' + old_id, {\'corpus\': CORPUS}, allow_404=True)\n    if result is None:\n        with conn:\n            conn.execute(\'INSERT OR REPLACE INTO work_aliases_v2 VALUES(?,?,?,?,?)\',\n                         (old_id, None, \'unresolved_404\', \'single_record_404\', now()))\n        return\n    canonical = nid(result.get(\'id\'))\n    if canonical is None: raise StopCollection(\'Singleton lookup returned no valid work ID; progress saved.\')\n    with conn:\n        conn.execute(\'INSERT OR REPLACE INTO work_aliases_v2 VALUES(?,?,?,?,?)\',\n                     (old_id, canonical, \'resolved\', \'single_record_lookup\', now()))\n\n# A returned ID identical to a requested ID is confirmed directly.\n# A missing requested ID is NEVER paired to an extra returned canonical ID by position.\n# Resolve ambiguous/merged/absent IDs individually instead.\ndef resolve_target_ids_v2(target_ids):\n    targets = set(target_ids)\n    states = {r[\'old_id\']: r[\'status\'] for r in conn.execute(\'SELECT old_id,status FROM work_aliases_v2\')}\n    for old in sorted(targets):\n        if states.get(old) == \'pending_single\':\n            _resolve_single_v2(old)\n    while True:\n        states = {r[\'old_id\']: r[\'status\'] for r in conn.execute(\'SELECT old_id,status FROM work_aliases_v2\')}\n        pending = sorted(targets - set(states))\n        if not pending: break\n        batch = pending[:BATCH_SIZE]\n        response = request_page({\'filter\': \'ids.openalex:\' + \'|\'.join(batch),\n            \'select\': \'id\', \'per_page\': PER_PAGE, \'corpus\': CORPUS})\n        results = response.get(\'results\'); meta = response.get(\'meta\', {})\n        total = meta.get(\'count\')\n        if (not isinstance(results, list) or isinstance(total, bool) or not isinstance(total, int)\n            or total != len(results) or not 0 <= total <= len(batch)):\n            raise StopCollection(\'ID-batch response is incomplete or inconsistent; no alias guesses saved.\')\n        returned = [nid(w.get(\'id\')) if isinstance(w, dict) else None for w in results]\n        if any(w is None for w in returned) or len(set(returned)) != len(returned):\n            raise StopCollection(\'ID-batch response contains invalid/duplicate IDs.\')\n        direct = set(returned) & set(batch)\n        with conn:\n            for old in batch:\n                conn.execute(\'INSERT OR IGNORE INTO work_aliases_v2 VALUES(?,?,?,?,?)\',\n                    (old, old if old in direct else None,\n                     \'resolved\' if old in direct else \'pending_single\', \'batch_id_lookup\', now()))\n        for old in batch:\n            if old not in direct: _resolve_single_v2(old)\n    reload_alias_map_v2()\n\nreload_alias_map_v2()\n\n# Retain all validation, but compare reference/target IDs in the same canonical space.\n_base_validate_page_v2 = validate_page\n\ndef validate_page(task, body):\n    if task[\'kind\'] != \'citations\': return _base_validate_page_v2(task, body)\n    normalized = dict(body)\n    records = []\n    for work in body.get(\'results\', []):\n        if not isinstance(work, dict): records.append(work); continue\n        copied = dict(work)\n        refs = work.get(\'referenced_works\')\n        if isinstance(refs, list):\n            # Preserve invalid entries so the original validator still flags them.\n            copied[\'referenced_works\'] = [canonical_id_v2(x) if nid(x) else x for x in refs]\n        records.append(copied)\n    normalized[\'results\'] = records\n    return _base_validate_page_v2(task, normalized)\n\n_base_run_task_v2 = run_task\n\ndef _restart_drifted_query_v2(task_id):\n    prior_restarts = conn.execute(\'SELECT COUNT(*) AS n FROM query_restarts_v2 WHERE task=?\', (task_id,)).fetchone()[\'n\']\n    if prior_restarts >= 2: return False\n    with conn:\n        row = conn.execute(\'INSERT INTO query_restarts_v2(task,reason,at) VALUES(?,?,?)\',\n            (task_id, \'api_total_changed_during_pagination\', now()))\n        restart_id = row.lastrowid\n        conn.execute(\'INSERT INTO retired_items_v2 SELECT ?,task,id,year,author_ids FROM items WHERE task=?\', (restart_id, task_id))\n        conn.execute(\'INSERT INTO retired_edges_v2 SELECT ?,task,citing,cited,year FROM edges WHERE task=?\', (restart_id, task_id))\n        conn.execute(\'DELETE FROM items WHERE task=?\', (task_id,))\n        conn.execute(\'DELETE FROM edges WHERE task=?\', (task_id,))\n        conn.execute("UPDATE tasks SET status=\'pending\',cursor=\'*\',expected=NULL,pages=0,issue=\'\',started=NULL,finished=NULL WHERE id=?", (task_id,))\n    return True\n\ndef run_task(task_id):\n    while True:\n        task = conn.execute(\'SELECT * FROM tasks WHERE id=?\', (task_id,)).fetchone()\n        if task[\'status\'] == \'blocked\':\n            if task[\'issue\'] != \'api_total_changed_during_pagination\' or not _restart_drifted_query_v2(task_id):\n                raise StopCollection(\'Query remains blocked; inspect query_progress.csv. No validation was bypassed.\')\n        try:\n            _base_run_task_v2(task_id)\n            return\n        except StopCollection:\n            task = conn.execute(\'SELECT * FROM tasks WHERE id=?\', (task_id,)).fetchone()\n            if task[\'status\'] == \'blocked\' and task[\'issue\'] == \'api_total_changed_during_pagination\':\n                if _restart_drifted_query_v2(task_id): continue\n            raise\n'

DRIVER = '\n_legacy_assemble_targets_v2 = assemble_targets\n\n# The raw legacy plan hash remains intact to preserve compatibility with the checkpoint.\n# New citation tasks have a versioned payload and never reuse legacy citation edges.\ndef assemble_targets():\n    global unresolved_by_author\n    raw_mapping, audit, raw_plan, refresh_complete = _legacy_assemble_targets_v2()\n    # The original helper can create legacy tasks after portfolio completion; supersede them.\n    with conn:\n        for tid, _ in raw_plan:\n            conn.execute("UPDATE tasks SET status=\'superseded\' WHERE id=?", (tid,))\n    states = {r[\'old_id\']: r[\'status\'] for r in conn.execute(\'SELECT old_id,status FROM work_aliases_v2\')}\n    raw_targets = set().union(*raw_mapping.values())\n    resolution_done = refresh_complete and all(states.get(w) in (\'resolved\',\'unresolved_404\') for w in raw_targets)\n    reload_alias_map_v2()\n    mapping = {}; unresolved_by_author = {}; plans = []\n    audit = audit.copy()\n    merged_counts = {}; unresolved_counts = {}; resolved_flags = {}\n    for aid, raw_ids in raw_mapping.items():\n        unresolved = {w for w in raw_ids if states.get(w) != \'resolved\'}\n        unresolved_by_author[aid] = unresolved\n        mapping[aid] = {canonical_id_v2(w) for w in raw_ids if states.get(w) == \'resolved\'}\n        merged_counts[aid] = sum(w in ALIAS_MAP and canonical_id_v2(w) != w for w in raw_ids)\n        unresolved_counts[aid] = len(unresolved)\n        resolved_flags[aid] = not unresolved\n    audit[\'n_merged_target_ids\'] = audit.author_id.map(merged_counts)\n    audit[\'n_unresolved_target_ids\'] = audit.author_id.map(unresolved_counts)\n    audit[\'all_target_ids_resolved\'] = audit.author_id.map(resolved_flags)\n    audit[\'n_canonical_target_works\'] = audit.author_id.map(lambda a: len(mapping[a]))\n    if resolution_done:\n        canonical_targets = sorted(set().union(*mapping.values()))\n        for start in range(0,len(canonical_targets),BATCH_SIZE):\n            targets = canonical_targets[start:start+BATCH_SIZE]\n            payload = {\'targets\': targets, \'year_lo\': WINDOW_LO, \'year_hi\': WINDOW_HI,\n                       \'alias_policy\': ALIAS_REPAIR_VERSION}\n            plans.append((add_task(\'citations\',payload),targets))\n        fingerprint = stable_hash(sorted((a,sorted(ids)) for a,ids in mapping.items()))\n        old = conn.execute("SELECT value FROM metadata WHERE key=\'canonical_target_plan_hash_v2\'").fetchone()\n        if old and old[\'value\'] != fingerprint:\n            raise RuntimeError(\'Canonical plan changed after locking. Use a new version; do not mix plans.\')\n        with conn:\n            conn.execute("INSERT OR IGNORE INTO metadata VALUES(\'canonical_target_plan_hash_v2\',?)", (fingerprint,))\n    with conn:\n        conn.execute(\'DELETE FROM active_citation_tasks_v2\')\n        conn.executemany(\'INSERT INTO active_citation_tasks_v2 VALUES(?)\',[(tid,) for tid,_ in plans])\n    return mapping,audit,plans,resolution_done\n\ntry:\n    if RUN_API_COLLECTION:\n        session.headers[\'Authorization\'] = \'Bearer \' + get_api_key()\n        try:\n            for tid in portfolio_tasks.values(): run_task(tid)\n            raw_mapping,_,_,refresh_complete = _legacy_assemble_targets_v2()\n            if not refresh_complete:\n                raise StopCollection(\'Portfolio refresh still incomplete. Inspect query progress.\')\n            raw_ids = set().union(*raw_mapping.values())\n            print(\'Canonical target-ID audit: batched lookups; individual requests only for ambiguous/absent IDs.\')\n            resolve_target_ids_v2(raw_ids)\n            mapping,portfolio_audit,citation_plan,all_refresh_done = assemble_targets()\n            if all_refresh_done:\n                print(\'Canonical citation batches:\',len(citation_plan),\'| Pagination adds requests.\')\n                for tid,_ in citation_plan: run_task(tid)\n                stop_reason = \'all_resolvable_target_queries_complete; inspect unresolved-ID coverage\'\n            else:\n                stop_reason = \'canonical_target_audit_incomplete\'\n        finally:\n            session.headers.pop(\'Authorization\',None)\n    else:\n        stop_reason = \'preview_only_no_live_requests\'\nexcept StopCollection as exc:\n    stop_reason = str(exc)\nfinally:\n    session.headers.pop(\'Authorization\',None)\nmapping,portfolio_audit,citation_plan,all_refresh_done = assemble_targets()\nprint(\'Collection status:\',stop_reason)\nprint(\'HTTP attempts this run:\',requests_this_run)\nprint(\'Resolved target IDs:\',conn.execute("SELECT COUNT(*) AS n FROM work_aliases_v2 WHERE status=\'resolved\'").fetchone()[\'n\'])\nprint(\'404 target IDs remain explicit coverage gaps. Resume this notebook; no key is stored.\')\n'


def repair_notebook(source, destination=None):
    source = Path(source)
    nb = nbformat.read(source, as_version=4)
    markers = {
        'setup': 'def root_dir():',
        'inventory': 'inventory_rows = []',
        'database': 'def validate_page(task, body):',
        'collection': 'def assemble_targets():',
        'aggregate': 'edge_counts = Counter()',
        'export': "summary_values = {",
    }
    selected = {}
    for i, cell in enumerate(nb.cells):
        if cell.cell_type != 'code': continue
        for role, marker in markers.items():
            if marker in cell.source:
                if role in selected: raise RuntimeError('Ambiguous notebook layout for ' + role)
                selected[role] = i
    if set(selected) != set(markers):
        raise RuntimeError('Notebook differs from expected source: missing ' + repr(set(markers) - set(selected)))
    setup = nb.cells[selected['setup']].source
    database = nb.cells[selected['database']].source
    collection = nb.cells[selected['collection']].source
    aggregate = nb.cells[selected['aggregate']].source
    export = nb.cells[selected['export']].source
    if 'ALIAS_REPAIR_VERSION' in database:
        raise RuntimeError('This notebook already contains the v2 alias repair.')
    split = "\ntry:\n    if RUN_API_COLLECTION:"
    if collection.count(split) != 1:
        raise RuntimeError('Cannot safely locate collection driver.')
    raw_collection = collection.split(split)[0]
    old_edge_query = "SELECT cited,year,COUNT(DISTINCT citing) AS n FROM edges GROUP BY cited,year"
    new_edge_query = ("SELECT e.cited,e.year,COUNT(DISTINCT e.citing) AS n "
                     "FROM edges e JOIN active_citation_tasks_v2 a ON a.id=e.task GROUP BY e.cited,e.year")
    if aggregate.count(old_edge_query) != 1:
        raise RuntimeError('Unexpected edge-count query; no changes written.')
    old_done = "done = all_refresh_done and bool(target_ids)"
    if aggregate.count(old_done) != 1:
        raise RuntimeError('Unexpected completeness check; no changes written.')
    aggregate = aggregate.replace(old_edge_query, new_edge_query).replace(
        old_done, "done = all_refresh_done and not unresolved_by_author.get(aid) and bool(target_ids)")
    # Original exports calculate query progress at the start of their cell.
    # Keep all tasks visible (old citation tasks are explicitly 'superseded').
    insert_before = "SNAPSHOT_DIR=ROOT/"
    if export.count(insert_before) != 1:
        raise RuntimeError('Unexpected snapshot export layout; no changes written.')
    extra_exports = """
alias_audit = pd.read_sql_query('SELECT * FROM work_aliases_v2 ORDER BY old_id',conn)
restart_audit = pd.read_sql_query('SELECT * FROM query_restarts_v2 ORDER BY restart_id',conn)
unresolved_rows = [{'author_id':aid,'old_target_id':wid,
    'reason':'unresolved_404_or_alias_audit_pending'}
    for aid,ids in unresolved_by_author.items() for wid in sorted(ids)]
unresolved_audit = pd.DataFrame(unresolved_rows,columns=['author_id','old_target_id','reason'])
"""
    export = export.replace(insert_before, extra_exports + '\n' + insert_before)
    table_end = "'existing_citation_file_inventory.csv':inventory}"
    if table_end not in export: raise RuntimeError('Unexpected export table layout.')
    export = export.replace(table_end,
        "'existing_citation_file_inventory.csv':inventory,"
        "'work_alias_audit.csv':alias_audit,'query_restart_audit.csv':restart_audit,"
        "'unresolved_target_coverage.csv':unresolved_audit}")
    meta_key = "'credentials_saved':False"
    if meta_key not in export: raise RuntimeError('Unexpected manifest layout.')
    export = export.replace(meta_key,
        "'alias_repair_policy':ALIAS_REPAIR_VERSION,"
        "'legacy_citation_tasks':'superseded and excluded from v2 totals',"
        "'unresolved_alias_author_count':int((portfolio_audit.n_unresolved_target_ids>0).sum()),"
        + meta_key)
    nb.cells[selected['database']].source = database + '\n\n' + ENGINE
    nb.cells[selected['collection']].source = raw_collection + '\n\n' + DRIVER
    nb.cells[selected['aggregate']].source = aggregate
    nb.cells[selected['export']].source = export
    keep_indices = set(selected.values())
    last_core = max(keep_indices)
    cleaned = []
    for i, cell in enumerate(nb.cells):
        if cell.cell_type == 'code' and i not in keep_indices: continue
        if cell.cell_type != 'code' and i > last_core: continue
        if cell.cell_type == 'code':
            cell.outputs = []
            cell.execution_count = None
            cell.metadata = {}
            ast.parse(cell.source)
        cleaned.append(cell)
    note = nbformat.v4.new_markdown_cell("""## Canonical-ID repair — read before running

This version removes ad-hoc diagnostic cells and stale execution outputs. The original notebook is unchanged.

- Uses the SAME local SQLite checkpoint and automatically makes a one-time backup before importing aliases or superseding citation tasks.
- Reuses completed portfolio downloads and the request ledger. Legacy citation tasks/edges are preserved but superseded, because they did not account for merged target IDs.
- Imports saved successful diagnostic aliases. The two reported 404 IDs remain explicit unresolved coverage gaps.
- Checks targets in batches of up to 100 IDs (1 list request per batch). Only ambiguous/missing IDs need individual lookups; never pair old/canonical IDs by result order.
- Resolves target IDs BEFORE creating the new canonical citation plan. Several capped runs may finish only ID auditing. This is expected, not lost progress.
- Deduplicates canonical work IDs per author; one canonical target belongs to one new citation batch. Aggregation excludes all superseded legacy batches.
- Missing target IDs keep the affected author's main citation series blank. Other authors can become usable as their canonical query batches finish.
- Server/network retries are bounded. 401/403/429 stop collection. Changed API totals trigger at most two fresh-query retries; partial evidence is archived before each restart. All other validation guards remain enabled.
- No API key is embedded, and upstream outputs remain untouched. The free daily budget is NOT guaranteed to cover the whole collection.

Run this fixed notebook from a fresh kernel. Do not run its old diagnostic cells or delete the checkpoint. Publish the new progress snapshots only as provisional until query coverage is complete. Inspect `work_alias_audit.csv`, `unresolved_target_coverage.csv`, and `query_restart_audit.csv`.
""")
    nb.cells = [note, *cleaned]
    nb.metadata.pop('widgets', None)
    nbformat.validate(nb)
    destination = Path(destination) if destination else source.with_name(source.stem + '_fixed.ipynb')
    if destination.resolve() == source.resolve():
        raise RuntimeError('Refusing to overwrite original notebook.')
    if destination.exists():
        raise FileExistsError('Fixed output already exists; rename it before rerunning the repair.')
    nbformat.write(nb, destination)
    if not destination.is_file() or destination.stat().st_size == 0:
        raise RuntimeError('Notebook export failed.')
    return destination

if __name__ == '__main__':
    source = Path(sys.argv[1]) if len(sys.argv)>1 else Path('notebooks/05_yearly_citations.ipynb')
    dest = repair_notebook(source)
    print('Created:', dest)
    print('Original notebook untouched. Open the fixed notebook, restart its kernel, then Run All.')
