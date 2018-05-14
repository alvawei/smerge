def test_find_best_app(test_apps):
    """Test of find_best_app."""
    class mod:
        app = Flask('appname')
    assert find_best_app(mod) == mod.app

    class mod: