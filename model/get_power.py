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


import re
from exception.ToolException import FailException
from utils.client import RestfulClient,RedfishClient
from utils.model import BaseModule


class GetPower(BaseModule):

    def __init__(self):

        self.cpuPower = None
        self.memoryPower = None
        self.pciePower = None
        self.fanPower = None
        self.storagePower = None
        self.gpuPower = []
        self.overallPower = None

    @property
    def dict(self):

        return {
            "CPU Power Usage": self.cpuPower,
            "Memory Power Usage": self.memoryPower,
            "Fan Power Usage": self.fanPower,
            "Storage Power Usage": self.storagePower,
            "GPU Power Usage": self.gpuPower,
            "Overall Power Usage": self.overallPower
        }

    def run(self, args):

        client = RedfishClient(args)
        system_id = client.get_systems_id()
        url = f"/redfish/v1/Chassis/{system_id}/Power"
        resp = client.send_request("get", url)
        if (isinstance(resp, dict) and
                resp.get("status_code", None) == 200):
            self.package_results(resp["resource"])
        else:
            err_info = "Failure: failed to get power information"
            self.err_list.append(err_info)
            raise FailException(*self.err_list)
        url = f"/redfish/v1/Systems/{system_id}/GPU"
        resp = client.send_request("get", url)
        if (isinstance(resp, dict) and
                resp.get("status_code", None) == 200):
            for gpu in resp["resource"]["GPU"]:
                self.gpuPower.append(gpu["PowerConsumedWatts"])
        else:
            err_info = "Failure: failed to get GPU power information"
            self.err_list.append(err_info)
            raise FailException(*self.err_list)
        self.overallPower = self.cpuPower + self.memoryPower + self.fanPower + self.storagePower + sum(self.gpuPower)

    def package_results(self, resp):

        self.cpuPower = resp["PowerControl"][0]["Oem"]["Public"]["CurrentCPUPowerWatts"]
        self.memoryPower = resp["PowerControl"][0]["Oem"]["Public"]["CurrentMemoryPowerWatts"]
        self.fanPower = resp["PowerControl"][0]["Oem"]["Public"]["CurrentFanPowerWatts"]
        self.storagePower = resp["PowerControl"][0]["Oem"]["Public"]["CurrentDiskPowerWatts"]