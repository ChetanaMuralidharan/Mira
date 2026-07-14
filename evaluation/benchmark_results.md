# MIRA Phase 4 Benchmark Results

Overall accuracy: 24/25 = 96.00%
SQL accuracy: 14/15 = 93.33%
RAG accuracy: 10/10 = 100.00%

| ID | Type | Score | Intent | Validation | Retries | Latency ms | Reason |
|---|---|---:|---|---|---:|---:|---|
| sql_001 | sql | 1 | data_query | valid | 0 | 5989 | expected=5760, actual=5760 |
| sql_002 | sql | 1 | data_query | valid | 0 | 1905 | expected=811, actual=811 |
| sql_003 | sql | 1 | data_query | valid | 0 | 2044 | expected=50.97, actual=51.0, diff=0.030000000000001137 |
| sql_004 | sql | 1 | data_query | valid | 0 | 2890 | expected=ambulatory, actual=ambulatory, expected_norm=ambulatory, actual_norm=ambulatory |
| sql_005 | sql | 1 | data_query | valid | 0 | 2063 | expected=641, actual=641 |
| sql_006 | sql | 1 | data_query | valid | 0 | 2005 | expected=1261, actual=1261 |
| sql_007 | sql | 1 | data_query | valid | 0 | 2086 | expected=96, actual=96 |
| sql_008 | sql | 1 | data_query | valid | 0 | 1771 | expected=172, actual=172 |
| sql_009 | sql | 1 | data_query | valid | 0 | 2014 | expected=41.97, actual=41.97, diff=0.0 |
| sql_010 | sql | 1 | data_query | valid | 0 | 2894 | expected=3.51, actual=3.5, diff=0.009999999999999787 |
| sql_011 | sql | 0 | data_query | valid | 0 | 2835 | expected=2021-04-01 00:00:00, actual=1617235200, expected_norm=2021-04-01, actual_norm=2021-03-31 |
| sql_012 | sql | 1 | data_query | valid | 0 | 1998 | expected=106.76, actual=106.76, diff=0.0 |
| sql_013 | sql | 1 | data_query | valid | 0 | 1672 | expected=14911, actual=14911 |
| sql_014 | sql | 1 | data_query | valid | 0 | 2080 | expected=4.62, actual=4.62, diff=0.0 |
| sql_015 | sql | 1 | data_query | suspect | 3 | 27986 | top_item_hits=['medication review due (situation)', 'full-time employment (finding)', 'body mass index 30+ - obesity (finding)', 'received higher education (finding)', 'stress (finding)'], required=2 |
| rag_001 | rag | 1 | document_query | not_applicable | 0 | 9587 | keyword_hits=['readmission'], required=1 |
| rag_002 | rag | 1 | document_query | not_applicable | 0 | 11778 | keyword_hits=['abnormal', 'lab', 'escalation'], required=2 |
| rag_003 | rag | 1 | document_query | not_applicable | 0 | 10717 | keyword_hits=['medication', 'reconciliation', 'discharge'], required=2 |
| rag_004 | rag | 1 | document_query | not_applicable | 0 | 11642 | keyword_hits=['infection', 'hand hygiene', 'isolation', 'precautions'], required=2 |
| rag_005 | rag | 1 | document_query | not_applicable | 0 | 15312 | keyword_hits=['discharge', 'checklist'], required=2 |
| rag_006 | rag | 1 | document_query | not_applicable | 0 | 10118 | keyword_hits=['sepsis', 'warning', 'screening', 'escalation'], required=2 |
| rag_007 | rag | 1 | document_query | not_applicable | 0 | 12601 | keyword_hits=['fall', 'risk', 'prevention', 'assessment'], required=2 |
| rag_008 | rag | 1 | document_query | not_applicable | 0 | 5928 | keyword_hits=['monitoring', 'diabetes', 'hypoglycemia'], required=2 |
| rag_009 | rag | 1 | document_query | not_applicable | 0 | 14480 | keyword_hits=['pain', 'assessment', 'management', 'reassessment'], required=2 |
| rag_010 | rag | 1 | document_query | not_applicable | 0 | 16056 | keyword_hits=['DNR', 'documentation', 'patient'], required=2 |