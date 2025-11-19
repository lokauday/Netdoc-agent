# Network Documentation Report

## Device Summary
- **Hostname:** None
- **Model:** C2960X-UNIVERSALK9-M
- **Serial:** FOC1234X1CD
- **OS Version:** 15.2(2)E7

## VLANs
| VLAN ID | Name | Ports |
|--------|------|-------|
| 10 | USERS |  |
| 20 | SERVERS |  |

## Interfaces
| Interface | Description | IP Address | VLAN | Status | Protocol |
|-----------|-------------|-----------|------|--------|----------|
| Vlan10 |  | 10.0.10.1/24 | 10 | up | up |
| Vlan20 |  | 10.0.20.1/24 | 20 | up | up |

## Neighbors (CDP/LLDP)
| Local Interface | Neighbor Device | Neighbor Interface |
|----------------|-----------------|--------------------|
| GigabitEthernet1/0/1 | CORE1 | GigabitEthernet0/1 |

## Routing Summary
- Dynamic Protocols: 
- Default Route: None
- Total Routes: None

## Topology (ASCII View)
```
ThisDevice(Gi1/0/1)---CORE1(Gi0/1)
```