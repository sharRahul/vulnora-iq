from pathlib import Path

from webui import agent_lab

ROOT = Path(__file__).resolve().parents[1]


def test_project_id_accepts_real_names():
    assert agent_lab.normalise_project_id("realagent") == "realagent"


def test_project_id_rejects_fixture_terms():
    for name in ["demo-agent", "mock-agent", "fake-agent", "fixture-agent"]:
        try:
            agent_lab.normalise_project_id(name)
        except ValueError:
            continue
        raise AssertionError(name)


def test_provider_env_maps_local_model():
    env = agent_lab._provider_env({"kind": "custom_env", "base_url": "http://localhost:9000/v1", "model": "local-model"})
    assert env["OPENAI_BASE_URL"] == "http://localhost:9000/v1"
    assert env["MODEL"] == "local-model"


def test_agent_lab_static_ui_supports_local_folder_upload():
    html = (ROOT / "webui" / "static" / "agent-lab" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "webui" / "static" / "agent-lab" / "app.js").read_text(encoding="utf-8")

    assert "data-tab=\"folder\"" in html
    assert "id=\"folder-form\"" in html
    assert "webkitdirectory" in html
    assert "./agent-lab/projects/" in html
    assert "makeStoredZip" in js
    assert "importFolder" in js
    assert "/api/agent-lab/import/archive" in js
