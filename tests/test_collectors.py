from sysrescue.collectors import parse_meminfo, run_read_only


def test_parse_meminfo_extracts_values_in_kib():
    result = parse_meminfo(
        "MemTotal:       16384000 kB\n"
        "MemAvailable:    8192000 kB\n"
        "SwapTotal:             0 kB\n"
    )
    assert result == {
        "MemTotal": 16384000,
        "MemAvailable": 8192000,
        "SwapTotal": 0,
    }


def test_parse_meminfo_ignores_invalid_lines():
    result = parse_meminfo("Not a metric\nCached: unknown kB\n")
    assert result == {}


def test_run_read_only_rejects_empty_command():
    assert run_read_only([]) is None
