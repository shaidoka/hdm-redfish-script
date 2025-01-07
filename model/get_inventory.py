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
from utils.tools import init_args

class GetInventory(BaseModule):

    def __init__(self):
        super().__init__()
        self.id = None
        self.hostname = None
        self.memoryCount = None
        self.networkInterfaceCount = None
        self.gpuCount = None
        self.cpuCount = None
        self.lDiskCount = None
        self.pDiskCount = None
        self.storageControllerCount = None
        self.pcieCount = None
        self.psuCount = None

    @property
    def dict(self):

        return {
            "HostName": self.hostname,
            "MemoryCount": self.memoryCount,
            "NetworkInterfaceCount": self.networkInterfaceCount,
            "GPUCount": self.gpuCount,
            "CPUCount": self.cpuCount,
            "LogicalDiskCount": self.lDiskCount,
            "PhysicalDiskCount": self.pDiskCount,
            "StorageControllerCount": self.storageControllerCount,
            "PCIECount": self.pcieCount,
            "PSUCount": self.psuCount
        }
    
    def run(self, args):

        client = RedfishClient(args)
        self.id = client.get_systems_id()
        url = "/redfish/v1/Systems/%s" % self.id
        resp = client.send_request("get", url)
        if (isinstance(resp, dict) and
                Constant.SUCCESS_200 == resp.get("status_code", None)):
            self.pack_resource(resp["resource"])
        else:
            err_info = "Failure: failed to get system inventory"
            self.err_list.append(err_info)
            raise FailException(*self.err_list)
        url = "/redfish/v1/Systems/%s/NetworkInterfaces" % self.id
        resp = client.send_request("get", url)
        if (isinstance(resp, dict) and
                Constant.SUCCESS_200 == resp.get("status_code", None)):
            self.networkInterfaceCount = resp.get("Members@odata.count", None)
        else:
            err_info = "Failure: failed to get network interface count"
            self.err_list.append(err_info)
            raise FailException(*self.err_list)
        url = "/redfish/v1/Systems/%s/GPU" % self.id
        resp = client.send_request("get", url)
        if (isinstance(resp, dict) and
                Constant.SUCCESS_200 == resp.get("status_code", None)):
            self.gpuCount = resp.get("Members@odata.count", None)
        else:
            err_info = "Failure: failed to get GPU count"
            self.err_list.append(err_info)
            raise FailException(*self.err_list)

    def pack_resource(self, resp):

        self.hostname = resp.get("HostName", None)
        self.memoryCount = resp.get("MemorySummary", None)["Count"]
        self.cpuCount = resp.get("CPUCount", None)
        self.lDiskCount = resp["StorageControllerSummary"]["LogicalDriveCount"]
        self.pDiskCount = resp["StorageControllerSummary"]["PhysicalDriveCount"]
        self.storageControllerCount = resp.get("StorageControllerCount", None)
        self.pcieCount = resp.get("PCIECount", None)
        self.psuCount = resp.get("PSUCount", None)