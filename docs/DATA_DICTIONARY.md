# Data dictionary

Central index of every data file's schema. Individual `README.md` files under `data/*/` are the
authoritative per-directory docs; this file is a single-page cross-reference.

## `data/submission_ids/qN_*.csv`
`submission_id,label` — `label` in `{correct, wrong}`. See `data/submission_ids/README.md`.

## `data/splits/{q4_sortbykey,q5_topk}/split_manifest.json`
Experiment metadata: taxonomy/detector version, seed, split method, reported result. See
`data/splits/README.md`.

## `data/splits/{q4_sortbykey,q5_topk}/split_{00..09}_{train,test}_ids.txt`
One `submission_id` per line.

## `data/labels_scores/q{N}_{taxonomy_version}_{detector_version}_{scoping_mode}.csv`
`submission_id,test_suite_label,target_competency,coverage_score,structure_score,final_score,matched_branch,notes`.
See `data/labels_scores/README.md`.

## `data/exemplar_registry/exemplars.csv`
`exemplar_id,competency,source,source_submission_id,final_score,verified_taxonomy_version,verified_detector_version,code_path`.
See `data/exemplar_registry/README.md`.

## `data/exemplar_registry/similarities_{lexical,codet5p}.csv`
`exemplar_id,compared_against_id,relation,similarity` — `relation` in `{SAME, CROSS, UNRELATED}`.
Documented inline in `scripts/regenerate_table5.py`.

## `configs/stage_manifest.yaml`
The audit index. See its own header comment and `VERSIONING.md`.

## `configs/table4_config.yaml`, `configs/table5_config.yaml`
Which `stage_manifest.yaml` entries each table script consumes, and in what row/column order they're
rendered.
