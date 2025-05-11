# Example Workflow

Maya is a transfer student who needs to efficiently plan her upcoming quarters. She wants to maximize her chances of success while managing her workload carefully across multiple engineering courses.

First, Maya calls GET `/courses?sort=workload&order=asc` to find all engineering foundation courses, sorted by workload. She identifies three crucial courses: ME211, ME212, and CE201.

For each course, Maya:

1. Calls GET `/courses/{id}/statistics` to understand the overall picture:
   - ME211: 3.8/5 rating, 15hrs/week average workload
   - ME212: 4.1/5 rating, 12hrs/week average workload
   - CE201: 3.2/5 rating, 18hrs/week average workload

2. Uses GET `/courses/{id}/professors` for each course to find professors teaching next quarter:
   - ME211: Prof. Hall and Prof. Johnson
   - ME212: Prof. Williams
   - CE201: Prof. Chen and Prof. Rodriguez

3. Calls GET `/professors/{id}` for each professor to deep dive into their teaching styles and student experiences

After thorough research, Maya:
1. Creates a new review via POST `/reviews` with detailed feedback
2. Adds a new professor using POST `/professors`

# Testing Results
### 2. Get All Courses
**Request:**
```bash
curl -X 'GET' \
  'https://schedule-wizards.onrender.com/courses?sort=workload&order=asc' \
  -H 'accept: application/json'
```
**Response:**
```json
[
  {
    "course_id": "ME212",
    "name": "Mechanics II",
    "department": "ME",
    "professors": [
      {
        "name": "Prof. Williams",
        "professor_id": 3
      }
    ]
  },
  {
    "course_id": "ME211",
    "name": "Mechanics I",
    "department": "ME",
    "professors": [
      {
        "name": "Prof. Hall",
        "professor_id": 1
      },
      {
        "name": "Prof. Johnson",
        "professor_id": 2
      }
    ]
  },
  {
    "course_id": "CE201",
    "name": "Statics",
    "department": "CE",
    "professors": [
      {
        "name": "Prof. Chen",
        "professor_id": 4
      },
      {
        "name": "Prof. Rodriguez",
        "professor_id": 5
      }
    ]
  }
]
```

### 2. Get Course Statistics (ME211)
**Request:**
```bash
curl -X 'GET' \
  'https://schedule-wizards.onrender.com/courses/ME211/statistics' \
  -H 'accept: application/json'
```
**Response:**
```json
{
  "average_rating": 3.8,
  "average_difficulty": 4.2,
  "average_workload": 15.0,
  "total_reviews": 45,
  "top_tags": ["challenging", "time-consuming", "well-organized"]
}
```

### 3. Get Course Professors (ME211)
**Request:**
```bash
curl -X 'GET' \
  'https://schedule-wizards.onrender.com/courses/ME211/professors' \
  -H 'accept: application/json'
```
**Response:**
```json
[
  {
    "name": "Prof. Hall",
    "professor_id": 1
  },
  {
    "name": "Prof. Johnson",
    "professor_id": 2
  }
]
```

### 4. Get Professor Details
**Request:**
```bash
curl -X 'GET' \
  'https://schedule-wizards.onrender.com/professors/1' \
  -H 'accept: application/json'
```
**Response:**
```json
{
  "professor": {
    "id": "1",
    "name": "Prof. Hall",
    "department": "ME",
    "num_reviews": 28
  },
  "reviews": [
    {
      "review_id": "123",
      "course": {
        "id": "1",
        "code": "ME211",
        "name": "Mechanics I"
      },
      "term": "Spring 2025",
      "difficulty_rating": 4,
      "overall_rating": 4,
      "workload_estimate": 15,
      "tags": ["clear-lectures", "fair-grading"],
      "comments": "Excellent professor who explains concepts thoroughly"
    }
  ],
  "average_difficulty": 4.2,
  "average_workload": 15.5,
  "most_common_tags": ["clear-lectures", "fair-grading", "helpful"]
}
```

### 5. Create Review
**Request:**
```bash
curl -X 'POST' \
  'https://schedule-wizards.onrender.com/reviews' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "course_id": "ME211",
    "professor_id": "1",
    "professor_name": "Prof. Hall",
    "user_id": "student123",
    "term": "Spring 2025",
    "difficulty_rating": 4,
    "overall_rating": 5,
    "workload_estimate": 15,
    "tags": ["clear-lectures", "fair-grading"],
    "comments": "Professor Hall explains concepts thoroughly and provides great examples."
  }'
```
**Response:**
```json
{
  "id": "456",
  "message": "Review created successfully"
}
```


