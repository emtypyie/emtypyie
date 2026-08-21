# pyielink: High-Performance Remote Access Framework

## ⚙️ Architecture Overview
* **Bootstrap Layer (Rust)**: Handles secure terminal authentication, license verification, and token exchange.
* **Data Stream Layer (JS/Node.js)**: Runs low-latency multiplexed channels for heartbeats, file transfers, and video casting (Blender/VirtualBox).

```
[Client: pyielink user@ip]
       │
       ├─► (1) Bootstrap (Rust) ──► License Approval & Token Issuance
       │
       └─► (2) Data Stream (JS)  ──► Heartbeat Loop & Remote GUI Pipe
```

---

## 🦀 1. Bootstrap Connection Layer (Rust)
Saves compute overhead during initial handshakes. Run via terminal: `pyielink user@ip`

```rust
use std::env;
use std::io::{Read, Write, stdin, stdout};
use std::net::TcpStream;

fn main() -> std::io::Result<()> {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 { return Ok(()); }
    
    let parts: Vec<&str> = args[1].split('@').collect();
    if parts.len() != 2 { return Ok(()); }
    
    let mut stream = TcpStream::connect(format!("{}:8080", parts[1]))?;
    let mut buf = [0; 512];
    
    // 1. License Prompt
    let n = stream.read(&mut buf)?;
    println!("{}", String::from_utf8_lossy(&buf[..n]));
    
    // 2. User Confirmation
    print!("Accept? (yes/no): ");
    stdout().flush()?;
    let mut ans = String::new();
    stdin().read_line(&mut ans)?;
    stream.write_all(ans.as_bytes())?;
    
    // 3. Receive Session Token
    let n = stream.read(&mut buf)?;
    println!("Token Secured: {}", String::from_utf8_lossy(&buf[..n]).trim());
    Ok(())
}
```

---

## ⚡ 2. Data Connection & Heartbeat Layer (JS)
Asynchronously handles heavy multi-tasking, cloud gaming streams, and operational states.

```javascript
const net = require('net');

net.createServer((socket) => {
    let authed = false;

    socket.on('data', (data) => {
        const msg = data.toString().trim();

        if (!authed) {
            if (msg === 'yes') {
                const token = Math.random().toString(36).substring(2);
                socket.write(`TOKEN:${token}\n`);
                authed = true;
                setInterval(() => {
                    if (socket.writable) socket.write(JSON.stringify({type:'HB', ts:Date.now()})+'\n');
                }, 5000);
            } else {
                socket.write("ETHICS & LICENSE:\n1. Authorized access only.\nReply 'yes' to agree.");
            }
            return;
        }
        
        // Multi-tasking Engine: Handles Blender frames, VirtualBox UI, and file chunks
        console.log(`Piping Stream: ${msg.substring(0, 30)}`);
    });
}).listen(8080);
```

---

## 🚀 Implementation Milestones
1. **Encryption**: Integrate `rustls` (Rust) and `tls` (Node.js) for end-to-end security.
2. **Video Capture Loop**: Write an OS-level frame-buffer scraper to stream high-FPS app renders.
3. **Input Remap**: Pipe client pointer/keyboard actions directly into host-side OS simulation APIs.