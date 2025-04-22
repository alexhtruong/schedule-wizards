# API Specification for Reveel

## 1. Basic Review Submission

The API calls are made in this sequence when making a submission:
1. `Search Courses`
2. `If course or professor don't exist, create them`
3. `Post Review`

### 1.1. Search for the class - `/search/class/{course_id}` (GET)

Checks if the class already exists and lists all professors and reviews based on the query parameters.

**Query Parameters**:

- `professor_name` (optional): The name of the professor.
- `term` (optional): The academic term to filter by (e.g. "Fall 2024", "Spring 2025").
- `minDifficulty` (optional): The minimum difficulty rating to include (scale 1-5).
- `maxDifficulty` (optional): The maximum difficulty rating to include (scale 1-5).
- `minWorkload` (optional): The minimum workload in hours per week.
- `maxWorkload` (optional): The maximum workload in hours per week.
- `area` (optional): The GE Area (e.g., `C1`, `B2`)
- `sort_col` (optional): Column to sort by (e.g., `rating`, `workload`)
- `sort_order` (optional): asc or desc (default: `desc`)

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

### 1.2. If course or professor doesn't exist, create them - `/courses` (POST) OR `/professors` (POST)

**Request**:
#### 1.2a Add Course
```json
{
  "course_code": "CSC101",
  "name": "Intro to Computer Science",
  "department": "CSC",
  "description": "Fundamentals of programming."
}
```

#### 1.2b Add Professor
**Request**:

```json
{
  "name": "Andrew Smith",
  "department": "CSC",
  "metadata": {}
}
```

### 1.3. Post Review - `/reviews/` (POST)

Post a review for a professor's course.

**Request**:

```json
{
  "course_id": "CSC101",
  "professor_name": "Andrew Smith",
  "professor_id": "xyz456",
  "user_id": "user001", 
  "term": "Fall 2024",
  "difficulty_rating": 3,
  "overall_rating": 4,
  "workload_estimate": 5,
  "tags": ["Engaging", "Tough exams"],
  "comments": "Great teaching but tough grading."
}
```

## 2. Figuring out which professor to take for a certain class

The API calls are made in this sequence:
1. `Search for professors that taught the class`
2. `Look deeper into a certain professor to see all of their reviews`

### 2.1 Search for professors that taught the class - `/search/class/{course_id}` (GET)

**Query Parameters**:

- `professor_name` (optional): The name of the professor.
- `term` (optional): The academic term to filter by (e.g. "Fall 2024", "Spring 2025").
- `minDifficulty` (optional): The minimum difficulty rating to include (scale 1-5).
- `maxDifficulty` (optional): The maximum difficulty rating to include (scale 1-5).
- `minWorkload` (optional): The minimum workload in hours per week.
- `maxWorkload` (optional): The maximum workload in hours per week.
- `area` (optional): The GE Area (e.g., `C1`, `B2`)
- `sort_col` (optional): Column to sort by (e.g., `rating`, `workload`)
- `sort_order` (optional): asc or desc (default: `desc`)

**Response**:

```json
[
  {
    "course_id": "ME212",
    "name": "Engineering Dynamics",
    "department": "ME",
    "professors": [
      {
        "name": "Sally Cartman",
        "professor_id": "abc123"
      }
      {
        "name": "Ashton Hall",
        "professor_id": "ahall68"
      }
    ]
  }
]
```

### 2.2 View Professor's Reviews - `/professors/ahall68` (GET)

**Response**

```json
{
  "professor": {
    "id": "ahall68",
    "name": "Ashton Hall",
    "department": "ME",
    "num_reviews": 2,
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

## 3. Hidden Gem Exploration & Review Moderation

The API calls are made in this sequence:
1. `View All Courses in a GE Area`
2. `View Aggregated Insights for the Course`
3. `View All the Professors Who Have Taught the Course`
4. `View Reviews for a Specific Professor`
5. `Review Moderation`

### 3.1 View All Courses in a GE Area - `/search/class/?area=C1&sort_col=rating&sort_order=desc` (GET)

**Query Parameters**:

- `professor_name` (optional): The name of the professor.
- `term` (optional): The academic term to filter by (e.g. "Fall 2024", "Spring 2025").
- `minDifficulty` (optional): The minimum difficulty rating to include (scale 1-5).
- `maxDifficulty` (optional): The maximum difficulty rating to include (scale 1-5).
- `minWorkload` (optional): The minimum workload in hours per week.
- `maxWorkload` (optional): The maximum workload in hours per week.
- `area` (optional): The GE Area (e.g., `C1`, `B2`)
- `sort_col` (optional): Column to sort by (e.g., `rating`, `workload`)
- `sort_order` (optional): asc or desc (default: `desc`)

**Response**:

```json
[
    {
      "courses": {
        {
          "course_id": "CSC101",
          "professor_name": "Andrew Smith",
          "professor_id": "xyz456",
          "overall_rating": 10
          "term": "Fall 2024",
        },
        {
          "course_id": "ME212",
          "professor_name": "Ashton Hall",
          "professor_id": "xyz456",
          "overall_rating": 7
          "term": "Spring 2025",
        },
        {
          "course_id": "CE212",
          "professor_name": "Logan Paul",
          "professor_id": "lmc234",
          "overall_rating": 5
          "term": "Winter 2025",
        },
      }
    }
]
```

### 3.2. View Aggregated Insights for the Course - `/courses/{id}/aggregates` (GET)

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

### 3.3 View All Professors Who Have Taught the Course - `/search/class/{course_id}` (GET)

**Query Parameters**:

- `professor_name` (optional): The name of the professor.
- `term` (optional): The academic term to filter by (e.g. "Fall 2024", "Spring 2025").
- `minDifficulty` (optional): The minimum difficulty rating to include (scale 1-5).
- `maxDifficulty` (optional): The maximum difficulty rating to include (scale 1-5).
- `minWorkload` (optional): The minimum workload in hours per week.
- `maxWorkload` (optional): The maximum workload in hours per week.
- `area` (optional): The GE Area (e.g., `C1`, `B2`)
- `sort_col` (optional): Column to sort by (e.g., `rating`, `workload`)
- `sort_order` (optional): asc or desc (default: `desc`)

**Response**:

```json
[
  {
    "course_id": "CHEM124",
    "name": "Intro to Chemistry",
    "department": "CHEM",
    "professors": [
      {
        "name": "Slovak Bryka",
        "professor_id": "xyz456"
      },
      {
        "name": "Samantha Barnes",
        "professor_id": "xyz456"
      },
      {
        "name": "Alan Turing",
        "professor_id": "xyz456"
      }
    ]
  }
]
```

### 3.4 View Reviews for a Specific Professor - `/professor/:id` (GET)

**Response**

```json
{
  "professor": {
    "id": "aturing123",
    "name": "Alan Turing",
    "department": "CHEM",
    "num_reviews": 2520,
  },
  "reviews": [
    {
      "review_id": "rev001",
      "course": {
        "id": "103123",
        "code": "CHEM124",
        "name": "Intro to Chemistry"
      },
      "term": "Fall 2024",
      "difficulty_rating": 7,
      "overall_rating": 9,
      "workload_estimate": 10,
      "tags": ["Engaging", "Tough exams"],
      "comments": "Dr. Turing made lectures interesting but her exams were very hard.",
      "user_id": "user123"
    },
    {
      "review_id": "rev002",
      "course": {
        "id": "130193",
        "code": "CHEM228",
        "name": "Organic Chemistry III"
      },
      "term": "Winter 2025",
      "overall_rating": 7,
      "difficulty_rating": 7 ,
      "workload_estimate": 8,
      "tags": ["Helpful"],
      "comments": "Great professor for learning by doing. Labs were fun!",
      "user_id": "user456"
    },
    ...
  ],
  "average_difficulty": 7,
  "average_workload": 9,
  "most_common_tags": ["Engaging", "Helpful", "Tough exams"]
}
```

### 3.5 Review Moderation - `/reviews/:id/report` (POST)

**Request**:
```json
{
  "reason": "Inappropriate language",
  "details": "The review includes hate speech."
}
```
**Response**:
```json
{
  "message": "Review has been reported and will be reviewed by moderators."
}
```
