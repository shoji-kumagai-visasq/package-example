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

"""利用または参照する定数を定義するモジュール"""

import platform

from .models.common import CommonGcpProject, CommonJson
from .models.config import ConfigJson
from .paths import EXAMPLE_COMMON_JSON, EXAMPLE_CONFIG_JSON


def is_macos() -> bool:
    """MacOS か否かを判定する"""
    return platform.system() == "Darwin"


def is_linux() -> bool:
    """Linux か否かを判定する"""
    return platform.system() == "Linux"


MACOS: bool = is_macos()
"""実行プラットフォーム環境が MacOS か否かを表す定数"""

LINUX: bool = is_linux()
"""実行プラットフォーム環境が Linux か否かを表す定数"""


def get_gcp_project_name(stage: str = "dev") -> str:
    """Google Cloud の個人プロジェクト名を取得する"""

    if EXAMPLE_COMMON_JSON.exists():
        common: CommonJson = CommonJson.from_json(  # type: ignore
            open(EXAMPLE_COMMON_JSON, "rb").read(),
        )
        return getattr(common.gcp, stage).project
    else:
        config: ConfigJson = ConfigJson.from_json(  # type: ignore
            open(EXAMPLE_CONFIG_JSON, "rb").read(),
        )
        return getattr(config.gcp, stage).projects[0].projectName


GCP_PROJECT_NAME: str = get_gcp_project_name()
"""個人用 Google Cloud Project 名"""


GCP_PROJECT_STG = CommonGcpProject(
    project="service-vis-asq-v2-stg",
    restricted_project="vis-asq-restricted-stg",
)
"""Staging用 Google Cloud Project 名"""


GCP_PROJECT_PROD = CommonGcpProject(
    project="service-vis-asq-v2-prod",
    restricted_project="vis-asq-restricted-prod",
)
"""Production用 Google Cloud Project 名"""
