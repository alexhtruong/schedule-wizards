
# CSC 365 Proposal
### With Alex Truong, Aaron Krimer, Kyle Lin, and Colin Hassett
We’re building a Class Review API to give Cal Poly students a structured, insightful platform for sharing feedback on courses and professors. Unlike typical review systems, this API captures quantitative and qualitative data such as difficulty level, estimated weekly workload, usefulness of the course material, project vs. exam focus, and collaboration requirements. Students will be able to tag courses with descriptors like “heavy reading,” “great for internships,” or “group projects,” making reviews easier to search and filter.

The relational database will store relationships between users, courses, professors, and structured review fields, enabling aggregated insights like average difficulty or workload by course and professor over time. Reviews can be tied to specific academic terms, supporting time-based analysis (e.g., how a course changes from one instructor to another). The system will include full CRUD operations for reviews, users, professors, and course metadata.
###

### Database ER Diagram: https://lucid.app/lucidchart/9f414bfc-15ce-475f-acac-38fbecc21834/edit?invitationId=inv_a562e2ce-681e-447b-91fb-fd9ec0f97fb9&page=0_0#

## Local Development & Testing

To run your server locally:

1. **Install Dependencies**
    - [Install uv](https://docs.astral.sh/uv/getting-started/installation/)
    - Run:
   ```bash
   uv sync
   ```

2. **Setup local database**
   - Install Docker and Docker CLI if you don't already have it.
   - Run the following command in your terminal:
     ```bash
     docker run --name schedule-wizards -e POSTGRES_USER=myuser -e POSTGRES_PASSWORD=mypassword -e POSTGRES_DB=mydatabase -p 5432:5432 -d postgres:latest
     ```
    - In the future, you can restart the container by just running:
      ```bash
      docker start schedule-wizards
      ```
    - Upgrade the database to your latest schema:
      ```bash
      uv run alembic upgrade head
      ```

   - Download and install [TablePlus](https://tableplus.com/) or [DBeaver](https://dbeaver.io/). Any SQL editor compatible with postgres will work.
   - Create a new connection with the following connection string:
     ```bash
     postgresql://myuser:mypassword@localhost:5432/mydatabase
     ```
   - This will let you query your database and debug issues.


3. **Run the Server**
   ```bash
   uv run main.py
   ```
