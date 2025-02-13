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

filename: common.json
"""

from dataclasses import dataclass
from pathlib import Path

from dataclasses_json import LetterCase, dataclass_json


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CommonGcpProject:
    project: str
    restricted_project: str


@dataclass_json
@dataclass
class CommonGcp:
    dev: CommonGcpProject
    stg: CommonGcpProject
    prod: CommonGcpProject


@dataclass_json
@dataclass
class CommonRepositories:
    app: list[str]
    infra: list[str]


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CommonJson:
    email: str
    workspace_path: str | Path
    gcp: CommonGcp
