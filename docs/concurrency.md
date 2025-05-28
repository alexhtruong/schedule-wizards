
# Concurrency Analysis
### By Alex Truong, Kyle Lin, and Colin Hassett

## Complex Endpoints & Their Concurrency Issues

We have identified several endpoints that are susceptible to concurrency phenomena:

1. `GET /departments/{department_abbrev}/statistics`
2. `GET /courses/{course_code}/statistics`
3. Review submission endpoints

## Case 1: Phantom Reads in Department Statistics

When fetching department statistics, we could encounter phantom reads if new reviews or courses are added while we're calculating statistics.

```
    T1 as Transaction 1 (Get Stats)
    DB as Database
    T2 as Transaction 2 (Add Review)
    
    T1->>DB: Begin Transaction
    T1->>DB: Read department courses
    T1->>DB: Calculate avg_rating (3.5)
    T2->>DB: Begin Transaction
    T2->>DB: Insert new review (rating: 1.0)
    T2->>DB: Commit
    T1->>DB: Read reviews again for tags
    T1->>DB: Return stats (avg still 3.5)
    T1->>DB: Commit

    Note over T1,DB: Problem: Stats are inconsistent with new data
```

## Case 2: Non-Repeatable Reads in Course Statistics

When calculating course statistics, we might get non-repeatable reads if a professor's information is updated while we're aggregating data.

```
    T1 as Transaction 1 (Get Course Stats)
    DB as Database
    T2 as Transaction 2 (Update Professor)
    
    T1->>DB: Begin Transaction
    T1->>DB: Read course info
    T1->>DB: Read professor data
    T2->>DB: Begin Transaction
    T2->>DB: Update professor name
    T2->>DB: Commit
    T1->>DB: Read professor reviews
    T1->>DB: Return stats (with old/new mix)
    T1->>DB: Commit

    Problem: Inconsistent professor data in response
```

## Case 3: Lost Update in Review Statistics

When multiple users submit reviews simultaneously, we could encounter lost updates when updating the course's average statistics.

```
    T1 as Transaction 1 (Review 1)
    DB as Database
    T2 as Transaction 2 (Review 2)
    
    T1->>DB: Begin Transaction
    T2->>DB: Begin Transaction
    T1->>DB: Read current avg (3.0)
    T2->>DB: Read current avg (3.0)
    T1->>DB: Calculate new avg with Review 1 (4.0)
    T2->>DB: Calculate new avg with Review 2 (2.0)
    T1->>DB: Update avg to 4.0
    T1->>DB: Commit
    T2->>DB: Update avg to 2.0
    T2->>DB: Commit

    Problem: Review 1's contribution is lost
```

## Concurrency Control Solutions

### 1. For Statistics Endpoints (Cases 1 & 2)
We will use repeatable read isolation level because:
- It prevents non-repeatable reads by maintaining consistent snapshots
- It prevents phantom reads within the same transaction
- It allows for concurrent reads without blocking writes

### 2. For Review Updates (Case 3)
We'll implement:
- Triggers with SERIALIZABLE isolation for maintaining aggregate statistics
- Atomic updates to prevent lost updates
- Optimistic locking for concurrent review submissions


This ensures atomic updates of statistics when reviews are added or modified. 
