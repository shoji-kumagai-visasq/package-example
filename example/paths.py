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

"""利用または参照する path を定義するモジュール"""

import os
from pathlib import Path
from typing import Optional


def get_expanded_environ(env_name: str) -> Optional[Path]:
    value = os.environ.get(env_name)
    if value is not None:
        return Path(value).expanduser().resolve()
    return value


DEFAULT_CONFIG_ROOT: Path = (
    get_expanded_environ("XDG_CONFIG_HOME") or Path.home() / ".config"
)

EXAMPLE_CONFIG_HOME: Path = DEFAULT_CONFIG_ROOT / "example"
EXAMPLE_COMMON_JSON: Path = EXAMPLE_CONFIG_HOME / "common.json"
EXAMPLE_CONFIG_JSON: Path = EXAMPLE_CONFIG_HOME / "config.json"

DOCKER_CONFIG_HOME: Path = Path.home() / ".docker"
DOCKER_CONFIG_JSON: Path = DOCKER_CONFIG_HOME / "config.json"

GCLOUD_CONFIG_HOME: Path = DEFAULT_CONFIG_ROOT / "gcloud"
GCLOUD_ADC_JSON: Path = GCLOUD_CONFIG_HOME / "application_default_credentials.json"
