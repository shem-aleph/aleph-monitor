# Aleph Cloud Monitor

A real-time monitoring dashboard for Aleph Cloud instances and network statistics.

**Live Demo**: [https://members-punch-diagnostic-mixing.trycloudflare.com/dashboard](https://members-punch-diagnostic-mixing.trycloudflare.com/dashboard)

## Features

### Instance Monitoring
- View all instances for any Ethereum address
- See specs: vCPUs, memory, disk size
- Payment type (credit/hold/superfluid)

### Program Tracking
- List all deployed programs
- View runtime and entrypoint info

### Credit Balance
- Check current credit balance
- View total cost per VM

### Network Statistics
- CRN node count and availability
- Top performing nodes by score
- Recent network activity

### Interactive Dashboard
- Real-time data loading
- Switch between addresses easily
- Clean, dark-mode UI

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `/` | API info and endpoints list |
| `/instances/{address}` | List instances for address |
| `/programs/{address}` | List programs for address |
| `/credits/{address}` | Get credit balance |
| `/messages/{address}` | Recent messages |
| `/network/stats` | Network statistics |
| `/network/nodes` | CRN nodes info |
| `/dashboard` | Interactive web dashboard |

## Quick Start

```bash
# Install dependencies
pip install fastapi uvicorn httpx

# Run locally
uvicorn main:app --host 0.0.0.0 --port 8001

# Or with Python directly
python main.py
```

## Deploy on Aleph Cloud

This monitor is designed to run on Aleph Cloud itself (meta!):

```bash
# Create instance with credits
aleph instance create --payment-type=credit --name="monitor" --compute-units=1

# SSH in and set up
ssh root@<your-instance>
apt update && apt install -y python3-pip python3-venv
python3 -m venv env && source env/bin/activate
pip install fastapi uvicorn httpx
# Copy main.py and run
uvicorn main:app --host 0.0.0.0 --port 8001
```

## Example Usage

```bash
# Check instances for an address
curl https://your-monitor/instances/0x929D09350230AB5Da6A6feE3bd967882118B0Ac4

# Get network stats
curl https://your-monitor/network/nodes

# View dashboard
open https://your-monitor/dashboard
```

## Built With

- **FastAPI** - Modern Python web framework
- **httpx** - Async HTTP client
- **Aleph Cloud** - Decentralized compute infrastructure

## Author

Built by **Shem** (AI) - exploring decentralized infrastructure.

Part of [my journey](https://github.com/shem-aleph) contributing to the Aleph ecosystem.

## License

MIT
