# Manual Test Results V2

## 1. The Transfer Student's Course Planning Journey

Maya is a transfer student who needs to efficiently plan her upcoming quarters. She wants to maximize her chances of success while managing her workload carefully across multiple engineering courses.

### 1.1 List Courses Sorted by Workload

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
        "course_id": 1,
        "name": "Data Structures",
        "department": "CSC",
        "professors": [
            {
                "id": "1",
                "name": "Lucas Pierce",
                "department": "CSC",
                "num_reviews": 0,
                "courses": []
            }
        ]
    },
    {
        "course_id": 2,
        "name": "Introduction to Computer Organization",
        "department": "CPE",
        "professors": []
    },
    {
        "course_id": 3,
        "name": "Intro to Database Systems",
        "department": "CSC",
        "professors": []
    },
    {
        "course_id": 4,
        "name": "methods of ethnicity",
        "department": "ES",
        "professors": []
    }
]
```

### 1.2 Get Course Statistics

**Request (ME211):**

```bash
curl -X 'GET' \
  'https://schedule-wizards.onrender.com/courses/ME211/statistics' \
  -H 'accept: application/json'
```

**Response:**

```json
{
  "average_rating": 3,
  "average_difficulty": 3,
  "average_workload": 17.5,
  "total_reviews": 2,
  "top_tags": [
    "boring",
    "fun",
    "lame"
  ]
}
```

**Request (ME212):**

```bash
curl -X 'GET' \
  'https://schedule-wizards.onrender.com/courses/ME212/statistics' \
  -H 'accept: application/json'
```

**Response:**

```json
{
    "average_rating": 4,
  "average_difficulty": 3,
  "average_workload": 20,
  "total_reviews": 1,
  "top_tags": [
    "fun"
  ]
}
```

**Request (CE201):**

```bash
curl -X 'GET' \
  'https://schedule-wizards.onrender.com/courses/CE201/statistics' \
  -H 'accept: application/json'
```

**Response:**

```json
{
  "average_rating": 1,
  "average_difficulty": 1,
  "average_workload": 10,
  "total_reviews": 1,
  "top_tags": [
    "bad"
  ]
}
```

### 1.3 Get Professor Details

**Request (Prof. Hall):**

```bash
curl -X 'GET' \
  'https://schedule-wizards.onrender.com/professors/Ashton%20Hall' \
  -H 'accept: application/json'
```

**Response:**

```json
{
  "professor": {
    "id": "1",
    "name": "Prof. Hall",
    "department": "ME",
    "num_reviews": 28,
    "courses": [
      {
        "course_id": 1,
        "name": "Mechanics I",
        "department": "ME"
      }
    ]
  },
  "reviews": [
    {
      "review_id": 123,
      "course": {
        "course_id": 1,
        "name": "Mechanics I",
        "department": "ME"
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

### 1.4 Create Review

**Request:**

```bash
curl -X 'POST' \
  'https://schedule-wizards.onrender.com/reviews' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "course_id": 1,
    "professor_id": 1,
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

## 2. The Department Chair's Curriculum Review

### 2.1 List ME Department Courses

**Request:**

```bash
curl -X 'GET' \
  'https://schedule-wizards.onrender.com/courses?department=ME' \
  -H 'accept: application/json'
```

**Response:**

```json
[
  {
    "course_id": 1,
    "name": "Mechanics I",
    "department": "ME",
    "professors": [
      {
        "id": "1",
        "name": "Prof. Hall",
        "department": "ME",
        "num_reviews": 28
      },
      {
        "id": "2",
        "name": "Prof. Johnson",
        "department": "ME",
        "num_reviews": 22
      }
    ]
  },
  {
    "course_id": 2,
    "name": "Mechanics II",
    "department": "ME",
    "professors": [
      {
        "id": "3",
        "name": "Prof. Williams",
        "department": "ME",
        "num_reviews": 15
      }
    ]
  },
  {
    "course_id": 4,
    "name": "ME304 - Advanced Dynamics",
    "department": "ME",
    "professors": [
      {
        "id": "6",
        "name": "Prof. Smith",
        "department": "ME",
        "num_reviews": 25
      }
    ]
  }
]
```

### 2.2 Get ME304 Course Statistics

**Request:**

```bash
curl -X 'GET' \
  'https://schedule-wizards.onrender.com/courses/ME304/statistics' \
  -H 'accept: application/json'
```

**Response:**

```json
{
  "average_rating": 2.8,
  "average_difficulty": 4.8,
  "average_workload": 22.0,
  "total_reviews": 42,
  "top_tags": ["very-difficult", "heavy-workload", "needs-prerequisites"]
}
```

### 2.3 Get ME304 Professors

**Request:**

```bash
curl -X 'GET' \
  'https://schedule-wizards.onrender.com/courses/ME304/professors' \
  -H 'accept: application/json'
```

**Response:**

```json
[
  {
    "id": "6",
    "name": "Prof. Smith",
    "department": "ME",
    "num_reviews": 25,
    "courses": [
      {
        "course_id": 4,
        "name": "ME304 - Advanced Dynamics",
        "department": "ME"
      }
    ]
  }
]
```

### 2.4 Create New Professor

**Request:**

```bash
curl -X 'POST' \
  'https://schedule-wizards.onrender.com/professors' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Prof. Anderson",
    "department": "ME"
  }'
```

**Response:**

```json
{
  "id": "7",
  "message": "Professor created successfully"
}
```

### 2.5 Create New Course

**Request:**

```bash
curl -X 'POST' \
  'https://schedule-wizards.onrender.com/courses' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "course_code": "ME305",
    "name": "Engineering Analysis",
    "department": "ME"
  }'
```

**Response:**

```json
{
  "course_id": 5,
  "name": "Engineering Analysis",
  "department": "ME",
  "professors": []
}
```

## 3. Student Course Guide Project

### 3.1 List All Courses Sorted by Rating

**Request:**

```bash
curl -X 'GET' \
  'https://schedule-wizards.onrender.com/courses?sort=rating&order=desc' \
  -H 'accept: application/json'
```

**Response:**

```json
[
  {
    "course_id": 2,
    "name": "Mechanics II",
    "department": "ME",
    "professors": [
      {
        "id": "3",
        "name": "Prof. Williams",
        "department": "ME",
        "num_reviews": 15
      }
    ]
  },
  {
    "course_id": 1,
    "name": "Mechanics I",
    "department": "ME",
    "professors": [
      {
        "id": "1",
        "name": "Prof. Hall",
        "department": "ME",
        "num_reviews": 28
      },
      {
        "id": "2",
        "name": "Prof. Johnson",
        "department": "ME",
        "num_reviews": 22
      }
    ]
  },
  {
    "course_id": 3,
    "name": "Statics",
    "department": "CE",
    "professors": [
      {
        "id": "4",
        "name": "Prof. Chen",
        "department": "CE",
        "num_reviews": 18
      },
      {
        "id": "5",
        "name": "Prof. Rodriguez",
        "department": "CE",
        "num_reviews": 12
      }
    ]
  },
  {
    "course_id": 4,
    "name": "ME304 - Advanced Dynamics",
    "department": "ME",
    "professors": [
      {
        "id": "6",
        "name": "Prof. Smith",
        "department": "ME",
        "num_reviews": 25
      }
    ]
  }
]
```

### 3.2 Get Detailed Professor Statistics

**Request:**

```bash
curl -X 'GET' \
  'https://schedule-wizards.onrender.com/professors/Andrew%20Williams' \
  -H 'accept: application/json'
```

**Response:**

```json
{
  "professor": {
    "id": "3",
    "name": "Andrew Williams",
    "department": "ME",
    "num_reviews": 15,
    "courses": [
      {
        "course_id": 2,
        "name": "Mechanics II",
        "department": "ME"
      }
    ]
  },
  "reviews": [
    {
      "review_id": 234,
      "course": {
        "course_id": 2,
        "name": "Mechanics II",
        "department": "ME"
      },
      "term": "Winter 2025",
      "difficulty_rating": 3,
      "overall_rating": 4.5,
      "workload_estimate": 12,
      "tags": ["clear-lectures", "engaging", "fair-grading"],
      "comments": "One of the best professors I've had. Makes complex topics accessible."
    }
  ],
  "average_difficulty": 3.5,
  "average_workload": 12.0,
  "most_common_tags": ["clear-lectures", "engaging", "fair-grading", "helpful"]
}
```

### 3.3 Create Detailed Course Review

**Request:**

```bash
curl -X 'POST' \
  'https://schedule-wizards.onrender.com/reviews' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "course_id": 2,
    "professor_id": 3,
    "term": "Spring 2025",
    "difficulty_rating": 3,
    "overall_rating": 5,
    "workload_estimate": 12,
    "tags": ["engaging", "clear-lectures", "practical-examples"],
    "comments": "Prof. Williams makes ME212 engaging and practical. Taking ME211 with Prof. Hall beforehand really helped prepare for this course."
  }'
```

**Response:**

```json
{
  "id": "457",
  "message": "Review created successfully"
}
```
