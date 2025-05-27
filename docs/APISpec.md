# Schedule Wizards API Specification

## Endpoints

## Two Complex Endpoints

### Professor Search

#### `/professors/search/by-tags` (GET)

Search for professors based on review tags and get detailed matching information.

**Query Parameters**:

- `tags` (required): List of tags to search for (e.g. ["Clear Explanations", "Engaging"])

**Used for**:

- Finding professors by teaching style/characteristics
- Discovering professors based on student feedback
- Getting tag frequency statistics for professors

**Response**:

```json
[
  {
    "professor": {
      "id": "prof123",
      "name": "Jane Doe",
      "department": "CSC",
      "num_reviews": 15,
      "courses": []
    },
    "matched_tags": ["Clear Explanations", "Engaging"],
    "matching_tag_count": 2,
    "tag_frequency": 25
  },
  {
    "professor": {
      "id": "prof456",
      "name": "John Smith",
      "department": "MATH",
      "num_reviews": 8,
      "courses": []
    },
    "matched_tags": ["Clear Explanations"],
    "matching_tag_count": 1,
    "tag_frequency": 12
  }
]
```

**Notes**:

- Results are ordered by:
  1. Number of matching tags (descending)
  2. Tag frequency in reviews (descending)
- Tag matching is case-sensitive
- Course lists are omitted from professor objects for performance

### Department Statistics

#### `/departments/{department_abbrev}/statistics` (GET)

Get comprehensive statistics for a department including course counts, professor counts, and aggregated review metrics.

**Parameters**:

- `department_abbrev`: Department abbreviation (e.g., "CSC", "ME")

**Used for**:

- Getting department-wide analytics
- Comparing departments
- Understanding overall department performance and student sentiment

**Response**:

```json
{
  "department": {
    "department_id": 1,
    "name": "Computer Science",
    "abbrev": "CSC",
    "school_id": 1
  },
  "total_courses": 45,
  "total_professors": 12,
  "average_difficulty": 3.8,
  "average_workload": 12.5,
  "average_rating": 4.2,
  "total_reviews": 324,
  "most_common_tags": [
    "Programming Heavy",
    "Project Based",
    "Challenging",
    "Good TAs",
    "Math Heavy"
  ]
}
```

**Notes**:

- All average ratings are on a scale of 1-5
- Workload is measured in hours per week
- Tags are ordered by frequency (most frequent first)
- Returns 0 for numerical values when no data is available



### Search and Retrieval

#### `/search/class/{course_id}` (GET)

Search for classes and list professors/reviews.

**Query Parameters**:

- `professor_name` (optional): Filter by professor name
- `term` (optional): Academic term (e.g. "Fall 2024")
- `minDifficulty`/`maxDifficulty` (optional): Scale 1-5
- `minWorkload`/`maxWorkload` (optional): Hours per week
- `sort_col` (optional): Sort by `rating`, `workload`, etc.
- `sort_order` (optional): `asc` or `desc` (default)

**Used for**:

- Searching classes
- Listing professors who taught a course

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