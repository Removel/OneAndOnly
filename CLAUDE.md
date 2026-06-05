# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

"One and Only" is an AI companion. The repo is a polyrepo-style monorepo with **four roughly co-equal modules** that share databases and APIs but are otherwise independent:

- `agent/` — LangGraph-based agent pipeline (the "心智层" / cognition layer). Exposes `chat_with_agent(...)` from `agent/main.py`.
- `backend/` — FastAPI HTTP service. Wraps the agent and persists session metadata. Strict layered architecture (see "Backend rules" below).
- `custom_model/` — Local PyTorch/Transformers models. `styler/` is a T5 + LoRA text-stylizer; `aura/` is a (planned) VAC-emotion → Live2D-action model.
- `unity/` and `frontend/` — Two parallel clients (Unity desktop runtime and Vue 3 web). Both consume the same `backend/` HTTP API; they are siblings, not alternatives. `frontend/` is currently empty (designed in `.harness/doc/Web前端设计书.md`, not yet scaffolded).

The repo's own docs in `.harness/doc/` are authoritative and mostly in Chinese — read them before making non-trivial changes:
- `项目结构.md` — directory map
- `状态、节点与边设计.md` — agent graph design (state, nodes, edges, retry policy)
- `后端启动说明.md` / `后端测试文件使用说明.md` — backend run/test guides
- `人物记忆向量数据库 Chroma 分类体系.md` — memory taxonomy (vector DB vs MD doc split)
- `Web前端设计书.md` — Vue 3 frontend spec
- `.harness/rules/backend_coding_rules.md` — **mandatory** backend layering rules

## Common commands

All commands run from the repo root. Python 3.13 + the deps in `requirements.txt`.

```bash
# Install deps
pip install -r requirements.txt

# Run backend (auto-initializes SQLite DBs in database/backend/ and database/agent/)
python -m backend.main
# or
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Backend integration tests (interactive menu — DB tests, API tests, or both;
# auto-starts the server for API tests)
python test_scripts/backend_test/test_main.py

# Single test file
python test_scripts/backend_test/test_database.py
python test_scripts/backend_test/test_api.py            # requires backend running on :8000
pytest test_scripts/backend_test/test_session_repository.py -v

# Agent node tests (each node has its own driver script)
python test_scripts/agent_test/test_agent.py
python test_scripts/agent_test/test_plan_execute.py     # also: test_evaluate, test_memory_retrieve, test_styled_output

# Styler model standalone demo
python -m custom_model.styler.service
```

There is no project-wide lint/format config; match the surrounding file's style.

## Configuration

- **Agent API keys**: `agent/.env` (template at `agent/.env.example`). `OPENAI_API_KEY` is used by all four LLM roles by default. Loaded via `dotenv` in `agent/util/config_loader.py`.
- **Per-agent LLM config**: `agent/config/{plan_execute,memory_manager,evaluator,summarizer}.yaml`. Each YAML names a `model_name`, `temperature`, `base_url`, and `api_key_env` (the env var name to read). To use a different key per role, add another env var and point `api_key_env` at it.
- **Backend DB path**: `DATABASE_URL` env var overrides; defaults to `sqlite:///database/backend/conversation.db`.

## Backend architecture and rules

`backend/` follows a strict three-layer split that is **enforced by hand-review**, not by tooling. The rules live in `.harness/rules/backend_coding_rules.md` — read before editing. Highlights:

- **Repository layer** (`backend/repository/`): only DB I/O. Returns abstract entities (POJOs) or primitives — never `dict`/`Result`/`Response`. Mutating ops (create/update/delete) are void-returning; on failure they raise `DatabaseException`. Empty vs. not-found states are kept distinct.
- **Service layer** (`backend/service/`): all business logic, all parameter validation. Accepts entities or primitives, returns entities or primitives. Raises domain exceptions (`ParamValidationException`, `NotFoundException`, `ChatException`, …) defined in `backend/exception/Exceptions.py`. **No `try/except` unless there is a real compensation step** — let exceptions propagate to the global handler.
- **Router layer** (`backend/router/`): protocol translation only. Unpacks `Request` DTOs, calls the service, wraps results in `Result[T]` (`backend/entity/Result.py`). No business logic, no validation, **no `try/except`**.
- **Global exception handler** (`backend/exception/GlobalExceptionHandler.py`): every `BaseBusinessException` becomes a `Result.error(msg, code)` JSON response with the exception's HTTP code. Registered in `backend/main.py`.

When adding a new endpoint: write Repository → Service → Router in that order, define request/response DTOs under `backend/entity/{request,response}/`, and let exceptions flow up untouched.

## Agent architecture (LangGraph)

Pipeline (see `.harness/doc/状态、节点与边设计.md` for the canonical version):

```
START → memory_retrieve → styled_output → (need_continue?) → plan_execute → (need_evaluate?) → evaluate → (pass | retry<3) → plan_execute (loop)
                                        ↘ END ←──────────────┘                 ↘ styled_output → END ←────────────────┘
```

- **Shared state** is `GlobalState` (TypedDict in `agent/graph/state.py`): `messages`, `user_input`, `response_text`, `plan`, `memory`, `emotion_vac`, `need_evaluate`, `need_continue`, `retry_times`, `error_message`. `messages` uses LangGraph's `add_messages` reducer.
- **Four LLM roles**, each with its own YAML in `agent/config/`: `memory_manager` (vector-DB tools), `plan_execute` (intent+reply+evaluate-decision), `evaluator` (quality check, drives the retry loop, max 3 retries), `summarizer` (gate routing + final styling + VAC emotion + async memory write).
- **Auto-discovery in `agent/util/build_and_compile_graph.py`**:
  - Nodes: every `.py` in `agent/graph/node/` whose function signature is `(state: GlobalState) -> Dict[str, Any]` is registered. Function name `foo_node` becomes node `foo`; otherwise the function name is the node name.
  - Conditional edges: every function in `agent/graph/edge/` named `route_after_<node>` with signature `(state: GlobalState) -> str` is wired as a conditional edge from `<node>`.
  - The fixed edges (`memory_retrieve → styled_output`), entry point, and the literal mappings for conditional edges are hard-coded in `build_graph()`. **If you add a new node or edge target, update `build_graph()` too** — auto-discovery doesn't infer the routing dictionaries.
  - `styled_output`'s conditional edge maps `"__end__"` to `END` (LangGraph sentinel) for the termination path.
- **Tool discovery** (`agent/util/find_tools.py`): scans `agent/tools/tools_for_memory_manager/` and `agent/tools/tools_for_plan_executor/` for any module attribute that quacks like a LangChain tool (has `name`, `description`, `invoke`). The `plan_executor` tools dir is currently empty.
- **Persistence**: LangGraph checkpoints go to `database/agent/checkpoints.db` (SQLite, via `SqliteSaver`). The `ChatManager` singleton in `agent/main.py` builds and caches the compiled graph + checkpointer. `clear_history(thread_id)` deletes the LangGraph thread.
- **Long-term memory**: Chroma vector DB at `database/agent/vector_memory.db/`, plus a Markdown file (`user_info.md`) for static profile data. Split rationale documented in `.harness/doc/人物记忆向量数据库 Chroma 分类体系.md`.

`session_id` flows: `backend/router/ChatRouter` → `backend/service/ChatService` (looks up the SQLite session row) → `agent/main.chat_with_agent` (passes `str(session_id)` as the LangGraph `thread_id`). The agent thread and the backend session are linked by this id.

## Custom models

- `custom_model/styler/service.py` — `stylize(raw_text)` is the public entry point. Lazy-loads a T5 base model (`uer-t5-base-chinese-cluecorpussmall` by default) and applies a LoRA adapter from `styled_models/my_t5_style_model/checkpoint-*`. Uses `BertTokenizer` (the upstream T5 was trained with one), sets `[SEP]` as EOS when missing, and runs beam search with `no_repeat_ngram_size=3`. Picks `cuda` automatically if available.
- `custom_model/styler/train.py`, `download.py` — adapter training and base-model download.
- `custom_model/aura/` — emotion model, currently a stub.

## Things that will trip you up

- **`agent/graph/state.py` ends with `class GlobalStafrom: pass`** — a leftover stub. Don't "fix" it unless you confirm nothing imports it; the working class is `GlobalState`.
- **No top-level `main.py`**: the backend entry point is `backend/main.py` (run as `python -m backend.main`). The `python main.py` line in `.harness/doc/后端启动说明.md` predates a refactor.
- **Backend `service` calls into `agent/main.py` directly** — they're not isolated by an interface. Importing `backend.service.ChatService` will eagerly load the agent module and its `.env`.
- **Default to absolute imports rooted at the repo (`agent.util...`, `backend.repository...`)**. `find_tools.py` and `build_and_compile_graph.py` mutate `sys.path` to make this work when scripts are run directly.
- The repo uses Chinese for log messages, docstrings, exception `msg`, and most docs. Match this when editing existing files; new internal-only modules can be English.
