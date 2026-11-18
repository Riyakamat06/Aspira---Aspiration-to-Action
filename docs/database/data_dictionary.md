# Aspira – Data Dictionary (M1 Database)

Owner: Ananya. PK = primary key. FK = foreign key. Dates are stored as UTC.

## users
| Column | Type | Rules |
|---|---|---|
| id | integer | PK |
| full_name | text (100) | required |
| email | text (255) | required, unique |
| hashed_password | text (255) | required; hash only, never the real password |
| created_at | datetime | set automatically |

## dreams
| Column | Type | Rules |
|---|---|---|
| id | integer | PK |
| user_id | integer | FK to users.id, delete cascade |
| title | text (200) | required |
| description | text | optional |
| status | text (20) | default "active" |
| created_at | datetime | set automatically |

## roadmaps
| Column | Type | Rules |
|---|---|---|
| id | integer | PK |
| dream_id | integer | FK to dreams.id, delete cascade |
| title | text (200) | required |
| summary | text | optional |
| source | text (20) | "ai" or "user", default "ai" |
| created_at | datetime | set automatically |

## milestones
| Column | Type | Rules |
|---|---|---|
| id | integer | PK |
| roadmap_id | integer | FK to roadmaps.id, delete cascade |
| title | text (200) | required |
| description | text | optional |
| order_index | integer | position in the roadmap, default 0 |
| target_date | date | optional |

## tasks
| Column | Type | Rules |
|---|---|---|
| id | integer | PK |
| milestone_id | integer | FK to milestones.id, delete cascade |
| title | text (200) | required |
| task_type | text (20) | project, course, learning or practical |
| status | text (20) | pending, submitted, completed or overdue; default "pending" |
| due_date | date | required |

## journal_entries
| Column | Type | Rules |
|---|---|---|
| id | integer | PK |
| user_id | integer | FK to users.id, delete cascade |
| dream_id | integer | FK to dreams.id, optional, set empty on delete |
| content | text | required |
| created_at | datetime | set automatically |

## chat_messages
| Column | Type | Rules |
|---|---|---|
| id | integer | PK |
| user_id | integer | FK to users.id, delete cascade |
| dream_id | integer | FK to dreams.id, optional, set empty on delete |
| role | text (20) | "user" or "assistant" |
| content | text | required |
| created_at | datetime | set automatically |

## progress_snapshots
| Column | Type | Rules |
|---|---|---|
| id | integer | PK |
| user_id | integer | FK to users.id, delete cascade |
| dream_id | integer | FK to dreams.id, delete cascade |
| week_start | date | Monday of the week |
| tasks_completed | integer | default 0 |
| tasks_total | integer | default 0 |

## Open points for the team
- `task_type` and `status` values are checked in Sonali's schema and `constants.py`, not in the database.
- `due_date` on tasks is required because `TaskCreate` requires it.
- SQLite or PostgreSQL is not final. Only `db/session.py` would change.