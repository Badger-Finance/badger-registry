// SPDX-License-Identifier: MIT
pragma solidity >=0.6.0 <0.7.0;

library Strings2Bytes32 {
    function toBytes32(string memory source) public returns (bytes32 result) {
        bytes memory tempEmptyStringTest = bytes(source);
        if (tempEmptyStringTest.length == 0) {
            return 0x0;
        }

        assembly {
            result := mload(add(source, 32))
        }
    }
}
