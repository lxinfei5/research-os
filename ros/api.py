"""The single cross-module import surface for ResearchOS.

ACL (ported from AStockOS): higher layers (cli, runners, future search/condense/report modules)
import from `ros.api`, never reach into ros.storage.* internals directly. This keeps the storage
layer's contract in one place.
"""
from __future__ import annotations

from . import library, paths, topics
from .search import capabilities
from .storage import intake, knowledge, method

# storage / knowledge.db
get_conn = knowledge.get_conn
init_db = knowledge.init_db
restore_from_snapshot = knowledge.restore_from_snapshot
ensure_knowledge_db = knowledge.ensure_knowledge_db
apply_migrations = knowledge.apply_migrations
current_schema_version = knowledge.current_schema_version
db_user_version = knowledge.db_user_version
gen_id = knowledge.gen_id
content_sha256 = knowledge.content_sha256

record_credibility = knowledge.record_credibility
add_source_ref = knowledge.add_source_ref
record_context_snapshot = knowledge.record_context_snapshot
record_audit_change = knowledge.record_audit_change

upsert_l3_claim = knowledge.upsert_l3_claim
upsert_l2_finding = knowledge.upsert_l2_finding
upsert_l1_viewpoint = knowledge.upsert_l1_viewpoint
upsert_l0_worldview = knowledge.upsert_l0_worldview
upsert_facet = knowledge.upsert_facet
record_search = knowledge.record_search
recent_searches = knowledge.recent_searches

coverage = knowledge.coverage
knowledge_snapshot = knowledge.knowledge_snapshot
l0_history = knowledge.l0_history

# intake / sources.db
init_store = intake.init_store
record_capture = intake.record_capture
list_items = intake.list_items
promote_item = intake.promote_item
bulk_promote = intake.bulk_promote
link_source = intake.link_source
dump_store = intake.dump_store

# library
record_source = library.record_source
read_source = library.read_source
list_sources = library.list_sources
shared_sources = library.shared_sources

# method lane (M0/M1)
method_upsert = method.upsert
method_list = method.list_rules
method_export = method.export_to_shared
method_import = method.import_from_shared
method_list_shared = method.list_shared

# search policy gate
validate_collector = capabilities.validate_collector
source_policy = capabilities.source_policy
known_sources = capabilities.known_sources
search_entry = capabilities.search_entry

__all__ = [n for n in dir() if not n.startswith("_")]
