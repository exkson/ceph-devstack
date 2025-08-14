import os
from pathlib import Path

import pytest

from ceph_devstack import Config
from ceph_devstack.resources.ceph.containers import TestNode


class TestTestnodeContainer:
    @pytest.fixture(scope="class")
    def cls(self):
        return TestNode

    def test_osd_count_is_read_from_env_variable(self, cls: type[TestNode]):
        os.environ["CEPH_OSD_COUNT"] = "3"
        testnode = cls()

        assert testnode.osd_count == 3
        del os.environ["CEPH_OSD_COUNT"]

    def test_config_loads_osd_count(self):
        config = Config()
        config.load(Path(__file__).parent.joinpath("fixtures", "osd_config.toml"))
        assert (
            config["containers"]["testnode"]["osd_count"] == 8
        )  # TODO: Find a way to mock config to make assert on testnode.osd_count

    def test_osd_count_defaults_to_1(self, cls: type[TestNode]):
        testnode = cls()
        assert testnode.osd_count == 1

    def test_devices_property(self, cls: type[TestNode]):
        testnode = cls()
        assert len(testnode.devices) == testnode.osd_count
        for i, device in zip(range(testnode.osd_count), testnode.devices):
            assert testnode.device_name(i) == device

    def test_device_name_returns_correct_name(self, cls: type[TestNode]):
        testnode = cls()
        assert testnode.device_name(0) == "/dev/loop0"
        assert testnode.device_name(1) == "/dev/loop1"
        assert testnode.device_name(2) == "/dev/loop2"

    def test_device_name_on_multiple_testnodes(self, cls: type[TestNode]):
        testnode = cls("testnode_1")

        assert testnode.device_name(0) == "/dev/loop10"
        assert testnode.device_name(1) == "/dev/loop11"
        assert testnode.device_name(2) == "/dev/loop12"

    def test_testnode_create_cmd_includes_devices(self, cls: type[TestNode]):
        osd_count = 3
        os.environ["CEPH_OSD_COUNT"] = str(osd_count)
        testnode = cls("testnode_1")
        cmd = testnode.create_cmd

        assert "--device=/dev/loop10" in cmd
        assert "--device=/dev/loop11" in cmd
        assert "--device=/dev/loop12" in cmd
