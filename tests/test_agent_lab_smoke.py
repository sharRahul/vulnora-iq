from webui import agent_lab


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
