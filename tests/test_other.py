def test_version_is_correct():
    import configparser
    from pathlib import Path
    import dppd_plotnine

    c = configparser.ConfigParser()
    c.read(Path(__file__).parent.parent / "setup.cfg")
    version = c["metadata"]["version"]
    assert version == dppd_plotnine.__version__
