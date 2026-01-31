"""
Aleph Cloud Monitor - A monitoring dashboard for Aleph instances
Built by Shem (AI)
"""
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
import httpx
from datetime import datetime, timedelta
from typing import Optional
import asyncio

app = FastAPI(
    title="Aleph Cloud Monitor",
    description="Monitor your Aleph Cloud instances and network stats",
    version="0.1.0"
)

ALEPH_API = "https://api2.aleph.im/api/v0"

# === API Endpoints ===

@app.get("/")
async def root():
    return {
        "name": "Aleph Cloud Monitor",
        "version": "0.1.0",
        "endpoints": [
            "/instances/{address}",
            "/programs/{address}",
            "/credits/{address}",
            "/messages/{address}",
            "/network/stats",
            "/network/nodes",
            "/dashboard"
        ]
    }

@app.get("/instances/{address}")
async def get_instances(address: str):
    """Get all instances for an address"""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{ALEPH_API}/messages.json",
                params={
                    "addresses": address,
                    "msgType": "INSTANCE",
                    "limit": 50
                },
                timeout=15
            )
            data = resp.json()
            instances = []
            for msg in data.get("messages", []):
                content = msg.get("content", {})
                instances.append({
                    "item_hash": msg.get("item_hash"),
                    "name": content.get("metadata", {}).get("name", "Unnamed"),
                    "created": datetime.fromtimestamp(msg.get("time", 0)).isoformat(),
                    "vcpus": content.get("resources", {}).get("vcpus"),
                    "memory": content.get("resources", {}).get("memory"),
                    "rootfs_size": content.get("rootfs", {}).get("size_mib"),
                    "payment": content.get("payment", {}).get("type"),
                })
            return {"address": address, "count": len(instances), "instances": instances}
    except Exception as e:
        return {"error": str(e)}

@app.get("/programs/{address}")
async def get_programs(address: str):
    """Get all programs for an address"""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{ALEPH_API}/messages.json",
                params={
                    "addresses": address,
                    "msgType": "PROGRAM",
                    "limit": 50
                },
                timeout=15
            )
            data = resp.json()
            programs = []
            for msg in data.get("messages", []):
                content = msg.get("content", {})
                programs.append({
                    "item_hash": msg.get("item_hash"),
                    "name": content.get("metadata", {}).get("name", "Unnamed"),
                    "created": datetime.fromtimestamp(msg.get("time", 0)).isoformat(),
                    "runtime": content.get("runtime", {}).get("ref", "")[:16] + "...",
                    "entrypoint": content.get("code", {}).get("entrypoint"),
                })
            return {"address": address, "count": len(programs), "programs": programs}
    except Exception as e:
        return {"error": str(e)}

@app.get("/credits/{address}")
async def get_credits(address: str):
    """Get credit balance for an address"""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://accounting.api.aleph.cloud/vm_cost_views/{address}",
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "address": address,
                    "balance": data.get("balance"),
                    "total_cost": data.get("total_cost"),
                    "vms": data.get("vms", [])
                }
            else:
                return {"address": address, "error": "Could not fetch credits"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/messages/{address}")
async def get_messages(address: str, limit: int = Query(default=10, le=50)):
    """Get recent messages for an address"""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{ALEPH_API}/messages.json",
                params={
                    "addresses": address,
                    "limit": limit
                },
                timeout=15
            )
            data = resp.json()
            messages = []
            for msg in data.get("messages", []):
                messages.append({
                    "type": msg.get("type"),
                    "item_hash": msg.get("item_hash", "")[:20] + "...",
                    "time": datetime.fromtimestamp(msg.get("time", 0)).isoformat(),
                    "channel": msg.get("channel"),
                    "size": msg.get("size")
                })
            return {"address": address, "count": len(messages), "messages": messages}
    except Exception as e:
        return {"error": str(e)}

@app.get("/network/stats")
async def network_stats():
    """Get Aleph network statistics"""
    try:
        async with httpx.AsyncClient() as client:
            # Get recent messages to calculate activity
            resp = await client.get(
                f"{ALEPH_API}/messages.json?limit=100",
                timeout=15
            )
            data = resp.json()
            
            type_counts = {}
            for msg in data.get("messages", []):
                t = msg.get("type", "UNKNOWN")
                type_counts[t] = type_counts.get(t, 0) + 1
            
            return {
                "sample_size": 100,
                "message_types": type_counts,
                "timestamp": datetime.utcnow().isoformat()
            }
    except Exception as e:
        return {"error": str(e)}

@app.get("/network/nodes")
async def network_nodes():
    """Get CRN nodes info"""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://scheduler.api.aleph.cloud/api/v0/allocation/resource_nodes",
                timeout=15
            )
            data = resp.json()
            nodes = []
            for node in data[:20]:  # Top 20
                nodes.append({
                    "name": node.get("name"),
                    "score": round(node.get("score", 0) * 100, 2),
                    "version": node.get("version"),
                    "url": node.get("url"),
                    "available_cpu": node.get("available_cpu"),
                    "available_memory": node.get("available_memory")
                })
            return {"count": len(data), "top_nodes": nodes}
    except Exception as e:
        return {"error": str(e)}

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(address: str = Query(default="0x929D09350230AB5Da6A6feE3bd967882118B0Ac4")):
    """Interactive monitoring dashboard"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Aleph Cloud Monitor</title>
        <style>
            * {{ box-sizing: border-box; }}
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; 
                margin: 0; padding: 20px;
                background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 100%);
                color: #e0e0e0;
                min-height: 100vh;
            }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            h1 {{ color: #7B3FE4; margin-bottom: 5px; }}
            .subtitle {{ color: #888; margin-bottom: 30px; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px; }}
            .card {{ 
                background: rgba(26, 26, 46, 0.8);
                border: 1px solid #333;
                border-radius: 12px;
                padding: 20px;
                backdrop-filter: blur(10px);
            }}
            .card h3 {{ color: #D4FF00; margin-top: 0; }}
            .stat-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; }}
            .stat {{ text-align: center; padding: 15px; background: rgba(0,0,0,0.3); border-radius: 8px; }}
            .stat-value {{ font-size: 28px; font-weight: bold; color: #7B3FE4; }}
            .stat-label {{ font-size: 12px; color: #888; margin-top: 5px; }}
            .instance {{ 
                background: rgba(0,0,0,0.3); 
                padding: 15px; 
                border-radius: 8px; 
                margin: 10px 0;
                border-left: 3px solid #4ade80;
            }}
            .instance-name {{ font-weight: bold; color: #fff; }}
            .instance-details {{ font-size: 13px; color: #888; margin-top: 5px; }}
            .loading {{ color: #888; font-style: italic; }}
            .address-input {{ 
                width: 100%; padding: 12px; 
                background: #1a1a2e; border: 1px solid #333;
                border-radius: 8px; color: #fff; font-size: 14px;
                margin-bottom: 20px;
            }}
            .btn {{ 
                background: #7B3FE4; color: #fff; 
                border: none; padding: 12px 24px;
                border-radius: 8px; cursor: pointer;
                font-size: 14px;
            }}
            .btn:hover {{ background: #6930c3; }}
            code {{ background: rgba(0,0,0,0.3); padding: 2px 6px; border-radius: 4px; font-size: 12px; }}
            .green {{ color: #4ade80; }}
            .yellow {{ color: #D4FF00; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>✦ Aleph Cloud Monitor</h1>
            <p class="subtitle">Real-time monitoring for your decentralized infrastructure</p>
            
            <div style="margin-bottom: 30px;">
                <input type="text" id="address" class="address-input" 
                    value="{address}" placeholder="Enter Ethereum address...">
                <button class="btn" onclick="loadDashboard()">Load Dashboard</button>
            </div>

            <div class="grid">
                <div class="card">
                    <h3>📊 Account Overview</h3>
                    <div id="account-stats" class="stat-grid">
                        <div class="stat">
                            <div class="stat-value" id="instance-count">-</div>
                            <div class="stat-label">Instances</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value" id="program-count">-</div>
                            <div class="stat-label">Programs</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value" id="credit-balance">-</div>
                            <div class="stat-label">Credits</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value" id="message-count">-</div>
                            <div class="stat-label">Messages</div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h3>🖥️ Running Instances</h3>
                    <div id="instances-list">
                        <p class="loading">Loading...</p>
                    </div>
                </div>

                <div class="card">
                    <h3>🌐 Network Stats</h3>
                    <div id="network-stats">
                        <p class="loading">Loading...</p>
                    </div>
                </div>

                <div class="card">
                    <h3>📝 Recent Activity</h3>
                    <div id="recent-messages">
                        <p class="loading">Loading...</p>
                    </div>
                </div>
            </div>

            <div style="margin-top: 40px; text-align: center; color: #666;">
                <p>Built by <span class="yellow">Shem</span> (AI) | Running on <span class="green">Aleph Cloud</span></p>
            </div>
        </div>

        <script>
            const API = window.location.origin;
            
            async function loadDashboard() {{
                const address = document.getElementById('address').value;
                
                // Load instances
                fetch(`${{API}}/instances/${{address}}`)
                    .then(r => r.json())
                    .then(data => {{
                        document.getElementById('instance-count').textContent = data.count || 0;
                        const list = document.getElementById('instances-list');
                        if (data.instances && data.instances.length > 0) {{
                            list.innerHTML = data.instances.map(i => `
                                <div class="instance">
                                    <div class="instance-name">${{i.name}}</div>
                                    <div class="instance-details">
                                        ${{i.vcpus}} vCPU | ${{Math.round(i.memory/1024)}}GB RAM | ${{i.payment}}
                                    </div>
                                </div>
                            `).join('');
                        }} else {{
                            list.innerHTML = '<p style="color:#888">No instances found</p>';
                        }}
                    }});
                
                // Load programs
                fetch(`${{API}}/programs/${{address}}`)
                    .then(r => r.json())
                    .then(data => {{
                        document.getElementById('program-count').textContent = data.count || 0;
                    }});
                
                // Load credits
                fetch(`${{API}}/credits/${{address}}`)
                    .then(r => r.json())
                    .then(data => {{
                        document.getElementById('credit-balance').textContent = 
                            data.balance ? Math.round(data.balance).toLocaleString() : '-';
                    }});
                
                // Load messages
                fetch(`${{API}}/messages/${{address}}?limit=5`)
                    .then(r => r.json())
                    .then(data => {{
                        document.getElementById('message-count').textContent = data.count || 0;
                        const list = document.getElementById('recent-messages');
                        if (data.messages && data.messages.length > 0) {{
                            list.innerHTML = data.messages.map(m => `
                                <div style="padding: 8px 0; border-bottom: 1px solid #333;">
                                    <span class="yellow">${{m.type}}</span> 
                                    <span style="color:#888">${{m.time}}</span>
                                </div>
                            `).join('');
                        }} else {{
                            list.innerHTML = '<p style="color:#888">No messages found</p>';
                        }}
                    }});
                
                // Load network stats
                fetch(`${{API}}/network/nodes`)
                    .then(r => r.json())
                    .then(data => {{
                        const div = document.getElementById('network-stats');
                        div.innerHTML = `
                            <p><strong class="green">${{data.count}}</strong> CRN nodes online</p>
                            <p style="margin-top:10px; color:#888;">Top nodes:</p>
                            ${{(data.top_nodes || []).slice(0,3).map(n => `
                                <div style="padding:5px 0;"><code>${{n.name}}</code> - ${{n.score}}%</div>
                            `).join('')}}
                        `;
                    }});
            }}
            
            // Load on page load
            loadDashboard();
        </script>
    </body>
    </html>
    """
    return html


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
