import os
import json
import pytest
from pathlib import Path

from yampa.openai.events import ConversationItem
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
async def test_opanai():
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
