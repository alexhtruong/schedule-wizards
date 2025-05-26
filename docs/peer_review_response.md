Issue: There are two Professor and Course base model classes, one in models.py and the other in reviews.py. The one in models has an extra attribute: courses. Having multiple professor classes opens the door to ambiguity and inconsistent data being required if the wrong Professor class is used.

Response: Refactored classes so there shouldn't be any repeats

Issue: Your create_department route checks if the department exists, and then inserts it into the if it doesn’t. If concurrent duplicate calls were made to this route, it could be possible for both select statements to occur simultaneously, and then insert duplicate department entries. You can fix this with a unique constraint on name in the db, and simply check for conflict when attempting to from the route.

Response: Added a check for existing departments and schools with a try/catch block. This way the code won't potentially miss any checks. Also added a composite keys for name to school id and abbrev to school id

Issue: Create_school - same problem as create_department above. Add unique constraint on name and check for conflict on insert.

Response: Added another try/catch block to catch creation of departments at any time. Also added unique constraints on name to school id

Issue: Get_professor_details - The error message for missing reviews doesn’t handle status code convention. 400 indicates client error but in this case the client is not at fault. I think some other status codes don’t follow convention as well

Response: Fixed status codes to follow convention

Issue: Get_professor_details - In the reviews_result query, professor id is fetched. This is unnecessary as professor id is already known from prof_result

Response: removed unnecessary query
