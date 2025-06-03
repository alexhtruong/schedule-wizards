
# CSC 365 Performance Writeup

### Explanation on million rows:

We knew we wanted some departments, and we wanted about 20-30 courses per department. We wanted to have at least 1-2 professors for all of our courses. 
Then we wanted the largest emphasis on the reviews. 

Our generation for the data can be found here:
https://github.com/alexhtruong/schedule-wizards/blob/main/scripts/generate_fake_data.py


### Courses Endpoints:

GET /courses/

POST /courses/

GET /courses/{course_code}

GET /courses/{course_code}/professors 

GET /courses/{course_code}/statistics

### Professors Endpoints:
GET /professors/{professor_id}

POST /professors/

POST /professors/{professor_id}/courses

GET /professors/search/by-tags

### Reviews Endpoints:
POST /reviews/

GET reviews/course/{course_code}

GET /reviews/professor/{professor_name}

### Departments Endpoints:
POST /departments/

GET /departments/

GET /departments/{department_abbrev}/statistics

### Stats Endpoints:
POST /stats/refresh


### Three Slowest Endpoints:

GET /departments/{department_abbrev}/statistics
POST /stats/refresh
GET /professors/search/by-tags

Since GET /departments/{department_abbrev}/statistics was the slowest, here is the explain analyze:

### First Query in Endpoint:

EXPLAIN ANALYZE
WITH DeptStats AS (
    SELECT 
        d.id,
        d.name,
        d.abbrev,
        d.school_id,
        COUNT(DISTINCT c.id) as total_courses,
        COUNT(DISTINCT p.id) as total_professors,
        COUNT(DISTINCT r.id) as total_reviews,
        ROUND(AVG(r.difficulty)::numeric, 1) as avg_difficulty,
        ROUND(AVG(r.workload_rating)::numeric, 1) as avg_workload,
        ROUND(AVG(r.overall_rating)::numeric, 1) as avg_rating
    FROM department d
    LEFT JOIN department_courses dc ON d.id = dc.department_id
    LEFT JOIN course c ON dc.course_id = c.id
    LEFT JOIN professors_courses pc ON c.id = pc.course_id
    LEFT JOIN professor p ON pc.professor_id = p.id
    LEFT JOIN review r ON r.course_id = c.id
    WHERE d.abbrev = 'CSC'
    GROUP BY d.id, d.name, d.abbrev, d.school_id
)
SELECT 
    ds.*,
    array_agg(DISTINCT t.name) FILTER (WHERE t.name IS NOT NULL) as common_tags
FROM DeptStats ds
LEFT JOIN department_courses dc ON ds.id = dc.department_id
LEFT JOIN course c ON dc.course_id = c.id
LEFT JOIN review r ON r.course_id = c.id
LEFT JOIN review_tags rt ON r.id = rt.review_id
LEFT JOIN tag t ON rt.tag_id = t.id
GROUP BY ds.id, ds.name, ds.abbrev, ds.school_id, ds.total_courses, 
         ds.total_professors, ds.total_reviews, ds.avg_difficulty, 
         ds.avg_workload, ds.avg_rating

| QUERY PLAN                                                                                                                                                                                                                                    |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GroupAggregate  (cost=490.45..494.24 rows=1 width=224) (actual time=0.363..0.367 rows=1 loops=1)                                                                                                                                              |
|   Group Key: d.id, d.name, d.abbrev, d.school_id, (count(DISTINCT c_1.id)), (count(DISTINCT p.id)), (count(DISTINCT r_1.id)), (round(avg(r_1.difficulty), 1)), (round(avg(r_1.workload_rating), 1)), (round(avg(r_1.overall_rating), 1))      |
|   ->  Sort  (cost=490.45..490.77 rows=126 width=224) (actual time=0.334..0.339 rows=11 loops=1)                                                                                                                                               |
|         Sort Key: d.id, d.name, d.abbrev, d.school_id, (count(DISTINCT c_1.id)), (count(DISTINCT p.id)), (count(DISTINCT r_1.id)), (round(avg(r_1.difficulty), 1)), (round(avg(r_1.workload_rating), 1)), (round(avg(r_1.overall_rating), 1)) |
|         Sort Method: quicksort  Memory: 26kB                                                                                                                                                                                                  |
|         ->  Nested Loop Left Join  (cost=43.33..486.06 rows=126 width=224) (actual time=0.235..0.272 rows=11 loops=1)                                                                                                                         |
|               ->  Nested Loop Left Join  (cost=43.18..463.90 rows=126 width=196) (actual time=0.227..0.253 rows=11 loops=1)                                                                                                                   |
|                     ->  Nested Loop Left Join  (cost=43.02..444.87 rows=40 width=196) (actual time=0.206..0.224 rows=6 loops=1)                                                                                                               |
|                           ->  GroupAggregate  (cost=32.05..414.17 rows=1 width=192) (actual time=0.179..0.182 rows=1 loops=1)                                                                                                                 |
|                                 Group Key: d.id                                                                                                                                                                                               |
|                                 ->  Nested Loop Left Join  (cost=32.05..92.34 rows=18389 width=96) (actual time=0.119..0.132 rows=6 loops=1)                                                                                                  |
|                                       ->  Index Scan using department_pkey on department d  (cost=0.13..3.52 rows=1 width=72) (actual time=0.011..0.014 rows=1 loops=1)                                                                       |
|                                             Filter: ((abbrev)::text = 'CSC'::text)                                                                                                                                                            |
|                                             Rows Removed by Filter: 4                                                                                                                                                                         |
|                                       ->  Hash Left Join  (cost=31.92..84.36 rows=446 width=28) (actual time=0.105..0.115 rows=6 loops=1)                                                                                                     |
|                                             Hash Cond: (pc.professor_id = p.id)                                                                                                                                                               |
|                                             ->  Hash Right Join  (cost=30.79..82.03 rows=446 width=28) (actual time=0.087..0.094 rows=6 loops=1)                                                                                              |
|                                                   Hash Cond: (pc.course_id = c_1.id)                                                                                                                                                          |
|                                                   ->  Seq Scan on professors_courses pc  (cost=0.00..32.60 rows=2260 width=8) (actual time=0.006..0.006 rows=7 loops=1)                                                                       |
|                                                   ->  Hash  (cost=30.29..30.29 rows=40 width=24) (actual time=0.071..0.073 rows=6 loops=1)                                                                                                    |
|                                                         Buckets: 1024  Batches: 1  Memory Usage: 9kB                                                                                                                                          |
|                                                         ->  Hash Right Join  (cost=10.97..30.29 rows=40 width=24) (actual time=0.055..0.069 rows=6 loops=1)                                                                                   |
|                                                               Hash Cond: (c_1.id = dc_1.course_id)                                                                                                                                            |
|                                                               ->  Hash Right Join  (cost=1.27..20.40 rows=43 width=20) (actual time=0.028..0.036 rows=19 loops=1)                                                                             |
|                                                                     Hash Cond: (r_1.course_id = c_1.id)                                                                                                                                       |
|                                                                     ->  Seq Scan on review r_1  (cost=0.00..17.20 rows=720 width=20) (actual time=0.004..0.006 rows=12 loops=1)                                                               |
|                                                                     ->  Hash  (cost=1.12..1.12 rows=12 width=4) (actual time=0.014..0.014 rows=12 loops=1)                                                                                    |
|                                                                           Buckets: 1024  Batches: 1  Memory Usage: 9kB                                                                                                                        |
|                                                                           ->  Seq Scan on course c_1  (cost=0.00..1.12 rows=12 width=4) (actual time=0.007..0.010 rows=12 loops=1)                                                            |
|                                                               ->  Hash  (cost=9.56..9.56 rows=11 width=8) (actual time=0.014..0.014 rows=3 loops=1)                                                                                           |
|                                                                     Buckets: 1024  Batches: 1  Memory Usage: 9kB                                                                                                                              |
|                                                                     ->  Bitmap Heap Scan on department_courses dc_1  (cost=1.34..9.56 rows=11 width=8) (actual time=0.007..0.008 rows=3 loops=1)                                              |
|                                                                           Recheck Cond: (d.id = department_id)                                                                                                                                |
|                                                                           Heap Blocks: exact=1                                                                                                                                                |
|                                                                           ->  Bitmap Index Scan on department_courses_pkey  (cost=0.00..1.34 rows=11 width=0) (actual time=0.003..0.003 rows=3 loops=1)                                       |
|                                                                                 Index Cond: (department_id = d.id)                                                                                                                            |
|                                             ->  Hash  (cost=1.06..1.06 rows=6 width=4) (actual time=0.009..0.009 rows=6 loops=1)                                                                                                              |
|                                                   Buckets: 1024  Batches: 1  Memory Usage: 9kB                                                                                                                                                |
|                                                   ->  Seq Scan on professor p  (cost=0.00..1.06 rows=6 width=4) (actual time=0.005..0.006 rows=6 loops=1)                                                                                     |
|                           ->  Hash Right Join  (cost=10.97..30.29 rows=40 width=8) (actual time=0.026..0.039 rows=6 loops=1)                                                                                                                  |
|                                 Hash Cond: (c.id = dc.course_id)                                                                                                                                                                              |
|                                 ->  Hash Right Join  (cost=1.27..20.40 rows=43 width=8) (actual time=0.013..0.020 rows=19 loops=1)                                                                                                            |
|                                       Hash Cond: (r.course_id = c.id)                                                                                                                                                                         |
|                                       ->  Seq Scan on review r  (cost=0.00..17.20 rows=720 width=8) (actual time=0.002..0.003 rows=12 loops=1)                                                                                                |
|                                       ->  Hash  (cost=1.12..1.12 rows=12 width=4) (actual time=0.006..0.006 rows=12 loops=1)                                                                                                                  |
|                                             Buckets: 1024  Batches: 1  Memory Usage: 9kB                                                                                                                                                      |
|                                             ->  Seq Scan on course c  (cost=0.00..1.12 rows=12 width=4) (actual time=0.002..0.003 rows=12 loops=1)                                                                                            |
|                                 ->  Hash  (cost=9.56..9.56 rows=11 width=8) (actual time=0.007..0.007 rows=3 loops=1)                                                                                                                         |
|                                       Buckets: 1024  Batches: 1  Memory Usage: 9kB                                                                                                                                                            |
|                                       ->  Bitmap Heap Scan on department_courses dc  (cost=1.34..9.56 rows=11 width=8) (actual time=0.005..0.005 rows=3 loops=1)                                                                              |
|                                             Recheck Cond: (d.id = department_id)                                                                                                                                                              |
|                                             Heap Blocks: exact=1                                                                                                                                                                              |
|                                             ->  Bitmap Index Scan on department_courses_pkey  (cost=0.00..1.34 rows=11 width=0) (actual time=0.003..0.003 rows=3 loops=1)                                                                     |
|                                                   Index Cond: (department_id = d.id)                                                                                                                                                          |
|                     ->  Index Only Scan using review_tags_pkey on review_tags rt  (cost=0.15..0.37 rows=11 width=8) (actual time=0.004..0.004 rows=1 loops=6)                                                                                 |
|                           Index Cond: (review_id = r.id)                                                                                                                                                                                      |
|                           Heap Fetches: 8                                                                                                                                                                                                     |
|               ->  Index Scan using tag_pkey on tag t  (cost=0.15..0.18 rows=1 width=36) (actual time=0.001..0.001 rows=1 loops=11)                                                                                                            |
|                     Index Cond: (id = rt.tag_id)                                                                                                                                                                                              |
| Planning Time: 1.842 ms                                                                                                                                                                                                                       |
| Execution Time: 0.665 ms                                                                                                                                                                                                                      |

The query is using a lot of nested for-loops So we used CREATE INDEX ON department(abbrev); And re-ran it. 
It didn't save much time cause there's not many departments to begin with. 

### Second Query in Endpoint:

EXPLAIN analyze
SELECT t.name, COUNT(*) as tag_count
FROM department d
JOIN department_courses dc ON d.id = dc.department_id
JOIN course c ON dc.course_id = c.id
JOIN review r ON r.course_id = c.id
JOIN review_tags rt ON r.id = rt.review_id
JOIN tag t ON rt.tag_id = t.id
WHERE d.abbrev = 'CSC'
GROUP BY t.name
ORDER BY tag_count DESC
LIMIT 10


| QUERY PLAN                                                                                                                                                                            |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Limit  (cost=732.74..732.76 rows=10 width=40) (actual time=0.160..0.164 rows=5 loops=1)                                                                                               |
|   ->  Sort  (cost=732.74..735.91 rows=1270 width=40) (actual time=0.159..0.163 rows=5 loops=1)                                                                                        |
|         Sort Key: (count(*)) DESC                                                                                                                                                     |
|         Sort Method: quicksort  Memory: 25kB                                                                                                                                          |
|         ->  HashAggregate  (cost=692.59..705.29 rows=1270 width=40) (actual time=0.129..0.138 rows=5 loops=1)                                                                         |
|               Group Key: t.name                                                                                                                                                       |
|               Batches: 1  Memory Usage: 73kB                                                                                                                                          |
|               ->  Hash Join  (cost=152.34..266.96 rows=85127 width=32) (actual time=0.111..0.124 rows=8 loops=1)                                                                      |
|                     Hash Cond: (dc.course_id = c.id)                                                                                                                                  |
|                     ->  Hash Join  (cost=151.07..251.99 rows=5107 width=40) (actual time=0.083..0.094 rows=8 loops=1)                                                                 |
|                           Hash Cond: (rt.review_id = r.id)                                                                                                                            |
|                           ->  Hash Join  (cost=38.58..77.13 rows=2260 width=36) (actual time=0.031..0.037 rows=18 loops=1)                                                            |
|                                 Hash Cond: (rt.tag_id = t.id)                                                                                                                         |
|                                 ->  Seq Scan on review_tags rt  (cost=0.00..32.60 rows=2260 width=8) (actual time=0.003..0.005 rows=18 loops=1)                                       |
|                                 ->  Hash  (cost=22.70..22.70 rows=1270 width=36) (actual time=0.011..0.012 rows=14 loops=1)                                                           |
|                                       Buckets: 2048  Batches: 1  Memory Usage: 17kB                                                                                                   |
|                                       ->  Seq Scan on tag t  (cost=0.00..22.70 rows=1270 width=36) (actual time=0.004..0.006 rows=14 loops=1)                                         |
|                           ->  Hash  (cost=92.15..92.15 rows=1627 width=12) (actual time=0.044..0.046 rows=4 loops=1)                                                                  |
|                                 Buckets: 2048  Batches: 1  Memory Usage: 17kB                                                                                                         |
|                                 ->  Hash Join  (cost=16.38..92.15 rows=1627 width=12) (actual time=0.039..0.044 rows=4 loops=1)                                                       |
|                                       Hash Cond: (r.course_id = dc.course_id)                                                                                                         |
|                                       ->  Seq Scan on review r  (cost=0.00..17.20 rows=720 width=8) (actual time=0.004..0.005 rows=12 loops=1)                                        |
|                                       ->  Hash  (cost=10.73..10.73 rows=452 width=4) (actual time=0.023..0.025 rows=3 loops=1)                                                        |
|                                             Buckets: 1024  Batches: 1  Memory Usage: 9kB                                                                                              |
|                                             ->  Nested Loop  (cost=1.34..10.73 rows=452 width=4) (actual time=0.018..0.020 rows=3 loops=1)                                            |
|                                                   ->  Seq Scan on department d  (cost=0.00..1.06 rows=1 width=4) (actual time=0.004..0.005 rows=1 loops=1)                            |
|                                                         Filter: ((abbrev)::text = 'CSC'::text)                                                                                        |
|                                                         Rows Removed by Filter: 4                                                                                                     |
|                                                   ->  Bitmap Heap Scan on department_courses dc  (cost=1.34..9.56 rows=11 width=8) (actual time=0.011..0.012 rows=3 loops=1)          |
|                                                         Recheck Cond: (department_id = d.id)                                                                                          |
|                                                         Heap Blocks: exact=1                                                                                                          |
|                                                         ->  Bitmap Index Scan on department_courses_pkey  (cost=0.00..1.34 rows=11 width=0) (actual time=0.007..0.007 rows=3 loops=1) |
|                                                               Index Cond: (department_id = d.id)                                                                                      |
|                     ->  Hash  (cost=1.12..1.12 rows=12 width=4) (actual time=0.019..0.019 rows=12 loops=1)                                                                            |
|                           Buckets: 1024  Batches: 1  Memory Usage: 9kB                                                                                                                |
|                           ->  Seq Scan on course c  (cost=0.00..1.12 rows=12 width=4) (actual time=0.009..0.012 rows=12 loops=1)                                                      |
| Planning Time: 2.617 ms                                                                                                                                                               |
| Execution Time: 0.322 ms                                                                                                                                                              |

Again used same indexes. It didn't help as much. 