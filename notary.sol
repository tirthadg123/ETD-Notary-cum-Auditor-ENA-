pragma solidity ^0.8.0;
contract ETDNotary {
    struct ThesisRecord {
        string dspaceUUID;
        string documentHash;
        uint256 timestamp;
        address registrar;
    }
    mapping(string => ThesisRecord) public registry;
    event ThesisNotarized(string indexed dspaceUUID, string documentHash, uint256 timestamp);
    function notarizeThesis(string memory _uuid, string memory _hash) public {
        require(bytes(registry[_uuid].dspaceUUID).length == 0, "This ETD UUID is already notarized!");
        registry[_uuid] = ThesisRecord({
            dspaceUUID: _uuid,
            documentHash: _hash,
            timestamp: block.timestamp,
            registrar: msg.sender
        });
        emit ThesisNotarized(_uuid, _hash, block.timestamp);
    }
    function verifyThesis(string memory _uuid) public view returns (string memory, uint256) {
        return (registry[_uuid].documentHash, registry[_uuid].timestamp);
    }
}
