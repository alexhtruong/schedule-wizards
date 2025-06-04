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

```sql
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
        ROUND(AVG(r.difficulty), 1) as avg_difficulty,
        ROUND(AVG(r.workload_rating), 1) as avg_workload,
        ROUND(AVG(r.overall_rating), 1) as avg_rating
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
```

GroupAggregate  (cost=54699939.14..131580135.94 rows=4 width=224) (actual time=375359.691..375359.756 rows=1 loops=1)
  Group Key: d.id, d.name, d.abbrev, d.school_id, (count(DISTINCT c_1.id)), (count(DISTINCT p.id)), (count(DISTINCT r_1.id)), (round(avg(r_1.difficulty), 1)), (round(avg(r_1.workload_rating), 1)), (round(avg(r_1.overall_rating), 1))
  ->  Incremental Sort  (cost=54699939.14..131425516.37 rows=5622528 width=224) (actual time=373583.677..375034.514 rows=1124113 loops=1)
        Sort Key: d.id, d.name, d.abbrev, d.school_id, (count(DISTINCT c_1.id)), (count(DISTINCT p.id)), (count(DISTINCT r_1.id)), (round(avg(r_1.difficulty), 1)), (round(avg(r_1.workload_rating), 1)), (round(avg(r_1.overall_rating), 1)), t.name
        Presorted Key: d.id
        Full-sort Groups: 1  Sort Method: quicksort  Average Memory: 31kB  Peak Memory: 31kB
        Pre-sorted Groups: 1  Sort Method: external merge  Average Disk: 106848kB  Peak Disk: 106848kB
        ->  Nested Loop Left Join  (cost=29148173.96..129589584.22 rows=5622528 width=224) (actual time=365054.352..369383.020 rows=1124113 loops=1)
              ->  Merge Left Join  (cost=29116792.65..127795918.10 rows=45 width=196) (actual time=364912.211..364912.319 rows=9 loops=1)
                    Merge Cond: (d.id = dc.department_id)
                    ->  GroupAggregate  (cost=29116634.15..127795747.84 rows=4 width=192) (actual time=364911.610..364911.666 rows=1 loops=1)
                          Group Key: d.id
                          ->  Incremental Sort  (cost=29116634.15..121186216.49 rows=377687500 width=96) (actual time=208621.258..251390.621 rows=212667958 loops=1)
                                Sort Key: d.id, c_1.id
                                Presorted Key: d.id
                                Full-sort Groups: 1  Sort Method: quicksort  Average Memory: 29kB  Peak Memory: 29kB
                                Pre-sorted Groups: 1  Sort Method: external merge  Average Disk: 13734072kB  Peak Disk: 13734072kB
                                ->  Nested Loop Left Join  (cost=471.31..8343883.74 rows=377687500 width=96) (actual time=592.388..29889.300 rows=212667958 loops=1)
                                      ->  Merge Left Join  (cost=178.67..190.10 rows=11 width=76) (actual time=589.995..590.088 rows=9 loops=1)
                                            Merge Cond: (d.id = dc_1.department_id)
                                            ->  Sort  (cost=20.16..20.18 rows=4 width=72) (actual time=589.938..589.941 rows=1 loops=1)
                                                  Sort Key: d.id
                                                  Sort Method: quicksort  Memory: 25kB
                                                  ->  Seq Scan on department d  (cost=0.00..20.12 rows=4 width=72) (actual time=589.924..589.930 rows=1 loops=1)
"                                                        Filter: (abbrev = 'CSC'::text)"
                                                        Rows Removed by Filter: 4
                                            ->  Sort  (cost=158.51..164.16 rows=2260 width=8) (actual time=0.041..0.097 rows=10 loops=1)
                                                  Sort Key: dc_1.department_id
                                                  Sort Method: quicksort  Memory: 25kB
                                                  ->  Seq Scan on department_courses dc_1  (cost=0.00..32.60 rows=2260 width=8) (actual time=0.018..0.019 rows=15 loops=1)
                                      ->  Hash Right Join  (cost=292.64..415658.64 rows=34312500 width=24) (actual time=1.728..1537.426 rows=23629773 loops=9)
                                            Hash Cond: (r_1.course_id = c_1.id)
                                            ->  Seq Scan on review r_1  (cost=0.00..27241.00 rows=1000000 width=20) (actual time=0.025..102.773 rows=1000000 loops=9)
                                            ->  Hash  (cost=285.77..285.77 rows=549 width=8) (actual time=1.686..1.686 rows=378 loops=9)
                                                  Buckets: 1024  Batches: 1  Memory Usage: 24kB
                                                  ->  Hash Right Join  (cost=163.11..285.77 rows=549 width=8) (actual time=1.004..1.642 rows=378 loops=9)
                                                        Hash Cond: (p.id = pc.professor_id)
                                                        ->  Seq Scan on professor p  (cost=0.00..95.58 rows=5758 width=4) (actual time=0.005..0.301 rows=5000 loops=9)
                                                        ->  Hash  (cost=156.25..156.25 rows=549 width=8) (actual time=0.992..0.993 rows=378 loops=9)
                                                              Buckets: 1024  Batches: 1  Memory Usage: 24kB
                                                              ->  Hash Right Join  (cost=0.17..156.25 rows=549 width=8) (actual time=0.035..0.949 rows=378 loops=9)
                                                                    Hash Cond: (pc.course_id = c_1.id)
                                                                    ->  Seq Scan on professors_courses pc  (cost=0.00..126.90 rows=8790 width=8) (actual time=0.006..0.426 rows=8790 loops=9)
                                                                    ->  Hash  (cost=0.16..0.16 rows=1 width=4) (actual time=0.016..0.017 rows=1 loops=9)
                                                                          Buckets: 1024  Batches: 1  Memory Usage: 9kB
                                                                          ->  Index Only Scan using course_pkey on course c_1  (cost=0.14..0.16 rows=1 width=4) (actual time=0.010..0.011 rows=1 loops=9)
                                                                                Index Cond: (id = dc_1.course_id)
                                                                                Heap Fetches: 0
                    ->  Sort  (cost=158.51..164.16 rows=2260 width=8) (actual time=0.079..0.096 rows=10 loops=1)
                          Sort Key: dc.department_id
                          Sort Method: quicksort  Memory: 25kB
                          ->  Seq Scan on department_courses dc  (cost=0.00..32.60 rows=2260 width=8) (actual time=0.049..0.050 rows=15 loops=1)
              ->  Hash Left Join  (cost=31381.31..69293.74 rows=124945 width=36) (actual time=138.157..486.917 rows=124901 loops=9)
                    Hash Cond: (rt.tag_id = t.id)
                    ->  Hash Right Join  (cost=31342.73..68926.09 rows=124945 width=8) (actual time=138.132..473.635 rows=124901 loops=9)
                          Hash Cond: (rt.review_id = r.id)
                          ->  Seq Scan on review_tags rt  (cost=0.00..28837.21 rows=1999121 width=8) (actual time=0.030..111.706 rows=1999121 loops=9)
                          ->  Hash  (cost=30561.48..30561.48 rows=62500 width=8) (actual time=138.050..138.050 rows=62495 loops=9)
                                Buckets: 65536  Batches: 1  Memory Usage: 2963kB
                                ->  Hash Right Join  (cost=0.17..30561.48 rows=62500 width=8) (actual time=0.049..127.891 rows=62495 loops=9)
                                      Hash Cond: (r.course_id = c.id)
                                      ->  Seq Scan on review r  (cost=0.00..27241.00 rows=1000000 width=8) (actual time=0.022..66.582 rows=1000000 loops=9)
                                      ->  Hash  (cost=0.16..0.16 rows=1 width=4) (actual time=0.019..0.019 rows=1 loops=9)
                                            Buckets: 1024  Batches: 1  Memory Usage: 9kB
                                            ->  Index Only Scan using course_pkey on course c  (cost=0.14..0.16 rows=1 width=4) (actual time=0.012..0.013 rows=1 loops=9)
                                                  Index Cond: (id = dc.course_id)
                                                  Heap Fetches: 0
                    ->  Hash  (cost=22.70..22.70 rows=1270 width=36) (actual time=0.030..0.031 rows=11 loops=1)
                          Buckets: 2048  Batches: 1  Memory Usage: 17kB
                          ->  Seq Scan on tag t  (cost=0.00..22.70 rows=1270 width=36) (actual time=0.022..0.023 rows=11 loops=1)
Planning Time: 11.401 ms
JIT:
  Functions: 83
  Options: Inlining true, Optimization true, Expressions true, Deforming true
  Timing: Generation 10.177 ms (Deform 4.632 ms), Inlining 39.608 ms, Optimization 328.217 ms, Emission 222.637 ms, Total 600.638 ms
Execution Time: 375631.140 ms

### Second Query in Endpoint:

```sql
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
```

→ Limit (cost=48246.25..48246.28 rows=10 width=40) (actual time=724.863..750.064 rows=10 loops=1)
→ Sort (cost=48246.25..48246.75 rows=200 width=40) (actual time=724.861..750.059 rows=10 loops=1)
Sort Key: (count(\*)) DESC
Sort Method: quicksort Memory: 25kB
→ Finalize GroupAggregate (cost=48191.26..48241.93 rows=200 width=40) (actual time=724.829..750.047 rows=11 loops=1)
Group Key: t.name
→ Gather Merge (cost=48191.26..48237.93 rows=400 width=40) (actual time=724.812..750.023 rows=33 loops=1)
Workers Planned: 2
Workers Launched: 2
→ Sort (cost=47191.24..47191.74 rows=200 width=40) (actual time=638.192..638.210 rows=11 loops=3)
Sort Key: t.name
Sort Method: quicksort Memory: 25kB
Worker 0: Sort Method: quicksort Memory: 25kB
Worker 1: Sort Method: quicksort Memory: 25kB
→ Partial HashAggregate (cost=47181.59..47183.59 rows=200 width=40) (actual time=638.109..638.128 rows=11 loops=3)
Group Key: t.name
Batches: 1 Memory Usage: 40kB
Worker 0: Batches: 1 Memory Usage: 40kB
Worker 1: Batches: 1 Memory Usage: 40kB
→ Hash Join (cost=23584.61..44318.27 rows=572665 width=32) (actual time=270.678..560.306 rows=374704 loops=3)
Hash Cond: (dc.course_id = c.id)
→ Hash Join (cost=23583.25..44194.10 rows=45813 width=40) (actual time=270.627..500.363 rows=374704 loops=3)
Hash Cond: (rt.tag_id = t.id)
→ Parallel Hash Join (cost=23544.68..44034.87 rows=45813 width=12) (actual time=270.588..435.076 rows=374704 loops=3)
Hash Cond: (rt.review_id = r.id)
→ Parallel Seq Scan on review_tags rt (cost=0.00..17175.67 rows=832967 width=8) (actual time=0.096..51.710 rows=666374 loops=3)
→ Parallel Hash (cost=23258.22..23258.22 rows=22917 width=12) (actual time=136.539..136.546 rows=187486 loops=3)
Buckets: 131072 (originally 65536) Batches: 8 (originally 1) Memory Usage: 4384kB
→ Hash Join (cost=58.88..23258.22 rows=22917 width=12) (actual time=0.110..76.572 rows=187486 loops=3)
Hash Cond: (r.course_id = dc.course_id)
→ Parallel Seq Scan on review r (cost=0.00..21407.67 rows=416667 width=8) (actual time=0.037..30.079 rows=333333 loops=3)
→ Hash (cost=58.74..58.74 rows=11 width=4) (actual time=0.044..0.049 rows=9 loops=3)
Buckets: 1024 Batches: 1 Memory Usage: 9kB
→ Hash Join (cost=20.18..58.74 rows=11 width=4) (actual time=0.039..0.046 rows=9 loops=3)
Hash Cond: (dc.department_id = d.id)
→ Seq Scan on department_courses dc (cost=0.00..32.60 rows=2260 width=8) (actual time=0.014..0.016 rows=15 loops=3)
→ Hash (cost=20.12..20.12 rows=4 width=4) (actual time=0.012..0.014 rows=1 loops=3)
Buckets: 1024 Batches: 1 Memory Usage: 9kB
→ Seq Scan on department d (cost=0.00..20.12 rows=4 width=4) (actual time=0.008..0.009 rows=1 loops=3)
Filter: (abbrev = 'CSC'::text)
Rows Removed by Filter: 4
→ Hash (cost=22.70..22.70 rows=1270 width=36) (actual time=0.019..0.020 rows=11 loops=3)
Buckets: 2048 Batches: 1 Memory Usage: 17kB
→ Seq Scan on tag t (cost=0.00..22.70 rows=1270 width=36) (actual time=0.013..0.014 rows=11 loops=3)
→ Hash (cost=1.16..1.16 rows=16 width=4) (actual time=0.021..0.022 rows=16 loops=3)
Buckets: 1024 Batches: 1 Memory Usage: 9kB
→ Seq Scan on course c (cost=0.00..1.16 rows=16 width=4) (actual time=0.014..0.016 rows=16 loops=3)

Planning Time: 1.188 ms
Execution Time: 750.427 ms

```

```
