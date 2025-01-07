###
# Copyright 2021 New H3C Technologies Co., Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###

# -*- coding: utf-8 -*-


from exception.ToolException import FailException
from utils.client import RedfishClient
from utils.common import Constant
from utils.model import BaseModule


class GetHealth(BaseModule):

    def __init__(self):
        super().__init__()
        self.overall = None
        self.board = None
        self.fans = None
        self.memory = None
        self.pcie = None
        self.power = None
        self.processor = None
        self.storage = None
        self.temperature = None

    @property
    def dict(self):

        return self.__dict__

    def run(self, args):

        client = RedfishClient(args)
        systems_id = client.get_systems_id()
        url = "/redfish/v1/System/%s" % systems_id
        resp = client.send_request("get", url)
        if (isinstance(resp, dict) and
                Constant.SUCCESS_200 == resp.get("status_code", None)):
            self._pack_resource(resp["resource"])
        else:
            err_info = "Failure: failed to get system health status"
            self.err_list.append(err_info)
            raise FailException(*self.err_list)

        return self.suc_list

    def _pack_resource(self, resp):

        if (isinstance(resp.get("Healthstate", None), dict)):
            self.overall = resp["Healthstate"].get("OverallHealth", None)
            self.board = resp["Healthstate"].get("board", None)
            self.fans = resp["Healthstate"].get("fans", None)
            self.memory = resp["Healthstate"].get("memory", None)
            self.pcie = resp["Healthstate"].get("pcie", None)
            self.power = resp["Healthstate"].get("power", None)
            self.processor = resp["Healthstate"].get("processor", None)
            self.storage = resp["Healthstate"].get("storage", None)
            self.temperature = resp["Healthstate"].get("temperature", None)
        else:
            err_info = "Failure: failed to pack health status"
            self.err_list.append(err_info)
            raise FailException(*self.err_list)