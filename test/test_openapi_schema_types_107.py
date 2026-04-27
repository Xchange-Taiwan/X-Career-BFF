"""Regression tests for issue #107 — OpenAPI spec types.

These tests dump the JSON schema for each affected Pydantic model and
assert the parts the FE generated types depend on:

1. ExperienceVO/DTO.mentor_experiences_metadata    -> object with
   additionalProperties: True (so the FE generated type is
   Record<string, unknown>, not Record<string, never>).
2. TimeSlotDTO.dt_type                             -> enum {ALLOW, FORBIDDEN}.
3. MentorScheduleSegmentVO.dt_type                 -> enum
   {ALLOW, FORBIDDEN, BOOKED, PENDING}.
4. UpdateReservationDTO.messages                   -> array of typed
   ReservationMessageDTO objects.
5. UpdateReservationDTO.previous_reserve           -> typed
   PreviousReserveRef object reference.
"""

from __future__ import annotations


def _resolve_ref(schema: dict, ref: str) -> dict:
    """Resolve a local '#/$defs/Foo' or '#/components/schemas/Foo' ref."""
    parts = ref.lstrip("#/").split("/")
    node = schema
    for part in parts:
        node = node[part]
    return node


def test_experience_models_metadata_is_open_object():
    from src.domain.mentor.model.experience_model import (
        ExperienceDTO,
        ExperienceVO,
    )

    for model in (ExperienceDTO, ExperienceVO):
        schema = model.model_json_schema()
        meta = schema["properties"]["mentor_experiences_metadata"]
        assert meta["type"] == "object", schema
        # Pydantic v2 emits additionalProperties: True for Dict[str, Any].
        # Anything other than False means the schema is open and
        # openapi-typescript renders Record<string, unknown>.
        assert meta.get("additionalProperties") is not False, schema


def test_timeslot_dto_dt_type_is_two_value_enum():
    from src.domain.mentor.model.mentor_model import TimeSlotDTO

    schema = TimeSlotDTO.model_json_schema()
    dt_type = schema["properties"]["dt_type"]
    if "$ref" in dt_type:
        dt_type = _resolve_ref(schema, dt_type["$ref"])
    assert sorted(dt_type["enum"]) == ["ALLOW", "FORBIDDEN"], schema


def test_segment_vo_dt_type_is_full_enum():
    from src.domain.mentor.model.mentor_model import MentorScheduleSegmentVO

    schema = MentorScheduleSegmentVO.model_json_schema()
    dt_type = schema["properties"]["dt_type"]
    if "$ref" in dt_type:
        dt_type = _resolve_ref(schema, dt_type["$ref"])
    assert sorted(dt_type["enum"]) == [
        "ALLOW",
        "BOOKED",
        "FORBIDDEN",
        "PENDING",
    ], schema


def test_update_reservation_messages_are_typed():
    from src.domain.user.model.reservation_model import UpdateReservationDTO

    schema = UpdateReservationDTO.model_json_schema()
    messages = schema["properties"]["messages"]
    # Strip Optional/anyOf wrapping if present.
    if "anyOf" in messages:
        messages = next(
            opt for opt in messages["anyOf"] if opt.get("type") == "array"
        )
    assert messages["type"] == "array", schema
    item = messages["items"]
    if "$ref" in item:
        item = _resolve_ref(schema, item["$ref"])
    props = item["properties"]
    assert "user_id" in props and "content" in props, schema
    assert props["user_id"]["type"] == "integer", schema
    assert props["content"]["type"] == "string", schema


def test_update_reservation_has_previous_reserve_typed():
    from src.domain.user.model.reservation_model import UpdateReservationDTO

    schema = UpdateReservationDTO.model_json_schema()
    assert "previous_reserve" in schema["properties"], schema
    prev = schema["properties"]["previous_reserve"]
    if "anyOf" in prev:
        prev = next(opt for opt in prev["anyOf"] if "$ref" in opt or opt.get("type") == "object")
    if "$ref" in prev:
        prev = _resolve_ref(schema, prev["$ref"])
    assert prev["type"] == "object", schema
    assert "reserve_id" in prev["properties"], schema
