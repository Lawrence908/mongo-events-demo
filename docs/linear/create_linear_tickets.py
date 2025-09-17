#!/usr/bin/env python3
"""
Linear Ticket Creator for MongoDB Events Demo
Creates all tickets from the project plan automatically.

Usage:

    Install:
    npm install -g @linear/cli
    
    Get API key
    
    sudo lin new
"""

import time
import requests


class LinearTicketCreator:
    def __init__(self, api_key: str, team_id: str):
        self.api_key = api_key
        self.team_id = team_id
        self.headers = {
            "Authorization": api_key,
            "Content-Type": "application/json",
        }
        self.endpoint = "https://api.linear.app/graphql"

        # Cache for labels and projects
        self.labels_cache = {}
        self.projects_cache = {}

    def get_team_id(self) -> str:
        """Get the actual team ID from the team key."""
        query = """
        query GetTeams {
          teams {
            nodes {
              id
              key
              name
            }
          }
        }
        """

        response = requests.post(
            self.endpoint,
            headers=self.headers,
            json={"query": query},
        )

        if response.status_code == 200:
            data = response.json()
            teams = data.get("data", {}).get("teams", {}).get("nodes", [])
            print(f"🔍 Debug - Available teams: {teams}")
            
            for team in teams:
                if team["key"] == self.team_id:
                    print(f"✅ Found team '{self.team_id}' with ID: {team['id']}")
                    return team["id"]
            
            raise Exception(f"Team with key '{self.team_id}' not found")
        else:
            raise Exception(f"Failed to fetch teams: {response.status_code}")

    def get_labels(self) -> dict[str, str]:
        """Fetch all labels and cache them by name."""
        if self.labels_cache:
            return self.labels_cache

        # Get the actual team ID first
        actual_team_id = self.get_team_id()

        # Updated query for current Linear API
        query = """
        query GetLabels($teamId: String!) {
          team(id: $teamId) {
            labels {
              nodes {
                id
                name
              }
            }
          }
        }
        """

        variables = {"teamId": actual_team_id}

        response = requests.post(
            self.endpoint,
            headers=self.headers,
            json={"query": query, "variables": variables},
        )

        if response.status_code == 200:
            data = response.json()
            print(f"🔍 Debug - Full response: {data}")
            
            team_data = data.get("data", {}).get("team", {})
            print(f"🔍 Debug - Team data: {team_data}")
            
            if team_data:
                labels = team_data.get("labels", {}).get("nodes", [])
                print(f"🔍 Debug - Raw labels: {labels}")
                
                self.labels_cache = {label["name"]: label["id"] for label in labels}
                print(f"🔍 Debug - Processed labels cache: {self.labels_cache}")
                print(f"✅ Found {len(self.labels_cache)} labels: {list(self.labels_cache.keys())}")
                return self.labels_cache
            else:
                print("❌ Debug - No team data found in response")
                raise Exception("Team not found or no access")
        else:
            print(f"❌ Debug - HTTP {response.status_code}: {response.text}")
            raise Exception(f"Failed to fetch labels: {response.status_code}")

    def get_projects(self) -> dict[str, str]:
        """Fetch all projects and cache them by name."""
        if self.projects_cache:
            return self.projects_cache

        # Get the actual team ID first
        actual_team_id = self.get_team_id()

        query = """
        query GetProjects($teamId: String!) {
          team(id: $teamId) {
            projects {
              nodes {
                id
                name
              }
            }
          }
        }
        """

        variables = {"teamId": actual_team_id}

        response = requests.post(
            self.endpoint,
            headers=self.headers,
            json={"query": query, "variables": variables},
        )

        if response.status_code == 200:
            data = response.json()
            print(f"🔍 Debug - Projects response: {data}")
            
            team_data = data.get("data", {}).get("team", {})
            if team_data:
                projects = team_data.get("projects", {}).get("nodes", [])
                print(f"🔍 Debug - Raw projects: {projects}")
                
                self.projects_cache = {
                    project["name"]: project["id"] for project in projects
                }
                print(f"✅ Found {len(self.projects_cache)} projects: {list(self.projects_cache.keys())}")
                return self.projects_cache
            else:
                print("❌ Debug - No team data found in projects response")
                raise Exception("Team not found or no access")
        else:
            print(f"❌ Debug - Projects HTTP {response.status_code}: {response.text}")
            raise Exception(f"Failed to fetch projects: {response.status_code}")

    def create_ticket(
        self,
        title: str,
        description: str,
        priority: int,
        label_names: list[str],
        project_name: str,
        estimated_time: str,
        dependencies: str,
    ) -> str | None:
        """Create a single ticket in Linear."""

        # Get label IDs
        print(f"🔍 Debug - Looking for labels: {label_names}")
        labels = self.get_labels()
        label_ids = []
        for label_name in label_names:
            if label_name in labels:
                label_ids.append(labels[label_name])
                print(f"✅ Found label '{label_name}': {labels[label_name]}")
            else:
                print(f"⚠️ Warning: Label '{label_name}' not found in available labels: {list(labels.keys())}")

        # Get project ID
        print(f"🔍 Debug - Looking for project: {project_name}")
        projects = self.get_projects()
        if project_name not in projects:
            print(f"❌ Error: Project '{project_name}' not found in available projects: {list(projects.keys())}")
            return None

        project_id = projects[project_name]
        print(f"✅ Found project '{project_name}': {project_id}")

        # Create the ticket
        mutation = """
        mutation CreateIssue($input: IssueCreateInput!) {
          issueCreate(input: $input) {
            success
            issue {
              id
              title
              number
            }
            errors {
              message
            }
          }
        }
        """

        variables = {
            "input": {
                "title": title,
                "description": description,
                "priority": priority,
                "labelIds": label_ids,
                "projectId": project_id,
                "teamKey": self.team_id,
            }
        }

        response = requests.post(
            self.endpoint,
            headers=self.headers,
            json={"query": mutation, "variables": variables},
        )

        if response.status_code == 200:
            data = response.json()
            result = data.get("data", {}).get("issueCreate", {})

            if result.get("success"):
                issue = result["issue"]
                print(f"✅ Created: {issue['title']} (#{issue['number']})")
                return issue["id"]
            else:
                errors = result.get("errors", [])
                print(f"❌ Failed to create '{title}': {errors}")
                return None
        else:
            print(f"❌ HTTP error creating '{title}': {response.status_code}")
            return None

    def create_all_tickets(self):
        """Create all tickets from the MongoDB Events Demo project plan."""

        # Ticket definitions from linear-plan.md
        tickets = [
            {
                "title": "Schema finalization and validation",
                "description": "Finalize `events`, `venues`, `users`, `checkins` schemas with JSON Schema validation.\n\n**Acceptance Criteria:**\n- Events collection enforces required fields and GeoJSON structure\n- Coordinate bounds validated\n- `DATABASE_DESIGN.md` matches implemented schema",
                "priority": 1,
                "labels": ["database", "schema"],
                "project": "MongoDB Events Demo",
                "estimated_time": "4h",
                "dependencies": "",
            },
            {
                "title": "Index suite implementation in app/database.py",
                "description": "Ensure all indexes exist: 2dsphere, text, start_date, category+start_date, location+start_date, organizer+start_date, created_at, tags.\n\n**Acceptance Criteria:**\n- `list_indexes` shows all specified indexes\n- Index build idempotent at startup",
                "priority": 1,
                "labels": ["indexing", "performance"],
                "project": "MongoDB Events Demo",
                "estimated_time": "3h",
                "dependencies": "Schema finalization and validation",
            },
            {
                "title": "CRUD services parity and unit tests",
                "description": "Verify create/get/update/delete paths and add unit tests.\n\n**Acceptance Criteria:**\n- Tests cover happy-path and invalid ObjectId\n- Update respects partial updates and timestamps",
                "priority": 1,
                "labels": ["backend", "testing"],
                "project": "MongoDB Events Demo",
                "estimated_time": "4h",
                "dependencies": "Schema finalization and validation",
            },
            {
                "title": "Text search endpoint and scoring",
                "description": "Support `$text` search with `$meta: \"textScore\"` sorting and projection.\n\n**Acceptance Criteria:**\n- `/api/events?q=...` returns results sorted by relevance\n- Includes `score` in response for debugging",
                "priority": 2,
                "labels": ["search", "backend"],
                "project": "MongoDB Events Demo",
                "estimated_time": "3h",
                "dependencies": "Index suite implementation in app/database.py,CRUD services parity and unit tests",
            },
            {
                "title": "Cursor-based pagination for events list",
                "description": "Implement `_id` cursor pagination in service and API responses.\n\n**Acceptance Criteria:**\n- Response contains `next_cursor`, `has_more`\n- Works with category and search filters",
                "priority": 1,
                "labels": ["performance", "backend"],
                "project": "MongoDB Events Demo",
                "estimated_time": "3h",
                "dependencies": "CRUD services parity and unit tests",
            },
            {
                "title": "Weekend window calculation util",
                "description": "Utility to compute Friday 6pm → Sunday 11:59pm in UTC.\n\n**Acceptance Criteria:**\n- Covered by unit tests for boundary conditions",
                "priority": 3,
                "labels": ["utils", "backend"],
                "project": "MongoDB Events Demo",
                "estimated_time": "2h",
                "dependencies": "CRUD services parity and unit tests",
            },
            {
                "title": "Nearby events GeoJSON API",
                "description": "`$geoNear` aggregation with radius and limit returning GeoJSON FeatureCollection.\n\n**Acceptance Criteria:**\n- `/api/events/nearby` returns valid GeoJSON\n- Distance in meters rounded to 2 decimals",
                "priority": 1,
                "labels": ["geo", "api"],
                "project": "MongoDB Events Demo",
                "estimated_time": "3h",
                "dependencies": "Index suite implementation in app/database.py",
            },
            {
                "title": "Weekend near-me discovery API",
                "description": "Combine `$geoNear` with weekend date-range filter.\n\n**Acceptance Criteria:**\n- `/api/events/weekend` responds within target latency on 10k docs",
                "priority": 2,
                "labels": ["geo", "api"],
                "project": "MongoDB Events Demo",
                "estimated_time": "3h",
                "dependencies": "Weekend window calculation util,Nearby events GeoJSON API",
            },
            {
                "title": "Category filter + geo + date compound query",
                "description": "Add optional `category` to geospatial/date queries; verify compound index usage.\n\n**Acceptance Criteria:**\n- Explain shows index usage without collection scan",
                "priority": 2,
                "labels": ["geo", "search"],
                "project": "MongoDB Events Demo",
                "estimated_time": "3h",
                "dependencies": "Index suite implementation in app/database.py,Nearby events GeoJSON API,Weekend near-me discovery API",
            },
            {
                "title": "Map-ready sample page",
                "description": "Simple page integrating map placeholder and fetch from nearby API.\n\n**Acceptance Criteria:**\n- Visual markers for events (can be mocked initially)",
                "priority": 3,
                "labels": ["frontend", "ux"],
                "project": "MongoDB Events Demo",
                "estimated_time": "3h",
                "dependencies": "Nearby events GeoJSON API",
            },
            {
                "title": "Peak times aggregation",
                "description": "`$group` by hour and dayOfWeek with counts.\n\n**Acceptance Criteria:**\n- `/api/analytics` returns top 10 peak buckets",
                "priority": 2,
                "labels": ["analytics"],
                "project": "MongoDB Events Demo",
                "estimated_time": "3h",
                "dependencies": "CRUD services parity and unit tests",
            },
            {
                "title": "Category popularity aggregation",
                "description": "Counts per category; include average `max_attendees`.\n\n**Acceptance Criteria:**\n- Sorted by count desc; includes `avg_attendees`",
                "priority": 2,
                "labels": ["analytics"],
                "project": "MongoDB Events Demo",
                "estimated_time": "2h",
                "dependencies": "CRUD services parity and unit tests",
            },
            {
                "title": "Monthly trends aggregation",
                "description": "Group by year/month and sort ascending.\n\n**Acceptance Criteria:**\n- `/api/analytics` returns monthly series suitable for charting",
                "priority": 3,
                "labels": ["analytics"],
                "project": "MongoDB Events Demo",
                "estimated_time": "2h",
                "dependencies": "CRUD services parity and unit tests",
            },
            {
                "title": "Analytics performance budget",
                "description": "Validate analytics latency on 10k docs; document explain stats.\n\n**Acceptance Criteria:**\n- Each aggregation < 200ms on seeded dataset\n- Notes recorded in `docs/course-report.md`",
                "priority": 3,
                "labels": ["performance", "analytics"],
                "project": "MongoDB Events Demo",
                "estimated_time": "2h",
                "dependencies": "Peak times aggregation,Category popularity aggregation,Monthly trends aggregation",
            },
            {
                "title": "Socket.IO server plumbing",
                "description": "Initialize SocketIO, events and analytics namespaces.\n\n**Acceptance Criteria:**\n- Server boots; client can connect and receive a welcome ping",
                "priority": 1,
                "labels": ["realtime", "backend"],
                "project": "MongoDB Events Demo",
                "estimated_time": "3h",
                "dependencies": "CRUD services parity and unit tests",
            },
            {
                "title": "MongoDB change streams listener",
                "description": "Watch `events` collection; handle insert/update/delete.\n\n**Acceptance Criteria:**\n- Broadcasts `event_created`, `event_updated`, `event_deleted`",
                "priority": 1,
                "labels": ["realtime", "database"],
                "project": "MongoDB Events Demo",
                "estimated_time": "4h",
                "dependencies": "Socket.IO server plumbing",
            },
            {
                "title": "Location/category rooms",
                "description": "Allow joining rooms keyed by location window or category; prepare for scoped broadcasts.\n\n**Acceptance Criteria:**\n- Join/leave acknowledge events; room naming stable",
                "priority": 2,
                "labels": ["realtime"],
                "project": "MongoDB Events Demo",
                "estimated_time": "3h",
                "dependencies": "MongoDB change streams listener",
            },
            {
                "title": "Real-time demo page",
                "description": "`/realtime` page shows feed of new/updated/deleted events and analytics pings.\n\n**Acceptance Criteria:**\n- Manual test: creating an event triggers client update",
                "priority": 3,
                "labels": ["frontend", "realtime"],
                "project": "MongoDB Events Demo",
                "estimated_time": "3h",
                "dependencies": "Socket.IO server plumbing,MongoDB change streams listener,Location/category rooms",
            },
            {
                "title": "10k events generator",
                "description": "Generate realistic events across US cities; JSON export.\n\n**Acceptance Criteria:**\n- `test_events.json` generated; passes JSON validation",
                "priority": 1,
                "labels": ["data", "tooling"],
                "project": "MongoDB Events Demo",
                "estimated_time": "3h",
                "dependencies": "Schema finalization and validation",
            },
            {
                "title": "Import + seed script docs",
                "description": "Instructions for `mongoimport` and environment.\n\n**Acceptance Criteria:**\n- README section with exact commands",
                "priority": 2,
                "labels": ["docs", "tooling"],
                "project": "MongoDB Events Demo",
                "estimated_time": "1h",
                "dependencies": "10k events generator",
            },
            {
                "title": "Performance harness",
                "description": "`test_performance.py` measures inserts, queries, aggregations, pagination.\n\n**Acceptance Criteria:**\n- Console summary and per-test timings; explain snapshots saved to disk",
                "priority": 2,
                "labels": ["testing", "performance"],
                "project": "MongoDB Events Demo",
                "estimated_time": "4h",
                "dependencies": "10k events generator",
            },
            {
                "title": "Baseline performance report",
                "description": "Capture baseline metrics and include in `docs/course-report.md`.\n\n**Acceptance Criteria:**\n- Table of p50/p95 latencies per workload",
                "priority": 2,
                "labels": ["docs", "performance"],
                "project": "MongoDB Events Demo",
                "estimated_time": "3h",
                "dependencies": "Performance harness",
            },
            {
                "title": "Booking flow design",
                "description": "Specify multi-document transaction steps for ticket booking.\n\n**Acceptance Criteria:**\n- Sequence diagram + pseudo code; failure modes listed",
                "priority": 2,
                "labels": ["design", "transactions"],
                "project": "MongoDB Events Demo",
                "estimated_time": "3h",
                "dependencies": "Schema finalization and validation,CRUD services parity and unit tests",
            },
            {
                "title": "Booking API (transactional)",
                "description": "Implement transaction: check capacity → decrement → create check-in.\n\n**Acceptance Criteria:**\n- Rollback on error; idempotent retry strategy noted",
                "priority": 2,
                "labels": ["backend", "transactions"],
                "project": "MongoDB Events Demo",
                "estimated_time": "6h",
                "dependencies": "Booking flow design",
            },
            {
                "title": "Contention tests on seat inventory",
                "description": "Simulate concurrent bookings; measure conflicts and throughput.\n\n**Acceptance Criteria:**\n- Results table and discussion in course report",
                "priority": 3,
                "labels": ["testing", "performance"],
                "project": "MongoDB Events Demo",
                "estimated_time": "4h",
                "dependencies": "Booking API (transactional)",
            },
            {
                "title": "Input validation & error handling audit",
                "description": "Consistent error messages; Pydantic validations enforced on all APIs.\n\n**Acceptance Criteria:**\n- 4xx vs 5xx semantics correct; helpful error payloads",
                "priority": 2,
                "labels": ["quality", "security"],
                "project": "MongoDB Events Demo",
                "estimated_time": "3h",
                "dependencies": "CRUD services parity and unit tests",
            },
            {
                "title": "Linting and formatting CI (local/script)",
                "description": "Ensure ruff/black run clean; pre-commit or script documented.\n\n**Acceptance Criteria:**\n- Zero warnings; command documented in README",
                "priority": 3,
                "labels": ["devx"],
                "project": "MongoDB Events Demo",
                "estimated_time": "2h",
                "dependencies": "",
            },
            {
                "title": "Configuration hardening",
                "description": "`.env` handling, required vars, non-default secrets for production profile.\n\n**Acceptance Criteria:**\n- App fails fast when critical env vars missing in prod mode",
                "priority": 3,
                "labels": ["security", "ops"],
                "project": "MongoDB Events Demo",
                "estimated_time": "2h",
                "dependencies": "",
            },
            {
                "title": "API documentation snapshot",
                "description": "Document available endpoints, params, sample responses.\n\n**Acceptance Criteria:**\n- `docs/api.md` created with examples and curl snippets",
                "priority": 3,
                "labels": ["docs", "api"],
                "project": "MongoDB Events Demo",
                "estimated_time": "2h",
                "dependencies": "",
            },
            {
                "title": "Final write-up and presentation assets",
                "description": "Summarize outcomes: benchmarks, design decisions, trade-offs; slides or outline.\n\n**Acceptance Criteria:**\n- `docs/course-report.md` updated; final metrics and reflections included",
                "priority": 2,
                "labels": ["docs"],
                "project": "MongoDB Events Demo",
                "estimated_time": "4h",
                "dependencies": "Baseline performance report,Contention tests on seat inventory,Input validation & error handling audit,Linting and formatting CI (local/script),Configuration hardening,API documentation snapshot",
            },
        ]

        print(f"🚀 Creating {len(tickets)} tickets in Linear...")
        print("=" * 60)

        created_count = 0
        failed_count = 0

        for i, ticket in enumerate(tickets, 1):
            print(f"\n[{i}/{len(tickets)}] Creating: {ticket['title']}")

            ticket_id = self.create_ticket(
                title=ticket["title"],
                description=ticket["description"],
                priority=ticket["priority"],
                label_names=ticket["labels"],
                project_name=ticket["project"],
                estimated_time=ticket["estimated_time"],
                dependencies=ticket["dependencies"],
            )

            if ticket_id:
                created_count += 1
            else:
                failed_count += 1

            # Rate limiting - be nice to Linear's API
            time.sleep(0.5)

        print("\n" + "=" * 60)
        print(f"✅ Successfully created: {created_count} tickets")
        if failed_count > 0:
            print(f"❌ Failed to create: {failed_count} tickets")
        print("🎉 Ticket creation complete!")


def main():
    """Main function to run the ticket creator."""

    print("🎫 Linear Ticket Creator for MongoDB Events Demo")
    print("=" * 50)

    # Get configuration from user
    api_key = input("Enter your Linear API key: ").strip()
    if not api_key:
        print("❌ API key is required!")
        return

    team_id = input("Enter your Linear team ID: ").strip()
    if not team_id:
        print("❌ Team ID is required!")
        return

    print(f"\n🔑 Using API key: {api_key[:8]}...")
    print(f"👥 Using team ID: {team_id}")

    # Confirm before proceeding
    confirm = input("\nProceed with creating all tickets? (y/N): ").strip().lower()
    if confirm != "y":
        print("❌ Cancelled!")
        return

    try:
        creator = LinearTicketCreator(api_key, team_id)
        creator.create_all_tickets()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Make sure:")
        print("   • Your API key is valid")
        print("   • Your team ID is correct")
        print("   • You have permission to create tickets")
        print("   • All labels and projects exist")
        print("   • Project 'MongoDB Events Demo' exists in your team")


if __name__ == "__main__":
    main()
