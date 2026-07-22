# MIRA Phase 4 Benchmark Results

Overall accuracy: 48/50 = 96.00%
SQL accuracy: 25/25 = 100.00%
RAG accuracy: 15/15 = 100.00%
Hybrid accuracy: 7/7 = 100.00%
Visualization accuracy: 1/3 = 33.33%

| ID | Type | Score | Intent | Validation | Retries | Latency ms | Chart | Reason |
|---|---|---:|---|---|---:|---:|---|---|
| sql_001 | sql | 1 | data_query | valid | 0 | 5578 | metric_card | expected=5760, actual=5760 |
| sql_002 | sql | 1 | data_query | valid | 0 | 1986 | metric_card | expected=50.97, actual=51.0, diff=0.030000000000001137 |
| sql_003 | sql | 1 | data_query | valid | 0 | 1877 | metric_card | expected=41.97, actual=41.97, diff=0.0 |
| sql_004 | sql | 1 | data_query | valid | 0 | 4125 | bar | expected=18-44, actual=18-44, expected_norm=18-44, actual_norm=18-44 |
| sql_005 | sql | 1 | data_query | valid | 0 | 2790 | bar | expected=white, actual=white, expected_norm=white, actual_norm=white |
| sql_006 | sql | 1 | data_query | valid | 0 | 2009 | metric_card | expected=811, actual=811 |
| sql_007 | sql | 1 | data_query | valid | 0 | 2065 | metric_card | expected=1261, actual=1261 |
| sql_008 | sql | 1 | data_query | valid | 0 | 1709 | metric_card | expected=551, actual=551 |
| sql_009 | sql | 1 | data_query | valid | 0 | 9224 | metric_card | expected=96, actual=96 |
| sql_010 | sql | 1 | data_query | valid | 0 | 9103 | metric_card | expected=172, actual=172 |
| sql_011 | sql | 1 | data_query | valid | 0 | 9285 | metric_card | expected=641, actual=641 |
| sql_012 | sql | 1 | data_query | valid | 0 | 8923 | metric_card | expected=2, actual=2 |
| sql_013 | sql | 1 | data_query | valid | 0 | 8767 | bar | expected=ambulatory, actual=ambulatory, expected_norm=ambulatory, actual_norm=ambulatory |
| sql_014 | sql | 1 | data_query | valid | 0 | 8680 | line | expected=2021-04-01 00:00:00, actual=1617235200, expected_norm=2021-04-01, actual_norm=2021-04-01 |
| sql_015 | sql | 1 | data_query | valid | 0 | 7635 | metric_card | expected=106.76, actual=106.7579772921, diff=0.0020227079000108006 |
| sql_016 | sql | 1 | data_query | valid | 0 | 8347 | metric_card | expected=11722, actual=11722 |
| sql_017 | sql | 1 | data_query | valid | 0 | 7050 | metric_card | expected=3541.6, actual=3541.5987374168, diff=0.0012625832000594528 |
| sql_018 | sql | 1 | data_query | valid | 0 | 8845 | metric_card | expected=14911, actual=14911 |
| sql_019 | sql | 1 | data_query | valid | 0 | 9807 | bar | expected=antihypertensive, actual=antihypertensive, expected_norm=antihypertensive, actual_norm=antihypertensive |
| sql_020 | sql | 1 | data_query | valid | 0 | 10073 | bar | top_item_hits=['1 ml epoetin alfa 4000 unt/ml injection [epogen]', 'lisinopril 10 mg oral tablet', 'insulin isophane human 70 unt/ml / insulin regular human 30 unt/ml injectable suspension [humulin]', 'amlodipine 2.5 mg oral tablet', 'hydrochlorothiazide 25 mg oral tablet'], required=2 |
| sql_021 | sql | 1 | data_query | valid | 0 | 9863 | bar | expected=Body mass index (BMI) [Ratio], actual=Body mass index (BMI) [Ratio], expected_norm=body mass index (bmi) [ratio], actual_norm=body mass index (bmi) [ratio] |
| sql_022 | sql | 1 | data_query | valid | 0 | 8915 | metric_card | expected=178544, actual=178544 |
| sql_023 | sql | 1 | data_query | valid | 0 | 6802 | metric_card | expected=28.75, actual=28.75, diff=0.0 |
| sql_024 | sql | 1 | data_query | valid | 0 | 10055 | metric_card | expected=4.62, actual=4.62, diff=0.0 |
| sql_025 | sql | 1 | data_query | valid | 0 | 15733 | bar | expected=hypertension, actual=Hypertension, expected_norm=hypertension, actual_norm=hypertension |
| rag_001 | rag | 1 | document_query | not_applicable | 0 | 2507 | none | keyword_hits=['A1c', 'monitoring'], required=2 |
| rag_002 | rag | 1 | document_query | not_applicable | 0 | 2405 | none | keyword_hits=['monitoring', 'hypoglycemia'], required=2 |
| rag_003 | rag | 1 | document_query | not_applicable | 0 | 3355 | none | keyword_hits=['heart failure', 'discharge'], required=2 |
| rag_004 | rag | 1 | document_query | not_applicable | 0 | 7905 | none | keyword_hits=['stroke', 'risk', 'hypertension', 'diabetes'], required=2 |
| rag_005 | rag | 1 | document_query | not_applicable | 0 | 5123 | none | keyword_hits=['COPD', 'exacerbation', 'inhaler'], required=2 |
| rag_006 | rag | 1 | document_query | not_applicable | 0 | 2466 | none | keyword_hits=['asthma', 'control', 'symptoms', 'rescue inhaler'], required=2 |
| rag_007 | rag | 1 | document_query | not_applicable | 0 | 9907 | none | keyword_hits=['chronic kidney disease', 'CKD', 'kidney function', 'monitoring'], required=2 |
| rag_008 | rag | 1 | document_query | not_applicable | 0 | 5106 | none | keyword_hits=['medication', 'reconciliation', 'review', 'discharge'], required=2 |
| rag_009 | rag | 1 | document_query | not_applicable | 0 | 13501 | none | keyword_hits=['discharge', 'medication reconciliation'], required=2 |
| rag_010 | rag | 1 | document_query | not_applicable | 0 | 6460 | none | keyword_hits=['diagnosis', 'medication'], required=2 |
| rag_011 | rag | 1 | document_query | not_applicable | 0 | 5925 | none | keyword_hits=['ICU', 'escalation', 'deterioration', 'respiratory'], required=2 |
| rag_012 | rag | 1 | document_query | not_applicable | 0 | 2946 | none | keyword_hits=['abnormal', 'laboratory', 'escalation'], required=2 |
| rag_013 | rag | 1 | document_query | not_applicable | 0 | 5813 | none | keyword_hits=['infection', 'hand hygiene', 'precautions'], required=2 |
| rag_014 | rag | 1 | document_query | not_applicable | 0 | 11628 | none | keyword_hits=['fall', 'risk', 'prevention', 'assessment'], required=2 |
| rag_015 | rag | 1 | document_query | not_applicable | 0 | 10013 | none | keyword_hits=['anticoagulation', 'bleeding', 'monitor'], required=2 |
| hybrid_001 | hybrid | 1 | hybrid | not_applicable | 0 | 15630 | metric_card | SQL: expected=811, actual=811; RAG: keyword_hits=['A1c', 'diabetes', 'monitoring'], required=1 |
| hybrid_002 | hybrid | 1 | hybrid | not_applicable | 0 | 18350 | metric_card | SQL: expected=172, actual=172; RAG: keyword_hits=['heart failure', 'discharge'], required=1 |
| hybrid_003 | hybrid | 1 | hybrid | not_applicable | 0 | 19549 | metric_card | SQL: expected=96, actual=96; RAG: keyword_hits=['COPD', 'exacerbation'], required=1 |
| hybrid_004 | hybrid | 1 | hybrid | not_applicable | 0 | 15916 | metric_card | SQL: expected=551, actual=551; RAG: keyword_hits=['chronic kidney disease', 'CKD', 'monitoring'], required=1 |
| hybrid_005 | hybrid | 1 | hybrid | not_applicable | 0 | 27027 | metric_card | SQL: expected=178544, actual=178544; RAG: keyword_hits=['abnormal', 'laboratory', 'escalation'], required=1 |
| hybrid_006 | hybrid | 1 | hybrid | not_applicable | 0 | 22586 | metric_card | SQL: expected=14911, actual=14911; RAG: keyword_hits=['medication', 'reconciliation', 'review'], required=1 |
| hybrid_007 | hybrid | 1 | hybrid | not_applicable | 0 | 20477 | metric_card | SQL: expected=2, actual=2; RAG: keyword_hits=['hypoglycemia', 'monitoring'], required=1 |
| viz_001 | visualization | 0 | visualization | valid | 0 | 13794 | line | chart_type=line, expected_chart_type=line, has_chart=True, data_match=False, expected_rows=1199, actual_rows=1000 |
| viz_002 | visualization | 1 | data_query | valid | 0 | 13428 | bar | chart_type=bar, expected_chart_type=bar, has_chart=True, data_match=True, expected_rows=4, actual_rows=4 |
| viz_003 | visualization | 0 | data_query | valid | 0 | 13773 | line | chart_type=line, expected_chart_type=bar, has_chart=True, data_match=False, expected_rows=8, actual_rows=8 |