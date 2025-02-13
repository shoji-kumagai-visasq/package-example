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

"""CLI が利用または参照する設定ファイルの構造を定義するモジュール

filename: config.json
"""

from dataclasses import dataclass
from pathlib import Path

from dataclasses_json import LetterCase, dataclass_json


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ConfigAccount:
    mail_address: str
    company: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ConfigWorkspace:
    name: str
    activate: bool
    current_dir: str | Path


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ConfigSlack:
    mension_name: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ConfigGcpProjectDetail:
    project_name: str
    restricted_project_name: str
    region: str
    activate: bool


@dataclass
class ConfigGcpProjects:
    projects: list[ConfigGcpProjectDetail]


@dataclass
class ConfigGcp:
    dev: ConfigGcpProjects
    stg: ConfigGcpProjects
    prod: ConfigGcpProjects


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ConfigJson:
    account: ConfigAccount | None
    workspaces: list[ConfigWorkspace]
    slack: ConfigSlack | None
    gcp: ConfigGcp | None
