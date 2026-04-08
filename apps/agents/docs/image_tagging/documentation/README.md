# documentation

Exhaustive reference for the Image Analysis Agent: architecture, agent state and data models, taxonomy, configuration, every graph node, prompts, database, API, frontend, Docker, and development phases.

## Contents


| File                                                                   | Description                                                                  |
| ---------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| [01-project-overview.md](01-project-overview.md)                       | Project summary, features, tech stack, repo tree, doc index.                 |
| [02-architecture.md](02-architecture.md)                               | System diagram, request lifecycles (single, bulk, search), component map.    |
| [03-langgraph-pipeline.md](03-langgraph-pipeline.md)                   | Agent graph Mermaid, graph_builder walkthrough, Send API, state merge.       |
| [04-agent-state.md](04-agent-state.md)                                 | ImageTaggingState fields, reducer (partial_tags), lifecycle table, examples. |
| [05-agent-data-models.md](05-agent-data-models.md)                     | Pydantic models (TagResult, ValidatedTag, FlaggedTag, TagRecord, etc.).      |
| [06-taxonomy-complete-reference.md](06-taxonomy-complete-reference.md) | Every allowed value per category; get_flat_values, get_parent_for_child.     |
| [07-configuration-and-settings.md](07-configuration-and-settings.md)   | settings.py (env), configuration.py (thresholds, overrides).                 |
| [08-node-preprocessor.md](08-node-preprocessor.md)                     | image_preprocessor: steps, constants, errors.                                |
| [09-node-vision-analyzer.md](09-node-vision-analyzer.md)               | vision_analyzer: messages, retry, parse, vision JSON shape.                  |
| [10-node-taggers-overview.md](10-node-taggers-overview.md)             | run_tagger flow, ALL_TAGGERS, reducer, filtering, capping.                   |
| [11-node-taggers-per-category.md](11-node-taggers-per-category.md)     | All 8 taggers: instructions, max_tags, examples.                             |
| [12-node-validator.md](12-node-validator.md)                           | validate_tags: gate, flat/hierarchical validation, _validate_value.          |
| [13-node-confidence-filter.md](13-node-confidence-filter.md)           | filter_by_confidence: thresholds, overrides, needs_review.                   |
| [14-node-aggregator.md](14-node-aggregator.md)                         | aggregate_tags: helpers, TagRecord build, processing_status.                 |
| [15-prompts.md](15-prompts.md)                                         | VISION_ANALYZER_PROMPT and build_tagger_prompt; examples; tuning.            |
| [16-database.md](16-database.md)                                       | migration.sql, SupabaseClient, build_search_index, search/filters.           |
| [17-api-reference.md](17-api-reference.md)                             | Every endpoint: method, path, params, body, response, errors.                |
| [18-frontend.md](18-frontend.md)                                       | Pages, layout, components, data flow, TypeScript types.                      |
| [19-docker-and-deployment.md](19-docker-and-deployment.md)             | Dockerfiles, docker-compose, build/run, production API URL.                  |
| [20-development-phases.md](20-development-phases.md)                   | Phases 0–6 summary, key files, verification, changelog/progress.             |


