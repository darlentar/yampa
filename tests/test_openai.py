import os
import json
import pytest
from pathlib import Path

from yampa.openai.events import ConversationItem, AudioTranscriptDelta
from yampa.openai.processors import FakeOpenAI


def load_scenario(scenario_name: str) -> list[str]:
    steps = []
    scneario_dir = Path(__file__).resolve().parent / Path(f"scenarios/{scenario_name}")
    files = os.listdir(scneario_dir)
    for f in sorted(files, key=lambda f: f):
        with open(scneario_dir / f) as file:
            steps.append(json.load(file))
    return steps


@pytest.mark.asyncio
async def test_opanai_on_item_create():
    scenario = load_scenario("ask_order")
    received_items = []

    async def on_item_created(item: ConversationItem):
        received_items.append(item.item.id)

    openai = FakeOpenAI(
        events=scenario,
        on_item_created=on_item_created,
    )
    await openai.run()

    assert received_items == [
        "item_AIK0wpoIes7XyDYXRDYu4",
        "item_AIK0wRecrZqZlLV2oUVja",
    ]


@pytest.mark.asyncio
async def test_opanai_on_transcript_delta():
    scenario = load_scenario("ask_order")
    received_items = []

    async def on_transcript_delta(delta: AudioTranscriptDelta):
        received_items.append((delta.item_id, delta.delta))

    openai = FakeOpenAI(
        events=scenario,
        on_transcript_delta=on_transcript_delta,
    )
    await openai.run()

    assert len(received_items) == 21
    assert received_items[:5] == [
        (
            "item_AIK0wRecrZqZlLV2oUVja",
            "I",
        ),
        (
            "item_AIK0wRecrZqZlLV2oUVja",
            " can",
        ),
        (
            "item_AIK0wRecrZqZlLV2oUVja",
            " help",
        ),
        (
            "item_AIK0wRecrZqZlLV2oUVja",
            " with",
        ),
        (
            "item_AIK0wRecrZqZlLV2oUVja",
            " that",
        ),
    ]
