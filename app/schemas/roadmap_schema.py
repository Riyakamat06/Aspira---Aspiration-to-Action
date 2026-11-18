"""
roadmap_schema.py - data shapes for a roadmap and its milestones.

PURPOSE
    Defines how a roadmap is sent to the website: the roadmap itself,
    its milestones in order, and the tasks inside each milestone. The
    shape follows the SRS data model (sections 3.x and 4.2):
        Roadmap   -> source (generated or user-created), version, disclaimer flag
        Milestone -> title, order, completion percentage
        Task      -> reuses TaskResponse from task_schema.py (FR-RG-05)

SCHEMAS
    MilestoneResponse -> one milestone with its tasks
    RoadmapResponse   -> one roadmap with its milestones

WHO USES IT
    - roadmap_router.py and roadmap_generator.py (Riya) build and return it
    - Tanushree's roadmapApi.js, RoadmapPage and MilestoneCard read it

NOTES
    - disclaimer is True for medical, legal and other regulated fields,
      so the website shows the "educational guidance, not professional
      advice" banner (SRS FR-RG-08).
    - Field names must match Ananya's Roadmap and Milestone models.
      These names were written from the SRS and must be confirmed with
      Riya and Ananya.
    - Resources per task (FR-RES) are not included yet; they are "Later".
"""

from datetime import datetime
from typing import Literal                                   # limits a field to fixed words
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.task_schema import TaskResponse             # reuse the task shape


class MilestoneResponse(BaseModel):
    # lets Pydantic read data straight from a database object
    model_config = ConfigDict(from_attributes=True)

    id: int                                        # unique number of the milestone
    title: str                                     # the milestone's name
    order: int                                     # its position in the roadmap (1, 2, 3 ...)
    completion_percent: float = Field(ge=0, le=100)  # how much is done, 0 to 100
    tasks: list[TaskResponse] = []                 # the tasks inside this milestone


class RoadmapResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int                                        # unique number of the roadmap
    dream_id: int                                  # the dream it belongs to
    source: Literal["generated", "user_created"]   # who made it (SRS FR-VAL-04)
    version: int                                   # goes up each time it is regenerated
    disclaimer: bool                               # True for medical or legal careers
    created_at: datetime                           # when it was made
    milestones: list[MilestoneResponse] = []       # milestones, in order