# Reveel API Specification

## Endpoints

### Search and Retrieval

#### `/search/class/{course_id}` (GET)

Search for classes and list professors/reviews.

**Query Parameters**:

- `professor_name` (optional): Filter by professor name
- `term` (optional): Academic term (e.g. "Fall 2024")
- `minDifficulty`/`maxDifficulty` (optional): Scale 1-5
- `minWorkload`/`maxWorkload` (optional): Hours per week
- `area` (optional): GE Area (e.g. `C1`, `B2`)
- `sort_col` (optional): Sort by `rating`, `workload`, etc.
- `sort_order` (optional): `asc` or `desc` (default)

**Used for**:

- Searching classes
- Listing professors who taught a course
- Filtering courses by GE area

**Response**:

```json
[
  {
    "course_id": "CSC101",
    "name": "Intro to Computer Science",
    "department": "CSC",
    "professors": [
      {
        "name": "Andrew Smith",
        "professor_id": "xyz456"
      }
    ]
  }
]
```

#### `/professors/{id}` (GET)

Get detailed professor information and their reviews.

**Response includes**:

- Professor details
- List of reviews
- Aggregate metrics (difficulty, workload, common tags)

**Response**:

```json
{
  "professor": {
    "id": "ahall68",
    "name": "Ashton Hall",
    "department": "ME",
    "num_reviews": 2
  },
  "reviews": [
    {
      "review_id": "rev001",
      "course": {
        "id": "103123",
        "code": "ME212",
        "name": "Engineering Dynamics"
      },
      "term": "Fall 2024",
      "difficulty_rating": 7,
      "overall_rating": 9,
      "workload_estimate": 10,
      "tags": ["Engaging", "Tough exams"],
      "comments": "Dr. Smith made lectures interesting but her exams were very hard.",
      "user_id": "user123"
    },
    {
      "review_id": "rev002",
      "course": {
        "id": "130193",
        "code": "ME211",
        "name": "Engineering Statics"
      },
      "term": "Winter 2025",
      "overall_rating": 7,
      "difficulty_rating": 7,
      "workload_estimate": 8,
      "tags": ["Helpful", "Hands-on projects"],
      "comments": "Great professor for learning by doing. Projects were fun!",
      "user_id": "user456"
    }
  ],
  "average_difficulty": 7,
  "average_workload": 9,
  "most_common_tags": ["Engaging", "Helpful", "Tough exams"]
}
```

#### `/courses/{id}/aggregates` (GET)

Get aggregated course insights.

**Response includes**:

- Average ratings
- Difficulty metrics
- Review counts
- Popular tags

**Response**:

```json
{
  "average_rating": 4.6,
  "average_difficulty": 2.3,
  "average_workload": 5.2,
  "total_reviews": 37,
  "top_tags": ["Interesting Readings", "Chill Professors"]
}
```

### Creation Endpoints

#### `/courses` (POST)

Create a new course.

**Request Body**:

```json
{
  "course_code": "string",
  "name": "string",
  "department": "string",
  "description": "string"
}
```

#### `/professors` (POST)

Create a new professor.

**Request Body**:

```json
{
  "name": "string",
  "department": "string",
  "metadata": {}
}
```

#### `/reviews` (POST)

Submit a new review.

**Request Body**:

```json
{
  "course_id": "string",
  "professor_id": "string",
  "professor_name": "string",
  "user_id": "string",
  "term": "string",
  "difficulty_rating": number,
  "overall_rating": number,
  "workload_estimate": number,
  "tags": string[],
  "comments": "string"
}
```

### Moderation

#### `/reviews/:id/report` (POST)

Report a review for moderation.

**Request Body**:

```json
{
  "reason": "string",
  "details": "string"
}
```

**Response**:

```json
{
  "message": "Review has been reported and will be reviewed by moderators."
}
```
