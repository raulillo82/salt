"""
    :codeauthor: Jayesh Kariya <jayeshk@saltstack.com>
"""


import datetime
import pytest
import salt.modules.cmdmod
import salt.modules.rpm_lowpkg as rpm
import salt.utils.path
from tests.support.mock import MagicMock, patch

# pylint: disable=unused-import
try:
    import rpm as rpm_lib

    HAS_RPM = True
except ImportError:
    HAS_RPM = False

try:
    import rpm_vercmp

    HAS_PY_RPM = True
except ImportError:
    HAS_PY_RPM = False
# pylint: enable=unused-import


def _called_with_root(mock):
    cmd = " ".join(mock.call_args[0][0])
    return cmd.startswith("rpm --root /")


@pytest.fixture
def configure_loader_modules():
    return {rpm: {"rpm": MagicMock(return_value=MagicMock)}}

def test___virtual___openeuler():
    patch_which = patch("salt.utils.path.which", return_value=True)
    with patch.dict(
        rpm.__grains__, {"os": "openEuler", "os_family": "openEuler"}
    ), patch_which:
        assert rpm.__virtual__() == "lowpkg"


def test___virtual___issabel_pbx():
    patch_which = patch("salt.utils.path.which", return_value=True)
    with patch.dict(
        rpm.__grains__, {"os": "Issabel Pbx", "os_family": "IssabeL PBX"}
    ), patch_which:
        assert rpm.__virtual__() == "lowpkg"


def test___virtual___virtuozzo():
    patch_which = patch("salt.utils.path.which", return_value=True)
    with patch.dict(
        rpm.__grains__, {"os": "virtuozzo", "os_family": "VirtuoZZO"}
    ), patch_which:
        assert rpm.__virtual__() == "lowpkg"


def test___virtual___with_no_rpm():
    patch_which = patch("salt.utils.path.which", return_value=False)
    ret = rpm.__virtual__()
    assert isinstance(ret, tuple)
    assert ret[0] is False



# 'list_pkgs' function tests: 2


def test_list_pkgs():
    """
    Test if it list the packages currently installed in a dict
    """
    mock = MagicMock(return_value="")
    with patch.dict(rpm.__salt__, {"cmd.run": mock}):
        assert rpm.list_pkgs() == {}
        assert not _called_with_root(mock)


def test_list_pkgs_root():
    """
    Test if it list the packages currently installed in a dict,
    called with root parameter
    """
    mock = MagicMock(return_value="")
    with patch.dict(rpm.__salt__, {"cmd.run": mock}):
        rpm.list_pkgs(root="/")
        assert _called_with_root(mock)


# 'verify' function tests: 2


def test_verify():
    """
    Test if it runs an rpm -Va on a system, and returns the
    results in a dict
    """
    mock = MagicMock(
        return_value={"stdout": "", "stderr": "", "retcode": 0, "pid": 12345}
    )
    with patch.dict(rpm.__salt__, {"cmd.run_all": mock}):
        assert rpm.verify("httpd") == {}
        assert not _called_with_root(mock)


def test_verify_root():
    """
    Test if it runs an rpm -Va on a system, and returns the
    results in a dict, called with root parameter
    """
    mock = MagicMock(
        return_value={"stdout": "", "stderr": "", "retcode": 0, "pid": 12345}
    )
    with patch.dict(rpm.__salt__, {"cmd.run_all": mock}):
        rpm.verify("httpd", root="/")
        assert _called_with_root(mock)


# 'file_list' function tests: 2


def test_file_list():
    """
    Test if it list the files that belong to a package.
    """
    mock = MagicMock(return_value="")
    with patch.dict(rpm.__salt__, {"cmd.run": mock}):
        assert rpm.file_list("httpd") == {"errors": [], "files": []}
        assert not _called_with_root(mock)


def test_file_list_root():
    """
    Test if it list the files that belong to a package, using the
    root parameter.
    """

    mock = MagicMock(return_value="")
    with patch.dict(rpm.__salt__, {"cmd.run": mock}):
        rpm.file_list("httpd", root="/")
        assert _called_with_root(mock)


# 'file_dict' function tests: 2


def test_file_dict():
    """
    Test if it list the files that belong to a package
    """
    mock = MagicMock(return_value="")
    with patch.dict(rpm.__salt__, {"cmd.run": mock}):
        assert rpm.file_dict("httpd") == {"errors": [], "packages": {}}
        assert not _called_with_root(mock)


def test_file_dict_root():
    """
    Test if it list the files that belong to a package
    """
    mock = MagicMock(return_value="")
    with patch.dict(rpm.__salt__, {"cmd.run": mock}):
        rpm.file_dict("httpd", root="/")
        assert _called_with_root(mock)


# 'owner' function tests: 1


def test_owner():
    """
    Test if it return the name of the package that owns the file.
    """
    assert rpm.owner() == ""

    ret = "file /usr/bin/salt-jenkins-build is not owned by any package"
    mock = MagicMock(return_value=ret)
    with patch.dict(rpm.__salt__, {"cmd.run_stdout": mock}):
        assert rpm.owner("/usr/bin/salt-jenkins-build") == ""
        assert not _called_with_root(mock)

    ret = {
        "/usr/bin/vim": "vim-enhanced-7.4.160-1.e17.x86_64",
        "/usr/bin/python": "python-2.7.5-16.e17.x86_64",
    }
    mock = MagicMock(
        side_effect=[
            "python-2.7.5-16.e17.x86_64",
            "vim-enhanced-7.4.160-1.e17.x86_64",
        ]
    )
    with patch.dict(rpm.__salt__, {"cmd.run_stdout": mock}):
        assert rpm.owner("/usr/bin/python", "/usr/bin/vim") == ret
        assert not _called_with_root(mock)


def test_owner_root():
    """
    Test if it return the name of the package that owns the file,
    using the parameter root.
    """
    assert rpm.owner() == ""

    ret = "file /usr/bin/salt-jenkins-build is not owned by any package"
    mock = MagicMock(return_value=ret)
    with patch.dict(rpm.__salt__, {"cmd.run_stdout": mock}):
        rpm.owner("/usr/bin/salt-jenkins-build", root="/")
        assert _called_with_root(mock)


# 'checksum' function tests: 2


def test_checksum():
    """
    Test if checksum validate as expected
    """
    ret = {
        "file1.rpm": True,
        "file2.rpm": False,
        "file3.rpm": False,
    }

    mock = MagicMock(side_effect=[True, 0, True, 1, False, 0])
    with patch.dict(rpm.__salt__, {"file.file_exists": mock, "cmd.retcode": mock}):
        assert rpm.checksum("file1.rpm", "file2.rpm", "file3.rpm") == ret
        assert not _called_with_root(mock)


def test_checksum_root():
    """
    Test if checksum validate as expected, using the parameter
    root
    """
    mock = MagicMock(side_effect=[True, 0])
    with patch.dict(rpm.__salt__, {"file.file_exists": mock, "cmd.retcode": mock}):
        rpm.checksum("file1.rpm", root="/")
        assert _called_with_root(mock)


@pytest.mark.parametrize("rpm_lib", ["HAS_RPM", "HAS_PY_RPM", "rpmdev-vercmp"])
def test_version_cmp_rpm_all_libraries(rpm_lib):
    """
    Test package version when each library is installed
    """
    rpmdev = salt.utils.path.which("rpmdev-vercmp")
    patch_cmd = patch.dict(rpm.__salt__, {"cmd.run_all": salt.modules.cmdmod.run_all})
    if rpm_lib == "rpmdev-vercmp":
        if rpmdev:
            patch_rpm = patch("salt.modules.rpm_lowpkg.HAS_RPM", False)
            patch_py_rpm = patch("salt.modules.rpm_lowpkg.HAS_PY_RPM", False)
        else:
            pytest.skip("The rpmdev-vercmp binary is not installed")
    elif rpm_lib == "HAS_RPM":
        if HAS_RPM:
            patch_rpm = patch("salt.modules.rpm_lowpkg.HAS_RPM", True)
            patch_py_rpm = patch("salt.modules.rpm_lowpkg.HAS_PY_RPM", False)
        else:
            pytest.skip("The RPM lib is not installed, skipping")
    elif rpm_lib == "HAS_PY_RPM":
        if HAS_PY_RPM:
            patch_rpm = patch("salt.modules.rpm_lowpkg.HAS_RPM", False)
            patch_py_rpm = patch("salt.modules.rpm_lowpkg.HAS_PY_RPM", True)
        else:
            pytest.skip("The Python RPM lib is not installed, skipping")

    with patch_rpm, patch_py_rpm, patch_cmd:
        assert -1 == rpm.version_cmp("1", "2")
        assert -1 == rpm.version_cmp("2.9.1-6.el7_2.3", "2.9.1-6.el7.4")
        assert 1 == rpm.version_cmp("3.2", "3.0")
        assert 0 == rpm.version_cmp("3.0", "3.0")
        assert 1 == rpm.version_cmp("1:2.9.1-6.el7_2.3", "2.9.1-6.el7.4")
        assert -1 == rpm.version_cmp("1:2.9.1-6.el7_2.3", "1:2.9.1-6.el7.4")
        assert 1 == rpm.version_cmp("2:2.9.1-6.el7_2.3", "1:2.9.1-6.el7.4")
        assert 0 == rpm.version_cmp("3:2.9.1-6.el7.4", "3:2.9.1-6.el7.4")
        assert -1 == rpm.version_cmp("3:2.9.1-6.el7.4", "3:2.9.1-7.el7.4")
        assert 1 == rpm.version_cmp("3:2.9.1-8.el7.4", "3:2.9.1-7.el7.4")


@patch("salt.modules.rpm_lowpkg.HAS_RPM", True)
@patch("salt.modules.rpm_lowpkg.rpm.labelCompare", return_value=-1)
@patch("salt.modules.rpm_lowpkg.log")
def test_version_cmp_rpm(mock_log, mock_labelCompare):
    """
    Test package version if RPM-Python is installed

    :return:
    """
    assert -1 == rpm.version_cmp("1", "2")
    assert not mock_log.warning.called
    assert mock_labelCompare.called


@patch("salt.modules.rpm_lowpkg.HAS_RPM", False)
@patch("salt.modules.rpm_lowpkg.HAS_RPMUTILS", True)
@patch("salt.modules.rpm_lowpkg.HAS_PY_RPM", False)
@patch("salt.modules.rpm_lowpkg.rpmUtils", create=True)
@patch("salt.modules.rpm_lowpkg.log")
def test_version_cmp_rpmutils(mock_log, mock_rpmUtils):
    """
    Test package version if rpmUtils.miscutils called

    :return:
    """
    mock_rpmUtils.miscutils = MagicMock()
    mock_rpmUtils.miscutils.compareEVR = MagicMock(return_value=-1)
    assert -1 == rpm.version_cmp("1", "2")
    assert mock_log.warning.called
    assert mock_rpmUtils.miscutils.compareEVR.called
    assert (
        mock_log.warning.mock_calls[0][1][0]
        == "Please install a package that provides rpm.labelCompare for more accurate version comparisons."
    )


@patch("salt.modules.rpm_lowpkg.HAS_RPM", False)
@patch("salt.modules.rpm_lowpkg.HAS_RPMUTILS", False)
@patch("salt.modules.rpm_lowpkg.HAS_PY_RPM", False)
@patch("salt.utils.path.which", return_value=True)
@patch("salt.modules.rpm_lowpkg.log")
def test_version_cmp_rpmdev_vercmp(mock_log, mock_which):
    """
    Test package version if rpmdev-vercmp is installed

    :return:
    """
    mock__salt__ = MagicMock(return_value={"retcode": 12})
    with patch.dict(rpm.__salt__, {"cmd.run_all": mock__salt__}):
        assert -1 == rpm.version_cmp("1", "2")
        assert mock__salt__.called
        assert mock_log.warning.called
        assert (
            mock_log.warning.mock_calls[0][1][0]
            == "Please install a package that provides rpm.labelCompare for more accurate version comparisons."
        )
        assert (
            mock_log.warning.mock_calls[1][1][0]
            == "Installing the rpmdevtools package may surface dev tools in production."
        )


@patch("salt.modules.rpm_lowpkg.HAS_RPM", False)
@patch("salt.modules.rpm_lowpkg.HAS_RPMUTILS", False)
@patch("salt.modules.rpm_lowpkg.HAS_PY_RPM", False)
@patch("salt.utils.versions.version_cmp", return_value=-1)
@patch("salt.utils.path.which", return_value=False)
@patch("salt.modules.rpm_lowpkg.log")
def test_version_cmp_python(mock_log, mock_which, mock_version_cmp):
    """
    Test package version if falling back to python

    :return:
    """
    assert -1 == rpm.version_cmp("1", "2")
    assert mock_version_cmp.called
    assert mock_log.warning.called
    assert (
        mock_log.warning.mock_calls[0][1][0]
        == "Please install a package that provides rpm.labelCompare for more accurate version comparisons."
    )
    assert (
        mock_log.warning.mock_calls[1][1][0]
        == "Falling back on salt.utils.versions.version_cmp() for version comparisons"
    )


def test_list_gpg_keys_no_info():
    """
    Test list_gpg_keys with no extra information
    """
    mock = MagicMock(return_value="\n".join(["gpg-pubkey-1", "gpg-pubkey-2"]))
    with patch.dict(rpm.__salt__, {"cmd.run_stdout": mock}):
        assert rpm.list_gpg_keys() == ["gpg-pubkey-1", "gpg-pubkey-2"]
        assert not _called_with_root(mock)


def test_list_gpg_keys_no_info_root():
    """
    Test list_gpg_keys with no extra information and root
    """
    mock = MagicMock(return_value="\n".join(["gpg-pubkey-1", "gpg-pubkey-2"]))
    with patch.dict(rpm.__salt__, {"cmd.run_stdout": mock}):
        assert rpm.list_gpg_keys(root="/mnt") == ["gpg-pubkey-1", "gpg-pubkey-2"]
        assert _called_with_root(mock)


@patch("salt.modules.rpm_lowpkg.info_gpg_key")
def test_list_gpg_keys_info(info_gpg_key):
    """
    Test list_gpg_keys with extra information
    """
    info_gpg_key.side_effect = lambda x, root: {"Description": "key for {}".format(x)}
    mock = MagicMock(return_value="\n".join(["gpg-pubkey-1", "gpg-pubkey-2"]))
    with patch.dict(rpm.__salt__, {"cmd.run_stdout": mock}):
        assert rpm.list_gpg_keys(info=True) == {
            "gpg-pubkey-1": {"Description": "key for gpg-pubkey-1"},
            "gpg-pubkey-2": {"Description": "key for gpg-pubkey-2"},
        }
        assert not _called_with_root(mock)


def test_info_gpg_key():
    """
    Test info_gpg_keys from a normal output
    """
    info = """Name        : gpg-pubkey
Version     : 3dbdc284
Release     : 53674dd4
Architecture: (none)
Install Date: Fri 08 Mar 2019 11:57:44 AM UTC
Group       : Public Keys
Size        : 0
License     : pubkey
Signature   : (none)
Source RPM  : (none)
Build Date  : Mon 05 May 2014 10:37:40 AM UTC
Build Host  : localhost
Packager    : openSUSE Project Signing Key <opensuse@opensuse.org>
Summary     : gpg(openSUSE Project Signing Key <opensuse@opensuse.org>)
Description :
-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: rpm-4.14.2.1 (NSS-3)

mQENBEkUTD8BCADWLy5d5IpJedHQQSXkC1VK/oAZlJEeBVpSZjMCn8LiHaI9Wq3G
3Vp6wvsP1b3kssJGzVFNctdXt5tjvOLxvrEfRJuGfqHTKILByqLzkeyWawbFNfSQ
93/8OunfSTXC1Sx3hgsNXQuOrNVKrDAQUqT620/jj94xNIg09bLSxsjN6EeTvyiO
mtE9H1J03o9tY6meNL/gcQhxBvwuo205np0JojYBP0pOfN8l9hnIOLkA0yu4ZXig
oKOVmf4iTjX4NImIWldT+UaWTO18NWcCrujtgHueytwYLBNV5N0oJIP2VYuLZfSD
VYuPllv7c6O2UEOXJsdbQaVuzU1HLocDyipnABEBAAG0NG9wZW5TVVNFIFByb2pl
Y3QgU2lnbmluZyBLZXkgPG9wZW5zdXNlQG9wZW5zdXNlLm9yZz6JATwEEwECACYC
GwMGCwkIBwMCBBUCCAMEFgIDAQIeAQIXgAUCU2dN1AUJHR8ElQAKCRC4iy/UPb3C
hGQrB/9teCZ3Nt8vHE0SC5NmYMAE1Spcjkzx6M4r4C70AVTMEQh/8BvgmwkKP/qI
CWo2vC1hMXRgLg/TnTtFDq7kW+mHsCXmf5OLh2qOWCKi55Vitlf6bmH7n+h34Sha
Ei8gAObSpZSF8BzPGl6v0QmEaGKM3O1oUbbB3Z8i6w21CTg7dbU5vGR8Yhi9rNtr
hqrPS+q2yftjNbsODagaOUb85ESfQGx/LqoMePD+7MqGpAXjKMZqsEDP0TbxTwSk
4UKnF4zFCYHPLK3y/hSH5SEJwwPY11l6JGdC1Ue8Zzaj7f//axUs/hTC0UZaEE+a
5v4gbqOcigKaFs9Lc3Bj8b/lE10Y
=i2TA
-----END PGP PUBLIC KEY BLOCK-----

"""
    mock = MagicMock(return_value=info)
    with patch.dict(rpm.__salt__, {"cmd.run_stdout": mock}):
        assert rpm.info_gpg_key("key") == {
            "Name": "gpg-pubkey",
            "Version": "3dbdc284",
            "Release": "53674dd4",
            "Architecture": None,
            "Install Date": datetime.datetime(2019, 3, 8, 11, 57, 44),
            "Group": "Public Keys",
            "Size": 0,
            "License": "pubkey",
            "Signature": None,
            "Source RPM": None,
            "Build Date": datetime.datetime(2014, 5, 5, 10, 37, 40),
            "Build Host": "localhost",
            "Packager": "openSUSE Project Signing Key <opensuse@opensuse.org>",
            "Summary": "gpg(openSUSE Project Signing Key <opensuse@opensuse.org>)",
            "Description": """-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: rpm-4.14.2.1 (NSS-3)

mQENBEkUTD8BCADWLy5d5IpJedHQQSXkC1VK/oAZlJEeBVpSZjMCn8LiHaI9Wq3G
3Vp6wvsP1b3kssJGzVFNctdXt5tjvOLxvrEfRJuGfqHTKILByqLzkeyWawbFNfSQ
93/8OunfSTXC1Sx3hgsNXQuOrNVKrDAQUqT620/jj94xNIg09bLSxsjN6EeTvyiO
mtE9H1J03o9tY6meNL/gcQhxBvwuo205np0JojYBP0pOfN8l9hnIOLkA0yu4ZXig
oKOVmf4iTjX4NImIWldT+UaWTO18NWcCrujtgHueytwYLBNV5N0oJIP2VYuLZfSD
VYuPllv7c6O2UEOXJsdbQaVuzU1HLocDyipnABEBAAG0NG9wZW5TVVNFIFByb2pl
Y3QgU2lnbmluZyBLZXkgPG9wZW5zdXNlQG9wZW5zdXNlLm9yZz6JATwEEwECACYC
GwMGCwkIBwMCBBUCCAMEFgIDAQIeAQIXgAUCU2dN1AUJHR8ElQAKCRC4iy/UPb3C
hGQrB/9teCZ3Nt8vHE0SC5NmYMAE1Spcjkzx6M4r4C70AVTMEQh/8BvgmwkKP/qI
CWo2vC1hMXRgLg/TnTtFDq7kW+mHsCXmf5OLh2qOWCKi55Vitlf6bmH7n+h34Sha
Ei8gAObSpZSF8BzPGl6v0QmEaGKM3O1oUbbB3Z8i6w21CTg7dbU5vGR8Yhi9rNtr
hqrPS+q2yftjNbsODagaOUb85ESfQGx/LqoMePD+7MqGpAXjKMZqsEDP0TbxTwSk
4UKnF4zFCYHPLK3y/hSH5SEJwwPY11l6JGdC1Ue8Zzaj7f//axUs/hTC0UZaEE+a
5v4gbqOcigKaFs9Lc3Bj8b/lE10Y
=i2TA
-----END PGP PUBLIC KEY BLOCK-----""",
        }
        assert not _called_with_root(mock)


def test_info_gpg_key_extended():
    """
    Test info_gpg_keys from an extended output
    """
    info = """Name        : gpg-pubkey
Version     : 3dbdc284
Release     : 53674dd4
Architecture: (none)
Install Date: Fri 08 Mar 2019 11:57:44 AM UTC
Group       : Public Keys
Size        : 0
License     : pubkey
Signature   : (none)
Source RPM  : (none)
Build Date  : Mon 05 May 2014 10:37:40 AM UTC
Build Host  : localhost
Packager    : openSUSE Project Signing Key <opensuse@opensuse.org>
Summary     : gpg(openSUSE Project Signing Key <opensuse@opensuse.org>)
Description :
-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: rpm-4.14.2.1 (NSS-3)

mQENBEkUTD8BCADWLy5d5IpJedHQQSXkC1VK/oAZlJEeBVpSZjMCn8LiHaI9Wq3G
3Vp6wvsP1b3kssJGzVFNctdXt5tjvOLxvrEfRJuGfqHTKILByqLzkeyWawbFNfSQ
93/8OunfSTXC1Sx3hgsNXQuOrNVKrDAQUqT620/jj94xNIg09bLSxsjN6EeTvyiO
mtE9H1J03o9tY6meNL/gcQhxBvwuo205np0JojYBP0pOfN8l9hnIOLkA0yu4ZXig
oKOVmf4iTjX4NImIWldT+UaWTO18NWcCrujtgHueytwYLBNV5N0oJIP2VYuLZfSD
VYuPllv7c6O2UEOXJsdbQaVuzU1HLocDyipnABEBAAG0NG9wZW5TVVNFIFByb2pl
Y3QgU2lnbmluZyBLZXkgPG9wZW5zdXNlQG9wZW5zdXNlLm9yZz6JATwEEwECACYC
GwMGCwkIBwMCBBUCCAMEFgIDAQIeAQIXgAUCU2dN1AUJHR8ElQAKCRC4iy/UPb3C
hGQrB/9teCZ3Nt8vHE0SC5NmYMAE1Spcjkzx6M4r4C70AVTMEQh/8BvgmwkKP/qI
CWo2vC1hMXRgLg/TnTtFDq7kW+mHsCXmf5OLh2qOWCKi55Vitlf6bmH7n+h34Sha
Ei8gAObSpZSF8BzPGl6v0QmEaGKM3O1oUbbB3Z8i6w21CTg7dbU5vGR8Yhi9rNtr
hqrPS+q2yftjNbsODagaOUb85ESfQGx/LqoMePD+7MqGpAXjKMZqsEDP0TbxTwSk
4UKnF4zFCYHPLK3y/hSH5SEJwwPY11l6JGdC1Ue8Zzaj7f//axUs/hTC0UZaEE+a
5v4gbqOcigKaFs9Lc3Bj8b/lE10Y
=i2TA
-----END PGP PUBLIC KEY BLOCK-----

Distribution: (none)
"""
    mock = MagicMock(return_value=info)
    with patch.dict(rpm.__salt__, {"cmd.run_stdout": mock}):
        assert rpm.info_gpg_key("key") == {
            "Name": "gpg-pubkey",
            "Version": "3dbdc284",
            "Release": "53674dd4",
            "Architecture": None,
            "Install Date": datetime.datetime(2019, 3, 8, 11, 57, 44),
            "Group": "Public Keys",
            "Size": 0,
            "License": "pubkey",
            "Signature": None,
            "Source RPM": None,
            "Build Date": datetime.datetime(2014, 5, 5, 10, 37, 40),
            "Build Host": "localhost",
            "Packager": "openSUSE Project Signing Key <opensuse@opensuse.org>",
            "Summary": "gpg(openSUSE Project Signing Key <opensuse@opensuse.org>)",
            "Description": """-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: rpm-4.14.2.1 (NSS-3)

mQENBEkUTD8BCADWLy5d5IpJedHQQSXkC1VK/oAZlJEeBVpSZjMCn8LiHaI9Wq3G
3Vp6wvsP1b3kssJGzVFNctdXt5tjvOLxvrEfRJuGfqHTKILByqLzkeyWawbFNfSQ
93/8OunfSTXC1Sx3hgsNXQuOrNVKrDAQUqT620/jj94xNIg09bLSxsjN6EeTvyiO
mtE9H1J03o9tY6meNL/gcQhxBvwuo205np0JojYBP0pOfN8l9hnIOLkA0yu4ZXig
oKOVmf4iTjX4NImIWldT+UaWTO18NWcCrujtgHueytwYLBNV5N0oJIP2VYuLZfSD
VYuPllv7c6O2UEOXJsdbQaVuzU1HLocDyipnABEBAAG0NG9wZW5TVVNFIFByb2pl
Y3QgU2lnbmluZyBLZXkgPG9wZW5zdXNlQG9wZW5zdXNlLm9yZz6JATwEEwECACYC
GwMGCwkIBwMCBBUCCAMEFgIDAQIeAQIXgAUCU2dN1AUJHR8ElQAKCRC4iy/UPb3C
hGQrB/9teCZ3Nt8vHE0SC5NmYMAE1Spcjkzx6M4r4C70AVTMEQh/8BvgmwkKP/qI
CWo2vC1hMXRgLg/TnTtFDq7kW+mHsCXmf5OLh2qOWCKi55Vitlf6bmH7n+h34Sha
Ei8gAObSpZSF8BzPGl6v0QmEaGKM3O1oUbbB3Z8i6w21CTg7dbU5vGR8Yhi9rNtr
hqrPS+q2yftjNbsODagaOUb85ESfQGx/LqoMePD+7MqGpAXjKMZqsEDP0TbxTwSk
4UKnF4zFCYHPLK3y/hSH5SEJwwPY11l6JGdC1Ue8Zzaj7f//axUs/hTC0UZaEE+a
5v4gbqOcigKaFs9Lc3Bj8b/lE10Y
=i2TA
-----END PGP PUBLIC KEY BLOCK-----""",
            "Distribution": None,
        }
        assert not _called_with_root(mock)


def test_remove_gpg_key():
    """
    Test remove_gpg_key
    """
    mock = MagicMock(return_value=0)
    with patch.dict(rpm.__salt__, {"cmd.retcode": mock}):
        assert rpm.remove_gpg_key("gpg-pubkey-1")
        assert not _called_with_root(mock)
