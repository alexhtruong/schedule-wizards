
# Concurrency V4
### With Alex Truong, Kyle Lin, and Colin Hassett


## Complex Endpoints

Our two complex endpoints are:

GET /departments/{department_abbrev}/statistics
This one has to join together multiple tables in order to find the aggregated statistics
for a certain department. 

and GET /courses/{course_code}/statistics

## Concurrency Control

We mostly are adding data to tables, and don't necessarily update the values within those tables. 
We can experience phantom reads if we call the get department statistics endpoint
while someone else puts in a new review for a course. We may end up getting the old
department course statistics when someone has inputted a new course. 
