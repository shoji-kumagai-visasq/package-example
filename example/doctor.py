#  Copyright 2025 Shoji Kumagai
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""example doctor サブコマンドモジュール"""

import json
import subprocess
import time
from contextlib import contextmanager
from typing import Callable, Generator, TypeAlias

import rich
from packaging import version
from rich.live import Live
from rich.table import Table
from rich.theme import Theme

from .constants import GCP_PROJECT_NAME, MACOS
from .paths import DOCKER_CONFIG_JSON, GCLOUD_ADC_JSON
from .termui import Emoji


def command_exists(command: str) -> list[str | Emoji]:
    """コマンドが実行できるかどうかをテストする

    実行できる場合はインストール済みと判定。
    """

    proc = subprocess.run(
        ["command", "-v", f"{command}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        check=False,
    )
    if proc.returncode == 0:
        return [command, "インストール済か", f"[success]{Emoji.SUCCESS}[/]", f"[success]{proc.stdout.strip()}[/]"]
    else:
        return [command, "インストール済か", f"[error]{Emoji.FAIL}[/]", ""]


def execute_command(command: str) -> str:
    """引数で指定した文字列をコマンドとして実行し、出力を得る"""

    output = subprocess.check_output(
        command,
        shell=True,
        text=True,
    )
    return output.strip()


VERSION_COMMAND_MAPPING: dict[str, str] = {
    "gh": "gh version | grep version | awk '{ print $3; }'",
    "docker": "docker --version | awk '{ print $3; }' | tr -d ','",
    "docker compose": "docker compose version | awk '{ print $4; }' | sed -e 's/-.*$//g' -e 's/v//g'",
    "mutagen": "mutagen --version | awk '{ print $3; }'",
    "gcloud": "gcloud --version | grep SDK | awk '{ print $4; }'",
}


def current_version(command: str):
    """引数で指定した文字列をコマンドとして実行し、バージョン文字列を得る"""

    return execute_command(VERSION_COMMAND_MAPPING[command])


def version_satisfied(command: str, required: str) -> list[str | Emoji]:
    """引数で指定したコマンドのバージョンが、任意の要件を満たしているかをテストする"""

    current = current_version(command)
    cur = version.parse(current)
    req = version.parse(required)
    if cur >= req:
        return [
            command,
            "バージョン要件を満たしているか",
            f"[success]{Emoji.SUCCESS}[/]",
            f"[success]{current}[/] >={required}",
        ]
    else:
        return [
            command,
            "バージョン要件を満たしているか",
            f"[error]{Emoji.FAIL}[/]",
            f"[error]{current}[/] >={required}",
        ]


def check_ssh_access_on_github() -> list[str | Emoji]:
    """Github に対して ssh 鍵を使ったアクセス設定が完了しているかをテストする"""

    ssh_test_command = "ssh -o 'ConnectTimeout 5' -T git@github.com"
    output = subprocess.run(
        ssh_test_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        text=True,
        check=False,
    )
    message = output.stderr.strip()
    if "You've successfully authenticated" in message:
        return ["ssh", "Githubに接続可能か", f"[success]{Emoji.SUCCESS}[/]", f"[success]{message}[/]"]
    else:
        return ["ssh", "Githubに接続可能か", f"[error]{Emoji.FAIL}[/]", f"[error]{message}[/]"]


def check_gh_auth_login() -> list[str | Emoji]:
    """gh コマンドを使って Github にログイン済みかどうかをテストする"""

    gh_auth_status_command = "gh auth status"
    output = subprocess.run(
        gh_auth_status_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        text=True,
        check=False,
    )
    if "You are not logged into any GitHub hosts." in output.stderr:
        return [
            "gh",
            "ログイン済か",
            f"[error]{Emoji.FAIL}[/]",
            "[error]ログインしていません。gh auth login を実行して Github ホストにログインしてください。[/]",
        ]
    else:
        return ["gh", "ログイン済か", f"[success]{Emoji.SUCCESS}[/]", ""]


def check_docker_daemon() -> list[str | Emoji]:
    """ローカル環境で docker daemon プロセスが実行済みかどうかをテストする"""

    if MACOS:
        pgrep_command = "pgrep com.docker.backend"
    else:
        pgrep_command = "pgrep -f dockerd"
    proc = subprocess.run(
        pgrep_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        text=True,
        check=False,
    )
    if proc.returncode == 0:
        return ["Docker daemon", "プロセス起動済か", f"[success]{Emoji.SUCCESS}[/]", ""]
    else:
        return [
            "Docker daemon",
            "プロセス起動済か",
            f"[error]{Emoji.FAIL}[/]",
            "[error]プロセスの起動が確認できません。Docker daemon プロセスを起動してください。[/]",
        ]


def check_configure_docker() -> list[str | Emoji]:
    """Google Cloud SDK で docker の設定が完了しているかをテストする"""

    if not DOCKER_CONFIG_JSON.exists():
        return [
            "Google Cloud",
            "Artifact Registry 連携済か",
            f"[error]{Emoji.FAIL}[/]",
            "[error]Artifact Registry の連携が未設定です。gcloud auth configure-docker を実行してください。[/]",
        ]
    config = json.load(open(DOCKER_CONFIG_JSON, "rb"))
    if config.get("credHelpers") is None:
        return [
            "Google Cloud",
            "Artifact Registry 連携済か",
            f"[error]{Emoji.FAIL}[/]",
            "[error]Artifact Registry の連携が未設定です。gcloud auth configure-docker を実行してください。[/]",
        ]
    return [
        "Google Cloud",
        "Artifact Registry 連携済か",
        f"[success]{Emoji.SUCCESS}[/]",
        f"[success]{DOCKER_CONFIG_JSON.absolute()}[/]",
    ]


MESSAGE_CREDENTIAL_NOT_SET = f"""[error]デフォルト認証情報が未設定です。以下のコマンドを実行して認証を完了してください。
gcloud config set account <your-name@visasq.com>
gcloud config set project {GCP_PROJECT_NAME}
gcloud auth application-default login[/]
"""


def check_application_credentials() -> list[str | Emoji]:
    """Google Cloud SDK でログインが完了しているかをテストする"""

    if not GCLOUD_ADC_JSON.exists():
        return [
            "Google Cloud",
            "デフォルト認証情報が設定済か",
            f"[error]{Emoji.FAIL}[/]",
            MESSAGE_CREDENTIAL_NOT_SET,
        ]
    else:
        return [
            "Google Cloud",
            "デフォルト認証情報が設定済か",
            f"[success]{Emoji.SUCCESS}[/]",
            f"[success]{GCLOUD_ADC_JSON.absolute()}[/]",
        ]


MESSAGE_RESOURCE_MGR_API_NOT_ENABLED = f"""[error]Cloud Resource Manager API 有効化が未実施です。Cloud Resource Manager API を有効にしてください。
gcloud services enable --project {GCP_PROJECT_NAME} cloudresourcemanager.googleapis.com[/]
"""


def check_cloud_resource_manager_enabled() -> list[str | Emoji]:
    """Google Cloud SDK で Resource Manager API が有効化されているかをテストする"""

    command = (
        "gcloud services list --enabled | grep -q cloudresourcemanager.googleapis.com"
    )
    proc = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        text=True,
        check=False,
    )
    if proc.returncode == 0:
        return ["Google Cloud", "Resource Manager API が有効化済か", f"[success]{Emoji.SUCCESS}[/]", ""]
    else:
        return [
            "Google Cloud",
            "Resource Manager API が有効化済か",
            f"[error]{Emoji.FAIL}[/]",
            MESSAGE_RESOURCE_MGR_API_NOT_ENABLED,
        ]


TestConfigExtra: TypeAlias = list[tuple[Callable, tuple[str, ...] | None]]
TestConfig: TypeAlias = dict[str, bool | TestConfigExtra]
Tool: TypeAlias = str

TOOL_TEST_CONFIG_MAPPING: dict[Tool, TestConfig] = {
    "xcode-select": {"platform": MACOS},
    "brew": {"platform": MACOS},
    "make": {},
    "ssh": {
        "extra": [
            (check_ssh_access_on_github, None),
        ],
    },
    "jq": {},
    "pgrep": {},
    "peco": {},
    "pipx": {},
    "gh": {
        "extra": [
            (version_satisfied, ("gh", "2.0.0")),
            (check_gh_auth_login, None),
        ],
    },
    "docker": {
        "extra": [
            (version_satisfied, ("docker", "20.10.7")),
            (version_satisfied, ("docker compose", "1.29.2")),
            (check_docker_daemon, None),
        ],
    },
    "mutagen": {
        "extra": [
            (version_satisfied, ("mutagen", "0.13.0")),
        ],
    },
    "gcloud": {
        "extra": [
            (version_satisfied, ("gcloud", "379.0.0")),
            (check_configure_docker, None),
            (check_application_credentials, None),
            (check_cloud_resource_manager_enabled, None),
        ],
    },
}

DEFAULT_THEME = {
    "primary": "cyan",
    "success": "green",
    "warning": "yellow",
    "error": "red",
    "info": "blue",
    "req": "bold green",
}

BEAT_TIME = 0.04


@contextmanager
def beat(length: int = 1) -> Generator[None, None, None]:
    yield
    time.sleep(length * BEAT_TIME)


def run() -> None:
    """開発作業に必要なツールのインストール状態や設定をテストする"""

    console = rich.get_console()
    console.push_theme(theme=Theme(DEFAULT_THEME))

    table = Table(title="Doctor result")
    table.add_column("Target", no_wrap=True)
    table.add_column("Condition", no_wrap=True)
    table.add_column("Result", no_wrap=True)
    table.add_column("Details", no_wrap=True)

    with Live(table, console=console, screen=False, refresh_per_second=20):
        for tool, test_config in TOOL_TEST_CONFIG_MAPPING.items():
            # コマンドの実在確認
            # プラットフォームによって実行可否が異なるケースは platform の bool 値を確認する
            platform = test_config.get("platform")
            if platform is None or platform:
                with beat(1):
                    table.add_row(*command_exists(tool))

            # 追加確認項目の実行
            if extras := test_config.get("extra"):
                for func, args in extras:
                    with beat(1):
                        table.add_row(*(func(*args) if args else func()))
