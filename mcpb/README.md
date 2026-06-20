# calibremcp (MCPB Bundle)

SOTA April 2026 industrialized FastMCP 3.2.0 server for conversational Calibre e-book library management with sampling, agentic workflows, skills, prompts, and LanceDB metadata RAG

## Usage

Add to \claude_desktop_config.json\:
\\\json
{
  "mcpServers": {
    "calibremcp": {
      "command": "uv",
      "args": ["run", "--directory", "\D:\Dev\repos", "python", "-m", "calibremcp"],
      "env": { "PYTHONPATH": "\D:\Dev\repos/src" }
    }
  }
}
\\\

## Tools

- **test_tool**: test_tool
- **health**: health
- **metrics**: Prometheus metrics for unified monitoring stack (includes mcp_tool_* when instrumented).
- **get_transport_config_stdio**: get_transport_config(stdio)
- **get_transport_config_http**: get_transport_config(http)
- **get_transport_config_sse**: get_transport_config(sse)
- **get_page**: get_page
- **update_viewer_settings**: update_viewer_settings
- **health_check**: Health check endpoint.
- **agentic_library_workflow**: agentic_library_workflow
- **agentic_calibre_workflow**: agentic_calibre_workflow
- **intelligent_library_processing**: intelligent_library_processing
- **conversational_calibre_assistant**: conversational_calibre_assistant
- **wrapper**: wrapper
- **_format_books_table**: _format_books_table
- **search_books_helper**: search_books_helper
- **get_books_by_series_helper**: get_books_by_series_helper
- **get_books_by_author_helper**: get_books_by_author_helper
- **Name**: Name
- **__init__**: Initialize compatibility shim.
- **list_tags**: list_tags
- **get_tag**: get_tag
- **create_tag**: create_tag
- **update_tag**: update_tag
- **delete_tag**: delete_tag
- **find_duplicate_tags**: find_duplicate_tags
- **merge_tags**: merge_tags
- **get_unused_tags**: get_unused_tags
- **delete_unused_tags**: delete_unused_tags
- **get_simple_tag_statistics**: get_simple_tag_statistics
- **mystery**: mystery
- **Locked Room Mystery**: Locked Room Mystery
- **sci-fi**: sci-fi
- **scifi**: scifi
- **old tag**: old tag
- **fiction**: fiction
- **test_database_concurrency**: test_database_concurrency
- **manage_bulk_operations**: manage_bulk_operations
- **manage_content_sync**: manage_content_sync
- **manage_smart_collections**: manage_smart_collections
- **manage_ai_operations**: manage_ai_operations
- **get_tag_statistics_helper**: get_tag_statistics_helper
- **analyze_library**: analyze_library
- **get_tag_statistics**: get_tag_statistics
- **find_duplicate_books**: find_duplicate_books
- **get_series_analysis**: get_series_analysis
- **analyze_library_health**: analyze_library_health
- **unread_priority_list**: unread_priority_list
- **reading_statistics**: reading_statistics
- **manage_analysis**: manage_analysis
- **manage_authors**: manage_authors
- **search_fulltext**: search_fulltext
- **get_book_helper**: get_book_helper
- **manage_books**: manage_books
- **query_books**: query_books
- **manage_comments**: manage_comments
- **list_books_helper**: list_books_helper
- **manage_descriptions**: manage_descriptions
- **manage_extended_metadata**: manage_extended_metadata
- **convert_book_format_helper**: convert_book_format_helper
- **download_book_helper**: download_book_helper
- **bulk_format_operations_helper**: bulk_format_operations_helper
- **manage_files**: manage_files
- **help_tool**: help_tool
- **export_books**: export_books
- **manage_import**: manage_import
- **library_discovery**: library_discovery
- **list_libraries_helper**: list_libraries_helper
- **switch_library_helper**: switch_library_helper
- **get_library_stats_helper**: get_library_stats_helper
- **cross_library_search_helper**: cross_library_search_helper
- **manage_libraries**: manage_libraries
- **manage_library_operations**: manage_library_operations
- **manage_metadata**: manage_metadata
- **update_book_metadata_helper**: update_book_metadata_helper
- **auto_organize_tags_helper**: auto_organize_tags_helper
- **fix_metadata_issues_helper**: fix_metadata_issues_helper
- **_error_auto**: _error(auto)
- **_error_finereader**: _error(finereader)
- **_error_got_ocr**: _error(got-ocr)
- **manage_organization**: manage_organization
- **media_research_book**: media_research_book
- **media_synopsis**: media_synopsis
- **media_critical_reception**: media_critical_reception
- **media_deep_research**: media_deep_research
- **calibre_rag**: calibre_rag
- **show_book_prefab_card**: show_book_prefab_card
- **show_libraries_prefab_card**: show_libraries_prefab_card
- **manage_publishers**: manage_publishers
- **rag_index_build**: rag_index_build
- **rag_retrieve**: rag_retrieve
- **calibre_metadata_index_build**: calibre_metadata_index_build
- **calibre_metadata_search**: calibre_metadata_search
- **calibre_metadata_export_json**: calibre_metadata_export_json
- **manage_series**: manage_series
- **japanese_book_organizer_helper**: japanese_book_organizer_helper
- **show_api_docs**: show_api_docs
- **manage_system**: manage_system
- **manage_tags**: manage_tags
- **manage_times**: manage_times
- **manage_user_comments**: manage_user_comments
- **_load_or_create_secret**: _load_or_create_secret
- **manage_users**: manage_users
- **manage_viewer**: manage_viewer

## Requirements

- Python 3.12+
- uv
