#!/usr/bin/env python3
"""Pure offline SWE-bench workflow-study artifact pipeline."""
from __future__ import annotations

import argparse, hashlib, json, math, os, re, secrets, stat, sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
SCRIPT_DIR = Path(__file__).resolve(strict=True).parent
RUNTIME = SCRIPT_DIR.parent

def storage_boundary(runtime: Path) -> Path:
    """Return the checkout root, or the owning skill-bundle root after relocation."""
    checkout = runtime.parents[2] if len(runtime.parents) > 2 else None
    if checkout is not None and runtime == checkout / "skills" / "agy-worker" / "runtime":
        try:
            wrapper = os.stat(
                checkout / "swebench-workflow-study.sh", follow_symlinks=False
            )
        except OSError:
            pass
        else:
            if stat.S_ISREG(wrapper.st_mode):
                return checkout
    return runtime.parent

STORAGE_BOUNDARY = storage_boundary(RUNTIME)

SCHEMAS = RUNTIME / "schemas"
PLAN_SCHEMA = SCHEMAS / "swebench-workflow-study-plan.schema.json"
REPORT_SCHEMA = SCHEMAS / "swebench-workflow-study-report.schema.json"
ADVISORY_SCHEMA = SCHEMAS / "swebench-workflow-study-advisory.schema.json"
MAX_INPUT_BYTES = 16 * 1024 * 1024
ARTIFACTS = ("plan.json", "imported_results.json", "report.json", "advisory.json")
ARMS = ("codex-only", "agy-explore-first", "agy-task-first", "agy-project-first", "second-eye")
FAILURES = ("none", "pre_subject_infrastructure", "subject_failure", "evaluator_failure")
TOKEN_FIELDS = ("input", "cached_input", "fresh_input", "cache_write", "output", "reasoning_output")
TOKEN_CORE_FIELDS = ("input", "cached_input", "fresh_input", "output", "reasoning_output")
MANDATORY_ACCEPTANCE_FIELDS = ("evaluator_resolved", "clean_driver_gate", "independent_diff_acceptance", "exact_bindings_verified", "accepted_solution")
BUDGET_FIELDS = ("max_tasks", "max_repairs_per_cell", "max_wall_time_seconds_per_cell", "max_codex_tokens_per_cell", "max_agy_tokens_per_cell", "max_observed_billed_cost_per_cell", "max_version_bound_list_price_cost_per_cell")
TELEMETRY_PARTIES = ("codex", "agy")
TELEMETRY_BINDING_FIELDS = ("accounting", "tokenizer", "currency", "price_source")
PLAN_STRING_FIELDS = ("dataset_revision", "evaluator_revision", "permissions_policy", "network_policy", "codex_model", "codex_effort", "agy_model", "agy_effort")
MAX_TASKS = 10_000
MAX_CELLS = 50_000
MAX_REPAIRS = 1_000_000
MAX_WALL_TIME = 1_000_000_000.0
MAX_TOKENS = 1_000_000_000_000
MAX_COST = 1_000_000_000.0
MAX_INTEGER = 1_000_000_000_000_000
MAX_FLOAT = 1e15

SAFE_ID = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9._:+-]{0,99}\Z")
DIGEST = re.compile(r"[0-9a-f]{64}\Z")
FORBIDDEN = re.compile(
    r"(?i)(secret|password|credential|auth|token|bearer|private.?key|@|https?://|file://|/"
    r"Users/|/home/|\\|[\r\n\x00-\x1f])"
)
PLACEHOLDERS={"none","unknown","placeholder","todo","tbd","null","undefined","n/a","na","unspecified","default","temp","tmp","test","dummy","fake","mock"}

class ValidationFailure(ValueError):
    pass

def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value,allow_nan=False,ensure_ascii=True,sort_keys=True,separators=(",",":")).encode("utf-8")

def reject_duplicates(pairs: list[tuple[str,Any]]) -> dict[str,Any]:
    result={}
    for key,value in pairs:
        if key in result:
            raise ValidationFailure("duplicate JSON key")
        result[key]=value
    return result

def parse_json_bytes(payload: bytes, label: str) -> Any:
    if not payload or len(payload)>MAX_INPUT_BYTES:
        raise ValidationFailure(f"{label} is empty or oversized")
    try:
        return json.loads(payload.decode("utf-8"),object_pairs_hook=reject_duplicates)
    except (UnicodeDecodeError,ValueError,ValidationFailure) as exc:
        raise ValidationFailure(f"{label} is not valid unique-key UTF-8 JSON") from exc

def schema_type_matches(value: Any, expected: str) -> bool:
    return {
        "object":isinstance(value,dict),
        "array":isinstance(value,list),
        "string":isinstance(value,str),
        "boolean":type(value) is bool,
        "number":type(value) in (int,float),
        "integer":type(value) is int,
        "null":value is None,
    }.get(expected,False)

def validate_schema(value: Any, schema: dict[str,Any], location: str = "$", root_schema: dict[str,Any] | None = None) -> None:
    if root_schema is None:
        root_schema=schema
    reference=schema.get("$ref")
    if reference is not None:
        if not isinstance(reference,str) or not reference.startswith("#/"):
            raise ValidationFailure(f"{location} uses an unsupported schema reference")
        target:Any=root_schema
        for component in reference[2:].split("/"):
            component=component.replace("~1","/").replace("~0","~")
            if not isinstance(target,dict) or component not in target:
                raise ValidationFailure(f"{location} uses an unresolved schema reference")
            target=target[component]
        if not isinstance(target,dict):
            raise ValidationFailure(f"{location} uses an invalid schema reference")
        validate_schema(value,target,location,root_schema)
        return
    if "oneOf" in schema:
        accepted=0
        for alternative in schema["oneOf"]:
            try: validate_schema(value,alternative,location,root_schema)
            except ValidationFailure: continue
            accepted+=1
        if accepted!=1: raise ValidationFailure(f"{location} does not match exactly one schema alternative")
    expected=schema.get("type")
    if expected is not None and not schema_type_matches(value,expected): raise ValidationFailure(f"{location} has the wrong type")
    if "enum" in schema and value not in schema["enum"]: raise ValidationFailure(f"{location} has a forbidden value")
    if isinstance(value,str):
        if len(value)<schema.get("minLength",0) or len(value)>schema.get("maxLength",len(value)): raise ValidationFailure(f"{location} has invalid length")
        pattern=schema.get("pattern")
        if pattern is not None and re.search(pattern,value) is None: raise ValidationFailure(f"{location} does not match its pattern")
    if type(value) in (int,float) and not isinstance(value,bool):
        try:
            f=float(value)
            if not math.isfinite(f): raise ValidationFailure(f"{location} must be finite")
        except OverflowError: raise ValidationFailure(f"{location} is oversized")
        if value<schema.get("minimum",value) or value>schema.get("maximum",value): raise ValidationFailure(f"{location} is outside its range")
    if isinstance(value,list):
        if len(value)<schema.get("minItems",0) or len(value)>schema.get("maxItems",len(value)): raise ValidationFailure(f"{location} has invalid item count")
        if "items" in schema:
            for index,item in enumerate(value): validate_schema(item,schema["items"],f"{location}[{index}]",root_schema)
    if isinstance(value,dict):
        required=set(schema.get("required",[])); properties=schema.get("properties",{})
        if required-set(value): raise ValidationFailure(f"{location} is missing required fields")
        if schema.get("additionalProperties") is False and set(value)-set(properties): raise ValidationFailure(f"{location} has unexpected fields")
        for key,child in properties.items():
            if key in value: validate_schema(value[key],child,f"{location}.{key}",root_schema)

def fail(message: str, code: str = "invalid_input") -> None:
    """Stop with a bounded, stable semantic category and sanitized detail."""
    print(f"error: {code}: {message}", file=sys.stderr)
    raise SystemExit(1)

def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()

def number(value: Any, label: str, integer: bool = False, maximum: float | int | None = None) -> float | int:
    if isinstance(value, bool):
        fail(f"{label} must be a number, not boolean", "numeric_validation")
    if integer:
        if not isinstance(value, int) or isinstance(value, bool):
            fail(f"{label} must be an integer", "numeric_validation")
    else:
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            fail(f"{label} must be finite and non-negative", "numeric_validation")
    try:
        f = float(value)
    except (OverflowError, ValueError):
        fail(f"{label} is oversized or non-convertible", "numeric_validation")
    if not math.isfinite(f) or f < 0:
        fail(f"{label} must be finite and non-negative", "finite_value")
    if integer and value > (maximum if maximum is not None else MAX_INTEGER):
        fail(f"{label} exceeds maximum integer bound", "numeric_validation")
    if not integer and f > (maximum if maximum is not None else MAX_FLOAT):
        fail(f"{label} exceeds maximum float bound", "numeric_validation")
    return value

def safe(value: Any, label: str, is_digest: bool = False, code: str = "privacy") -> None:
    if not isinstance(value, str) or (DIGEST if is_digest else SAFE_ID).fullmatch(value) is None or FORBIDDEN.search(value) or re.search(r"\d{4}-\d{2}-\d{2}",value) or value.lower() in PLACEHOLDERS:
        fail(f"{label} is not a bounded privacy-safe identifier", code)

def open_root(path: Path) -> tuple[Path, int]:
    try:
        fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
        st = os.fstat(fd); resolved = path.resolve(strict=True)
    except (OSError, ValueError):
        fail("result root is unavailable")
    if st.st_uid != os.getuid() or stat.S_IMODE(st.st_mode) != 0o700:
        os.close(fd); fail("result root must be owner-0700", "root_permissions")
    try:
        resolved.relative_to(STORAGE_BOUNDARY)
    except ValueError:
        return resolved, fd
    os.close(fd); fail("result root must be outside the repository", "root_location")

def inventory(fd: int) -> tuple[str, ...]:
    try: names = tuple(sorted(os.listdir(fd)))
    except OSError: fail("result root inventory is unavailable")
    if any(name not in ARTIFACTS for name in names): fail("result root contains an unexpected entry")
    return names

def require_stage(fd: int, expected: tuple[str, ...]) -> None:
    if inventory(fd) != tuple(sorted(expected)):
        fail("result root does not match the required lifecycle stage", "lifecycle_stage")

def read_json_fd(fd: int, label: str) -> tuple[Any, bytes]:
    st = os.fstat(fd)
    if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1 or st.st_size > MAX_INPUT_BYTES: fail(f"{label} must be one bounded regular file")
    chunks=[]; left=MAX_INPUT_BYTES+1
    while left:
        part=os.read(fd,min(65536,left))
        if not part: break
        chunks.append(part); left-=len(part)
    raw=b"".join(chunks)
    if len(raw)>MAX_INPUT_BYTES: fail(f"{label} exceeds the input bound")
    try: return parse_json_bytes(raw,label),raw
    except ValidationFailure: fail(f"{label} is not valid JSON")

def read_bundled_json(path: Path, label: str) -> tuple[Any, bytes]:
    try: fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
    except OSError: fail(f"{label} is unavailable")
    try: return read_json_fd(fd,label)
    finally: os.close(fd)

def require_private_input(fd: int, label: str) -> None:
    st=os.fstat(fd)
    if st.st_uid!=os.getuid() or stat.S_IMODE(st.st_mode)!=0o600:
        fail(f"{label} must be caller-owned mode-0600", "input_permissions")

def read_private_json(path: Path, label: str) -> tuple[Any, bytes]:
    try: fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
    except OSError: fail(f"{label} is unavailable", "input_unavailable")
    try:
        require_private_input(fd,label)
        return read_json_fd(fd,label)
    finally: os.close(fd)

def read_private_raw(path: Path,label: str)->bytes:
    try: fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
    except OSError: fail(f"{label} is unavailable", "input_unavailable")
    try:
        require_private_input(fd,label)
        st=os.fstat(fd)
        if not stat.S_ISREG(st.st_mode) or st.st_nlink!=1 or st.st_size>MAX_INPUT_BYTES: fail(f"{label} must be one bounded regular file")
        chunks=[]; left=MAX_INPUT_BYTES+1
        while left:
            part=os.read(fd,min(65536,left))
            if not part: break
            chunks.append(part); left-=len(part)
        raw=b"".join(chunks)
        if len(raw)>MAX_INPUT_BYTES: fail(f"{label} exceeds the input bound")
        return raw
    finally: os.close(fd)

def read_artifact(root_fd: int, name: str) -> tuple[Any, bytes]:
    try: fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=root_fd)
    except OSError: fail(f"{name} is unavailable")
    try:
        st=os.fstat(fd)
        if st.st_uid!=os.getuid() or stat.S_IMODE(st.st_mode)!=0o600: fail(f"{name} has invalid ownership or mode")
        value,raw=read_json_fd(fd,name)
        if raw!=canonical_bytes(value): fail(f"{name} is not canonical")
        return value,raw
    finally: os.close(fd)

def publish(root_fd: int, name: str, value: Any) -> None:
    raw=canonical_bytes(value)
    # Bound the actual canonical bytes, not the smaller caller representation.
    # Fail before creating a temporary or final entry so the prior lifecycle
    # stage remains complete and retryable.
    if len(raw)>MAX_INPUT_BYTES:
        fail("canonical artifact exceeds the storage bound", "publication_size")
    temp=f".{name}.{secrets.token_hex(12)}.tmp"; out=-1; final_fd=-1; linked=False; temp_st=None
    try:
        out=os.open(temp,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=root_fd); os.fchmod(out,0o600)
        temp_st=os.fstat(out)
        view=memoryview(raw)
        while view:
            n=os.write(out,view)
            if n<=0: raise OSError("publication write failed")
            view=view[n:]
        os.fsync(out); os.close(out); out=-1
        os.link(temp,name,src_dir_fd=root_fd,dst_dir_fd=root_fd,follow_symlinks=False); linked=True
        final_fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=root_fd)
        st=os.fstat(final_fd)
        if (st.st_dev,st.st_ino)!=(temp_st.st_dev,temp_st.st_ino) or not stat.S_ISREG(st.st_mode) or st.st_nlink!=2 or st.st_uid!=os.getuid() or stat.S_IMODE(st.st_mode)!=0o600:
            raise OSError("publication identity changed")
        os.unlink(temp,dir_fd=root_fd)
        st=os.fstat(final_fd)
        if st.st_nlink!=1:
            raise OSError("publication link count changed")
        os.fsync(root_fd)
    except FileExistsError:
        fail("study artifacts never overwrite", "publication_no_overwrite")
    except OSError:
        if linked and temp_st is not None:
            try:
                st=os.stat(name,dir_fd=root_fd,follow_symlinks=False)
                if (st.st_dev,st.st_ino)==(temp_st.st_dev,temp_st.st_ino):
                    os.unlink(name,dir_fd=root_fd)
                    os.fsync(root_fd)
            except OSError:
                pass
        fail("artifact publication failed", "publication_failure")
    finally:
        if out>=0: os.close(out)
        if final_fd>=0: os.close(final_fd)
        try: os.unlink(temp,dir_fd=root_fd)
        except OSError: pass

def load_schema(path: Path) -> dict[str,Any]:
    value,_=read_bundled_json(path,"bundled schema")
    if not isinstance(value,dict): fail("bundled schema is invalid")
    return value

def validate_plan(plan: Any, require_binding: bool = True) -> dict[str,Any]:
    if not isinstance(plan,dict): fail("plan must be an object", "plan_schema")
    # Validate privacy before ordering so a sensitive value can never be hidden by
    # a secondary ordering diagnostic.
    tasks=plan.get("tasks")
    if not isinstance(tasks,list) or not tasks:
        fail("plan must contain a nonempty task commitment list", "plan_tasks")
    for task in tasks:
        safe(task,"plan task",code="plan_privacy")
    if len(tasks)!=len(set(tasks)):
        fail("plan tasks must be unique", "plan_tasks")
    if tasks!=sorted(tasks):
        fail("plan tasks must use deterministic order", "plan_ordering")
    budgets=plan.get("budgets")
    if not isinstance(budgets,dict) or set(budgets)!=set(BUDGET_FIELDS):
        fail("plan budgets must contain the exact closed fields", "plan_schema")
    for field in BUDGET_FIELDS:
        is_int = field in {"max_tasks","max_repairs_per_cell","max_codex_tokens_per_cell","max_agy_tokens_per_cell"}
        max_bound = MAX_TASKS if field=="max_tasks" else (MAX_REPAIRS if field=="max_repairs_per_cell" else (MAX_TOKENS if "tokens" in field else MAX_COST))
        number(budgets[field],f"plan budget {field}",integer=is_int,maximum=max_bound)
    if budgets["max_tasks"]==0 or len(tasks)>budgets["max_tasks"]: fail("plan task budget is empty or exceeded")
    schema_value=dict(plan); schema_value.pop("plan_content_sha256",None)
    try: validate_schema(schema_value,load_schema(PLAN_SCHEMA))
    except ValidationFailure: fail("plan does not match the closed schema", "plan_schema")
    binding=plan.get("plan_content_sha256")
    if require_binding:
        if not isinstance(binding,str): fail("plan content binding is missing", "plan_binding")
        content=dict(plan); del content["plan_content_sha256"]
        if binding!=sha(canonical_bytes(content)): fail("plan content binding drifted", "plan_binding")
    elif binding is not None:
        fail("input plan must not seed a derived content binding", "plan_binding")
    for field in PLAN_STRING_FIELDS:
        safe(plan[field],f"plan.{field}",code="plan_privacy")
    bindings=plan.get("telemetry_bindings")
    if not isinstance(bindings,dict) or set(bindings)!=set(TELEMETRY_PARTIES):
        fail("plan telemetry bindings must contain exact Codex and agy records", "plan_schema")
    for party in TELEMETRY_PARTIES:
        binding=bindings[party]
        if not isinstance(binding,dict) or set(binding)!=set(TELEMETRY_BINDING_FIELDS):
            fail(f"plan {party} telemetry binding has an invalid shape", "plan_schema")
        for field in TELEMETRY_BINDING_FIELDS:
            safe(binding[field],f"plan.telemetry_bindings.{party}.{field}",code="plan_privacy")
    for field in ("repository_base","repository_image"):
        safe(plan[field],f"plan.{field}",True,"plan_binding")
    safe(plan["frozen_prompt_digest"],"plan.frozen_prompt_digest",True,"plan_binding")
    if tuple(plan["arms"])!=ARMS or plan["ordering"]!="task_then_arm":
        fail("plan ordering or arms changed", "plan_arms")
    return plan

def usage(value: Any,label: str)->tuple[int|None,bool]:
    if not isinstance(value,dict) or set(value)!=set(TOKEN_FIELDS):
        fail(f"{label} has invalid counters", "telemetry_shape")
    present=[value[k] is not None for k in TOKEN_CORE_FIELDS]
    if any(present)!=all(present):
        fail(f"{label} must be wholly present or unavailable", "telemetry_availability")
    if not any(present):
        if value["cache_write"] is not None:
            fail(f"{label}.cache_write cannot exist without core counters", "telemetry_availability")
        return None,False
    for k in TOKEN_CORE_FIELDS:
        number(value[k],f"{label}.{k}",integer=True,maximum=MAX_TOKENS)
    if value["cache_write"] is not None:
        number(value["cache_write"],f"{label}.cache_write",integer=True,maximum=MAX_TOKENS)
    if value["input"]!=value["cached_input"]+value["fresh_input"]:
        fail(f"{label}.input must equal cached_input plus fresh_input", "telemetry_arithmetic")
    if value["reasoning_output"]>value["output"]:
        fail(f"{label}.reasoning_output exceeds output", "telemetry_arithmetic")
    # Cached/fresh are a partition of input; reasoning is a subset of output;
    # cache-write remains separately observed. None is counted twice.
    return value["input"]+value["output"],True

def cost(value: Any,label: str)->None:
    if not isinstance(value,dict) or set(value)!={"observed_billed","version_bound_list_price"}: fail(f"{label} has invalid fields")
    for k in value:
        if value[k] is not None: number(value[k],f"{label}.{k}",integer=False,maximum=MAX_COST)

def token_bindings_comparable(plan:dict[str,Any])->bool:
    bindings=plan["telemetry_bindings"]
    return all(
        bindings["codex"][field]==bindings["agy"][field]
        for field in ("accounting","tokenizer")
    )

def cost_bindings_comparable(plan:dict[str,Any],basis:str)->bool:
    bindings=plan["telemetry_bindings"]
    if bindings["codex"]["currency"]!=bindings["agy"]["currency"]:
        return False
    return basis=="observed_billed" or bindings["codex"]["price_source"]==bindings["agy"]["price_source"]

def validate_cell(cell: Any,plan:dict[str,Any])->dict[str,Any]:
    budgets=plan["budgets"]
    required={"arm","failure_class","evaluator_resolved","clean_driver_gate","independent_diff_acceptance","exact_bindings_verified","accepted_solution","repair_count","wall_time_seconds","codex_usage","codex_cost","agy_usage","agy_cost"}
    if not isinstance(cell,dict) or set(cell)!=required: fail("study cell does not match the closed shape", "cell_schema")
    if cell["arm"] not in ARMS or cell["failure_class"] not in FAILURES: fail("unknown arm or failure classification", "cell_classification")
    gates=("evaluator_resolved","clean_driver_gate","independent_diff_acceptance","exact_bindings_verified")
    if any(not isinstance(cell[k],bool) for k in gates+("accepted_solution",)): fail("study cell gates must be boolean")
    accepted=cell["failure_class"]=="none" and all(cell[k] for k in gates)
    if cell["accepted_solution"] is not accepted:
        fail("accepted_solution is not derived from every mandatory gate", "acceptance_derivation")
    number(cell["repair_count"],"repair_count",integer=True,maximum=budgets["max_repairs_per_cell"])
    number(cell["wall_time_seconds"],"wall_time_seconds",integer=False,maximum=budgets["max_wall_time_seconds_per_cell"])
    ctotal,cok=usage(cell["codex_usage"],"Codex usage"); atotal,aok=usage(cell["agy_usage"],"agy usage")
    cost(cell["codex_cost"],"Codex cost"); cost(cell["agy_cost"],"agy cost")
    if ctotal is not None and ctotal>budgets["max_codex_tokens_per_cell"]: fail("Codex token budget exceeded", "token_budget")
    if atotal is not None and atotal>budgets["max_agy_tokens_per_cell"]: fail("agy token budget exceeded", "token_budget")
    for party in ("codex","agy"):
        for field,budget in (("observed_billed","max_observed_billed_cost_per_cell"),("version_bound_list_price","max_version_bound_list_price_cost_per_cell")):
            value=cell[f"{party}_cost"][field]
            if value is not None and value>budgets[budget]: fail("cost budget exceeded", "cost_budget")
    if cell["arm"]!="codex-only":
        for field,budget in (("observed_billed","max_observed_billed_cost_per_cell"),("version_bound_list_price","max_version_bound_list_price_cost_per_cell")):
            codex_value=cell["codex_cost"][field]; agy_value=cell["agy_cost"][field]
            if cost_bindings_comparable(plan,field) and codex_value is not None and agy_value is not None and codex_value+agy_value>budgets[budget]:
                fail("combined per-cell cost budget exceeded", "cost_budget")
    if cell["arm"]=="codex-only":
        if not aok or any(cell["agy_usage"][k] not in (0,None) for k in TOKEN_FIELDS) or any(v not in (0,None) for v in cell["agy_cost"].values()):
            fail("codex-only requires explicit zero agy telemetry", "telemetry_shape")
    # Missing observations remain explicit unavailable evidence. They are kept in
    # the report and become an advisory hard stop; import never invents zeros.
    return cell

def validate_records(records: Any,plan: dict[str,Any])->list[dict[str,Any]]:
    if not isinstance(records,list) or len(records)!=len(plan["tasks"]):
        fail("records must cover every task", "task_coverage")
    by_task={}
    for record in records:
        if not isinstance(record,dict) or set(record)!={"task_commitment","cells"}: fail("task record has invalid shape")
        task=record["task_commitment"]
        if task not in plan["tasks"] or task in by_task: fail("task record is unknown or duplicate", "task_coverage")
        if not isinstance(record["cells"],list) or len(record["cells"])!=len(ARMS): fail("task record must cover every arm", "arm_coverage")
        by_arm={}
        for item in record["cells"]:
            cell=validate_cell(item,plan)
            if cell["arm"] in by_arm: fail("duplicate arm", "arm_coverage")
            by_arm[cell["arm"]]=cell
        if set(by_arm)!=set(ARMS): fail("task record must cover every arm", "arm_coverage")
        by_task[task]={"task_commitment":task,"cells":[by_arm[a] for a in ARMS]}
    if set(by_task)!=set(plan["tasks"]): fail("records drifted from task plan", "task_coverage")
    return [by_task[t] for t in plan["tasks"]]

def validate_imported(value: Any,plan: dict[str,Any],plan_raw: bytes)->dict[str,Any]:
    keys={"schema_version","kind","plan_sha256","exact_bindings_verified","records"}
    if not isinstance(value,dict) or set(value)!=keys: fail("import artifact has invalid shape")
    if value["schema_version"]!=1 or value["kind"]!="agy-swebench-workflow-study-import" or value["exact_bindings_verified"] is not True or value["plan_sha256"]!=sha(plan_raw): fail("import artifact is not exactly plan-bound")
    value["records"]=validate_records(value["records"],plan)
    return value

def validate_report(value: Any,plan: dict[str,Any],plan_raw: bytes,imported: dict[str,Any],imported_raw: bytes)->dict[str,Any]:
    try: validate_schema(value,load_schema(REPORT_SCHEMA))
    except ValidationFailure: fail("report does not match the closed schema")
    if value["plan_sha256"]!=sha(plan_raw) or value["imported_results_sha256"]!=sha(imported_raw) or value["exact_bindings_verified"] is not True: fail("report is not exactly input-bound")
    if value["plan"]!=plan or value["records"]!=imported["records"]: fail("report content drifted from its chain")
    validate_plan(value["plan"]); validate_records(value["records"],plan)
    expected_denominators={"planned_tasks":len(plan["tasks"]),"planned_cells":len(plan["tasks"])*len(ARMS),"accepted_solutions":sum(cell["accepted_solution"] for record in value["records"] for cell in record["cells"])}
    if value["denominators"]!=expected_denominators:
        fail("report denominators drifted from the complete records", "report_derivation")
    return value

def chain(root_fd:int,stage:str)->tuple[Any,...]:
    expected={"import":("plan.json",),"report":("plan.json","imported_results.json"),"advise":("plan.json","imported_results.json","report.json")}[stage]
    require_stage(root_fd,expected)
    plan,plan_raw=read_artifact(root_fd,"plan.json"); plan=validate_plan(plan)
    imported=imported_raw=report=report_raw=None
    if stage in {"report","advise"}:
        imported,imported_raw=read_artifact(root_fd,"imported_results.json"); imported=validate_imported(imported,plan,plan_raw)
    if stage=="advise":
        report,report_raw=read_artifact(root_fd,"report.json"); report=validate_report(report,plan,plan_raw,imported,imported_raw)
    return plan,plan_raw,imported,imported_raw,report,report_raw

def do_prepare(args: argparse.Namespace)->None:
    _,fd=open_root(args.root)
    try:
        require_stage(fd,())
        plan,_=read_private_json(args.plan,"plan input"); plan=validate_plan(plan,False)
        plan["plan_content_sha256"]=sha(canonical_bytes(plan))
        publish(fd,"plan.json",validate_plan(plan)); print("Prepared study plan")
    finally: os.close(fd)

def parse_records(path:Path)->Any:
    # First accept a canonical JSON array; otherwise consume bounded JSONL.
    raw=read_private_raw(path,"records input")
    try: value=parse_json_bytes(raw,"records input")
    except ValidationFailure: value=None
    if isinstance(value,list): return value
    records=[]
    try:
        for line in raw.splitlines():
            if line.strip(): records.append(parse_json_bytes(line,"records input line"))
    except ValidationFailure: fail("records input is neither JSON array nor unique-key JSONL")
    return records

def do_import(args: argparse.Namespace)->None:
    _,fd=open_root(args.root)
    try:
        plan,plan_raw,*_=chain(fd,"import")
        records=validate_records(parse_records(args.records),plan)
        publish(fd,"imported_results.json",{"schema_version":1,"kind":"agy-swebench-workflow-study-import","plan_sha256":sha(plan_raw),"exact_bindings_verified":True,"records":records}); print("Imported study records")
    finally: os.close(fd)

def do_report(args: argparse.Namespace)->None:
    _,fd=open_root(args.root)
    try:
        plan,plan_raw,imported,imported_raw,_,_=chain(fd,"report")
        records=imported["records"]
        report={"schema_version":1,"kind":"agy-swebench-workflow-study-report","plan_sha256":sha(plan_raw),"imported_results_sha256":sha(imported_raw),"exact_bindings_verified":True,"plan":plan,"records":records,"denominators":{"planned_tasks":len(plan["tasks"]),"planned_cells":len(plan["tasks"])*len(ARMS),"accepted_solutions":sum(cell["accepted_solution"] for record in records for cell in record["cells"])}}
        validate_report(report,plan,plan_raw,imported,imported_raw); publish(fd,"report.json",report); print("Generated study report")
    finally: os.close(fd)

def total_usage(plan:dict[str,Any],cell:dict[str,Any])->int|None:
    if not token_bindings_comparable(plan):
        return None
    codex,cok=usage(cell["codex_usage"],"Codex usage"); agy,aok=usage(cell["agy_usage"],"agy usage")
    return int(codex or 0)+int(agy or 0) if cok and aok else None

def selected_cost_basis(plan:dict[str,Any],records:list[dict[str,Any]])->str|None:
    """Choose one like-for-like basis for every planned cell, or none."""
    for basis in ("observed_billed","version_bound_list_price"):
        if not cost_bindings_comparable(plan,basis):
            continue
        complete=True
        for record in records:
            for cell in record["cells"]:
                if cell["codex_cost"][basis] is None:
                    complete=False
                if cell["arm"]!="codex-only" and cell["agy_cost"][basis] is None:
                    complete=False
        if complete:
            return basis
    return None

def comparable_cost(plan:dict[str,Any],base:dict[str,Any],candidate:dict[str,Any],basis:str)->tuple[float,float]|None:
    # The basis is selected once across every cell; billed and modeled values
    # can therefore never be mixed within an advisory.
    if not cost_bindings_comparable(plan,basis):
        return None
    return float(base["codex_cost"][basis]),float(candidate["codex_cost"][basis]+candidate["agy_cost"][basis])

def complete_primary_telemetry(records:list[dict[str,Any]])->bool:
    for record in records:
        for cell in record["cells"]:
            _,codex_ok=usage(cell["codex_usage"],"Codex usage")
            _,agy_ok=usage(cell["agy_usage"],"agy usage")
            if not codex_ok or (cell["arm"]!="codex-only" and not agy_ok):
                return False
    return True

def do_advise(args: argparse.Namespace)->None:
    _,fd=open_root(args.root)
    try:
        plan,plan_raw,imported,imported_raw,report,report_raw=chain(fd,"advise")
        records=report["records"]; accepted=sum(cell["accepted_solution"] for record in records for cell in record["cells"])
        every_cell=[cell for record in records for cell in record["cells"]]
        hard_stop=any(
            cell["failure_class"]!="none"
            or any(cell[field] is not True for field in MANDATORY_ACCEPTANCE_FIELDS)
            for cell in every_cell
        )
        bindings_token_comparable=token_bindings_comparable(plan)
        bindings_cost_comparable=cost_bindings_comparable(plan,"observed_billed") or cost_bindings_comparable(plan,"version_bound_list_price")
        telemetry_complete=complete_primary_telemetry(records)
        cost_basis=selected_cost_basis(plan,records)
        dominant=[]
        if len(records)>=3 and accepted and not hard_stop and bindings_token_comparable and bindings_cost_comparable and telemetry_complete and cost_basis is not None:
            for arm in ARMS[1:]:
                valid=True; token_improved=False; cost_improved=False
                base_tokens=0; candidate_tokens=0
                base_cost=0.0; candidate_cost=0.0
                for record in records:
                    cells={cell["arm"]:cell for cell in record["cells"]}; base= cells[ARMS[0]]; candidate=cells[arm]
                    if not base["accepted_solution"] or not candidate["accepted_solution"]: valid=False; break
                    bt=total_usage(plan,base); ct=total_usage(plan,candidate); costs=comparable_cost(plan,base,candidate,cost_basis)
                    if bt is None or ct is None or costs is None: valid=False; break
                    # Guardrails: non-regression across all four dimensions
                    if ct>bt: valid=False; break
                    if candidate["repair_count"]>base["repair_count"]: valid=False; break
                    if candidate["wall_time_seconds"]>base["wall_time_seconds"]: valid=False; break
                    if costs[1]>costs[0]: valid=False; break
                    if ct<bt: token_improved=True
                    if costs[1]<costs[0]: cost_improved=True
                    base_tokens+=bt; candidate_tokens+=ct
                    base_cost+=costs[0]; candidate_cost+=costs[1]
                # Qualification: candidate must strictly improve on comparable tokens or cost.
                # Repair count and wall time are guardrails only.
                if valid and (token_improved or cost_improved):
                    token_eff=(base_tokens-candidate_tokens)/base_tokens if base_tokens>0 else 0.0
                    cost_eff=(base_cost-candidate_cost)/base_cost if base_cost>0 else 0.0
                    dominant.append((arm,token_eff,cost_eff))
        recommendation="no_recommendation"; token_efficiency=None; cost_efficiency=None; advisory_cost_basis=cost_basis
        if len(records)<3: reason="calibration-only"
        elif accepted==0: reason="zero-accepted-solutions"
        elif hard_stop: reason="hard-stop"
        elif not bindings_token_comparable: reason="incomparable-token"
        elif not bindings_cost_comparable: reason="incomparable-cost"
        elif not telemetry_complete: reason="incomplete-telemetry"
        elif cost_basis is None: reason="incomparable-cost"
        elif len(dominant)==1:
            recommendation,token_efficiency,cost_efficiency=dominant[0]
            reason="pareto-dominant"
        elif len(dominant)>1: reason="multiple-dominant"
        else: reason="no-dominant-arm"
        advisory={
            "schema_version":1,
            "kind":"agy-swebench-workflow-study-advisory",
            "plan_sha256":sha(plan_raw),
            "imported_results_sha256":sha(imported_raw),
            "report_sha256":sha(report_raw),
            "exact_bindings_verified":True,
            "recommendation_only":True,
            "applied":False,
            "dispatch_authorized":False,
            "model_change_authorized":False,
            "effort_change_authorized":False,
            "recommendation":recommendation,
            "reason_code":reason,
            "directional_total_reported_token_efficiency":token_efficiency,
            "directional_total_reported_cost_efficiency":cost_efficiency,
            "selected_cost_basis":advisory_cost_basis,
            "token_bindings_comparable":bindings_token_comparable,
            "cost_bindings_comparable":bindings_cost_comparable,
            "denominators":{"planned_tasks":len(records),"planned_cells":len(records)*len(ARMS),"accepted_solutions":accepted}
        }
        try: validate_schema(advisory,load_schema(ADVISORY_SCHEMA))
        except ValidationFailure: fail("advisory does not match the closed schema")
        publish(fd,"advisory.json",advisory); print("Generated study advisory")
    finally: os.close(fd)

def main()->None:
    parser=argparse.ArgumentParser(description="offline SWE-bench workflow study"); commands=parser.add_subparsers(dest="command",required=True)
    prepare=commands.add_parser("prepare"); prepare.add_argument("--root",type=Path,required=True); prepare.add_argument("--plan",type=Path,required=True); prepare.set_defaults(func=do_prepare)
    imp=commands.add_parser("import"); imp.add_argument("--root",type=Path,required=True); imp.add_argument("--records",type=Path,required=True); imp.set_defaults(func=do_import)
    report=commands.add_parser("report"); report.add_argument("--root",type=Path,required=True); report.set_defaults(func=do_report)
    advise=commands.add_parser("advise"); advise.add_argument("--root",type=Path,required=True); advise.set_defaults(func=do_advise)
    args=parser.parse_args(); args.func(args)

if __name__=="__main__": main()
