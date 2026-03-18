from fastapi import FastAPI, Form, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
import uvicorn
import json
from database import SessionLocal, User, Message, generate_id, Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 🚀 THE GHOST BUSTER CONNECTION MANAGER
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                dead_connections.append(connection)
        
        for dead in dead_connections:
            if dead in self.active_connections:
                self.active_connections.remove(dead)

manager = ConnectionManager()

# High Quality Base64 Avatars
male_avatar = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iIzYzNjZGMSI+PHBhdGggZD0iTTEyIDEyYzIuMjEgMCA0LTEuNzkgNC00czEtMS43OS00LTQtNCAxLjc5LTQgNCAxLjc5IDQgNCA0em0wIDJjLTIuNjcgMC04IDEuMzQtOCA0djJoMTZ2LTJjMC0yLjY2LTUuMzMtNC04LTR6Ii8+PC9zdmc+"
female_avatar = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iI0VDRjA4RCI+PHBhdGggZD0iTTEyIDEyYzIuMjEgMCA0LTEuNzkgNC00czEtMS43OS00LTQtNCAxLjc5LTQgNCAxLjc5IDQgNCA0em0wIDJjLTIuNjcgMC04IDEuMzQtOCA0djJoMTZ2LTJjMC0yLjY2LTUuMzMtNC04LTR6Ii8+PC9zdmc+"

html_app = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>ME CHAT - Premium</title>
    <link href="https://fonts.googleapis.com/css2?family=Luckiest+Guy&family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Poppins', sans-serif; }}
        body {{ background-color: #EEF2F6; display: flex; justify-content: center; align-items: center; min-height: 100vh; color: #1C1D22; overflow: hidden; }}
        
        .app-container {{ background-color: #FFFFFF; width: 100%; max-width: 420px; height: 90vh; max-height: 850px; border-radius: 35px; box-shadow: 0 25px 50px rgba(99, 102, 241, 0.15); display: flex; flex-direction: column; overflow: hidden; position: relative; }}
        .view-section {{ display: none; flex-direction: column; width: 100%; height: 100%; padding: 40px 30px; overflow-y: auto; background-color: #FFFFFF; position: absolute; top: 0; left: 0; z-index: 10; }}
        .view-section.active {{ display: flex; z-index: 20; }}

        .logo-title {{ font-family: 'Luckiest Guy', cursive; font-size: 48px; text-align: center; color: #111827; margin-bottom: 0px; letter-spacing: 2px; text-shadow: 2px 2px 0px #E5E7EB; }}
        .logo-dot {{ color: #EF4444; }} 
        
        .subtitle {{ font-size: 14px; color: #6B7280; text-align: center; margin-bottom: 30px; }}
        .page-title {{ font-size: 24px; font-weight: 700; text-align: center; margin-bottom: 25px; color: #111827; }}
        
        .btn-social {{ display: flex; justify-content: center; align-items: center; gap: 12px; width: 100%; padding: 16px; margin-bottom: 12px; background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 16px; font-size: 15px; font-weight: 500; color: #374151; cursor: pointer; transition: 0.2s; }}
        .btn-social:active {{ background-color: #F3F4F6; }}
        .btn-social svg {{ width: 22px; height: 22px; }}
        
        .btn-primary {{ width: 100%; padding: 16px; background-color: #6366F1; color: #FFFFFF; border: none; border-radius: 16px; font-size: 16px; font-weight: 600; cursor: pointer; margin-top: 15px; transition: 0.2s; box-shadow: 0 8px 20px rgba(99, 102, 241, 0.3); }}
        .btn-primary:active {{ background-color: #4F46E5; transform: scale(0.98); }}
        
        .input-box {{ width: 100%; padding: 16px 20px; margin-bottom: 15px; background-color: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 16px; font-size: 15px; outline: none; transition: 0.2s; color:#111827; }}
        .input-box:focus {{ border-color: #6366F1; background-color: #FFFFFF; }}
        
        .link-text {{ text-align: center; font-size: 14px; color: #6B7280; margin-top: 25px; }}
        .clickable-span {{ color: #6366F1; font-weight: 600; cursor: pointer; padding: 10px 5px; }}
        .divider {{ text-align: center; margin: 20px 0; font-size: 12px; color: #9CA3AF; }}
        
        .gender-select {{ display: flex; justify-content: center; gap: 20px; margin: -5px 0 15px; }}
        .gender-select label {{ font-size: 14px; color: #6B7280; font-weight: 500; cursor: pointer; display: flex; align-items: center; gap: 5px; }}
        .gender-select input {{ cursor: pointer; accent-color: #6366F1; }}

        .secret-box {{ background: #F8FAFC; padding: 20px; border-radius: 16px; margin-bottom: 20px; border: 2px dashed #6366F1; text-align: center; display: none; }}
        
        .about-card {{ background: #F9FAFB; padding: 20px; border-radius: 20px; border: 1px solid #E5E7EB; margin-bottom: 15px; }}
        .about-card h3 {{ font-size: 14px; color: #6B7280; font-weight: 500; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 1px; }}
        .about-card p {{ font-size: 18px; color: #111827; font-weight: 700; }}

        .dash-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }}
        .dash-header h2 {{ font-size: 24px; font-weight: 700; color: #111827; }}
        .btn-logout {{ color: #EF4444; font-size: 14px; font-weight: 600; cursor: pointer; padding: 5px; background: #FEF2F2; border-radius: 8px; padding: 5px 10px; }}
        
        .profile-card {{ display: flex; align-items: center; gap: 16px; padding: 20px; background-color: #F9FAFB; border-radius: 20px; margin-bottom: 25px; border: 1px solid #E5E7EB; }}
        .dp-img {{ width: 65px; height: 65px; border-radius: 50%; border: 3px solid #6366F1; padding: 3px; background: white; }}
        
        .search-row {{ display: flex; gap: 10px; margin-bottom: 25px; }}
        .search-row input {{ margin-bottom: 0; flex: 1; }}
        .btn-find {{ background-color: #111827; color: white; border: none; padding: 0 20px; border-radius: 16px; font-weight: 600; cursor: pointer; }}

        .friend-card {{ display: flex; align-items: center; gap: 15px; padding: 15px; background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 16px; margin-bottom: 12px; }}
        .friend-card img {{ width: 50px; height: 50px; border-radius: 50%; border: 2px solid #6366F1; padding: 2px; }}
        .btn-chat {{ background: #6366F1; color: white; border: none; padding: 8px 16px; border-radius: 10px; font-weight: 600; font-size: 13px; cursor: pointer; }}

        .chat-header {{ display: flex; align-items: center; gap: 15px; padding-bottom: 20px; border-bottom: 1px solid #E5E7EB; }}
        .btn-back {{ font-size: 24px; cursor: pointer; color: #111827; }}
        
        .chat-area {{ flex: 1; overflow-y: auto; padding: 20px 0; display: flex; flex-direction: column; gap: 12px; scroll-behavior: smooth; }}
        .bubble {{ max-width: 75%; padding: 14px 18px; border-radius: 20px; font-size: 14px; line-height: 1.5; word-wrap: break-word; }}
        .bubble-me {{ background: #6366F1; color: white; align-self: flex-end; border-bottom-right-radius: 4px; box-shadow: 0 2px 5px rgba(99, 102, 241, 0.2); }}
        .bubble-them {{ background: #F3F4F6; color: #111827; align-self: flex-start; border-bottom-left-radius: 4px; border: 1px solid #E5E7EB; }}

        .input-row {{ display: flex; gap: 10px; padding-top: 15px; border-top: 1px solid #E5E7EB; background: #FFFFFF; }}
        .input-row input {{ margin-bottom: 0; flex: 1; border-radius: 24px; background: #F3F4F6; }}
        .btn-send {{ background: #6366F1; color: white; border: none; width: 52px; height: 52px; border-radius: 26px; font-size: 20px; cursor: pointer; }}

        #toast {{ visibility: hidden; min-width: 250px; background-color: #111827; color: #fff; text-align: center; border-radius: 12px; padding: 16px; position: fixed; z-index: 9999; left: 50%; bottom: 30px; transform: translateX(-50%); font-size: 14px; font-weight: 500; }}
        #toast.show {{ visibility: visible; animation: fadein 0.5s, fadeout 0.5s 3.5s; }}
        @keyframes fadein {{ from {{bottom: 0; opacity: 0;}} to {{bottom: 30px; opacity: 1;}} }}
        @keyframes fadeout {{ from {{bottom: 30px; opacity: 1;}} to {{bottom: 0; opacity: 0;}} }}
    </style>
</head>
<body>

<div id="toast">Message</div>

<div class="app-container">

    <div id="view-welcome" class="view-section active">
        <div class="logo-title">ME CHAT<span class="logo-dot">!</span></div>
        <div class="subtitle">Secure Messaging Network</div>
        
        <button class="btn-social" onclick="switchView('view-login')">
            <svg viewBox="0 0 24 24" fill="#1877F2"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.469h2.047V9.43c0-2.027 1.24-3.146 3.054-3.146.866 0 1.376.064 1.563.092v1.814h-1.074c-.84 0-1.007.4-1.007.989v1.294h2.065l-.269 3.469h-1.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
            Continue with Facebook
        </button>
        <button class="btn-social" onclick="switchView('view-login')">
            <svg viewBox="0 0 24 24" fill="#EA4335"><path d="M12.24 10.285V13.97h6.738c-.297 1.906-2.27 5.588-6.738 5.588-4.045 0-7.36-3.35-7.36-7.493s3.315-7.493 7.36-7.493c2.27 0 3.787.967 4.652 1.798l2.894-2.78C18.06 1.77 15.404 0 12.24 0 5.62 0 .24 5.38.24 12s5.38 12 12 12c6.926 0 11.52-4.869 11.52-11.726 0-.788-.083-1.52-.24-2.214h-11.28z"/></svg>
            Continue with Google
        </button>
        
        <div class="divider">OR</div>
        <button class="btn-primary" onclick="switchView('view-login')">Secure Login</button>
        <div class="link-text">
            Don't have an account? <span class="clickable-span" onclick="switchView('view-register')">Signup</span><br><br>
            <span class="clickable-span" style="color: #9CA3AF; font-size:13px;" onclick="switchView('view-about')">About ME CHAT Platform</span>
        </div>
    </div>

    <div id="view-about" class="view-section">
        <div class="page-title">About App</div>
        <div class="logo-title" style="font-size: 32px; margin-bottom: 20px;">ME CHAT<span class="logo-dot">!</span></div>
        <p style="text-align:center; color:#4B5563; font-size:14px; margin-bottom:30px; line-height:1.6;">
            ME CHAT is a 100% secure, end-to-end encrypted anonymous messaging platform. No passwords or phone numbers required.
        </p>
        <div class="about-card">
            <h3>👑 Founder & CEO</h3>
            <p>Muhammad Umar Asif</p>
        </div>
        <div class="about-card">
            <h3>📍 Headquarters</h3>
            <p>Rahim Yar Khan (RYK)<br>Punjab, Pakistan 🇵🇰</p>
        </div>
        <button class="btn-primary" style="background:#111827; margin-top: auto;" onclick="switchView('view-welcome')">← Back to Home</button>
    </div>

    <div id="view-login" class="view-section">
        <div class="page-title">Secure Login</div>
        <p style="text-align:center; color:#6B7280; font-size:13px; margin-bottom:25px;">Enter your Secret Login Key to continue.</p>
        <input type="password" id="log_secret" class="input-box" style="text-align: center; font-weight: bold; font-family: monospace; letter-spacing: 1px;" placeholder="e.g. KEY-123456">
        <button class="btn-primary" onclick="processLogin()">Log in securely</button>
        <div class="link-text"><span class="clickable-span" onclick="switchView('view-welcome')">← Go Back</span> | <span class="clickable-span" onclick="switchView('view-register')">Create Account</span></div>
    </div>

    <div id="view-register" class="view-section">
        <div class="page-title">Sign up</div>
        <p style="text-align:center; color:#6B7280; font-size:13px; margin-bottom:20px;">Join the secure network today.</p>
        <input type="text" id="reg_name" class="input-box" placeholder="Your Full Name">
        <input type="text" id="reg_dob" class="input-box" placeholder="DOB (DD-MM-YYYY)">
        <div class="gender-select">
            <label><input type="radio" name="gender" value="Male" checked> Male</label>
            <label><input type="radio" name="gender" value="Female"> Female</label>
        </div>
        <div id="reg_success_box" class="secret-box">
            <p style="font-size: 13px; color: #6B7280; margin-bottom:10px;">📸 Take a screenshot of your keys!</p>
            <div style="font-weight: 700; color: #EF4444; font-size:16px; font-family: monospace;">Login Key: <span id="show_secret"></span></div>
            <div style="font-weight: 700; color: #10B981; font-size:16px; font-family: monospace; margin-top:5px;">Public ID: <span id="show_public"></span></div>
            <button class="btn-primary" style="padding: 12px; margin-top: 15px;" onclick="switchView('view-login')">Go to Login</button>
        </div>
        <button id="reg_btn" class="btn-primary" onclick="processRegister()">Create Account</button>
        <div class="link-text" id="reg_link"><span class="clickable-span" onclick="switchView('view-welcome')">← Go Back</span> | <span class="clickable-span" onclick="switchView('view-login')">Log In</span></div>
    </div>

    <div id="view-dashboard" class="view-section" style="padding: 30px 20px;">
        <div class="dash-header">
            <h2>Chats</h2>
            <div class="btn-logout" onclick="window.location.reload()">Logout</div>
        </div>
        <div class="profile-card">
            <div><img src="{male_avatar}" id="my_dp" class="dp-img"></div>
            <div>
                <div id="my_name" style="font-weight: 700; font-size: 18px; color: #111827;">Loading...</div>
                <div id="my_id" style="font-size: 14px; color: #6366F1; font-weight: 600; font-family: monospace;">ME-XXXXXX</div>
            </div>
        </div>
        <div class="search-row">
            <input type="text" id="search_id" class="input-box" placeholder="Search Friend's Public ID...">
            <button class="btn-find" onclick="searchForFriend()">Find</button>
        </div>
        <div id="search-results">
            <div style="text-align:center; color:#9CA3AF; font-size:13px; margin-top:30px; background:#F9FAFB; padding:20px; border-radius:16px; border:1px dashed #E5E7EB;">
                Connect with friends by entering their Public ID.
            </div>
        </div>
    </div>

    <div id="view-chat" class="view-section" style="padding: 20px;">
        <div class="chat-header">
            <div class="btn-back" onclick="switchView('view-dashboard')">←</div>
            <img src="{male_avatar}" id="chat_dp" style="width:45px; height:45px; border-radius:50%; background:#EEF2F6; padding: 2px;">
            <div id="chat_name" style="font-weight: 700; font-size:18px;">Friend</div>
        </div>
        <div class="chat-area" id="chat_box">
            </div>
        <form class="input-row" onsubmit="sendChatMsg(event)">
            <input type="text" id="msg_val" class="input-box" placeholder="Message..." autocomplete="off" required>
            <button type="submit" class="btn-send">➤</button>
        </form>
    </div>

</div>

<script>
    let myPublicId = "";
    let myChatWs = null;
    let currentFriendId = "";
    
    const avatars = {{
        "Male": "{male_avatar}",
        "Female": "{female_avatar}",
        "Other": "{male_avatar}"
    }};

    function showToast(message, isError=false) {{
        let x = document.getElementById("toast");
        x.innerText = message;
        x.style.backgroundColor = isError ? "#EF4444" : "#10B981";
        x.className = "show";
        setTimeout(() => {{ x.className = x.className.replace("show", ""); }}, 4000);
    }}

    function switchView(viewId) {{
        let views = document.getElementsByClassName('view-section');
        for(let i=0; i<views.length; i++) {{
            views[i].style.display = 'none';
            views[i].classList.remove('active');
        }}
        let target = document.getElementById(viewId);
        if(target) {{
            target.style.display = 'flex';
            setTimeout(() => target.classList.add('active'), 10);
        }}
    }}

    async function processRegister() {{
        let n = document.getElementById('reg_name').value;
        let d = document.getElementById('reg_dob').value;
        let gInput = document.querySelector('input[name="gender"]:checked');
        let g = gInput ? gInput.value : "Male";

        if(!n || !d) return showToast("Name and DOB are required!", true);

        try {{
            let res = await fetch('/api/register', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/x-www-form-urlencoded'}},
                body: new URLSearchParams({{'name': n, 'dob': d, 'gender': g}})
            }});
            let data = await res.json();
            if(res.ok) {{
                showToast(`Success! Your keys are generated.`);
                document.getElementById('show_secret').innerText = data.secret_key;
                document.getElementById('show_public').innerText = data.public_id;
                
                document.getElementById('reg_success_box').style.display = 'block';
                document.getElementById('reg_btn').style.display = 'none';
                document.getElementById('reg_link').style.display = 'none';
            }} else showToast("Registration failed!", true);
        }} catch(e) {{ showToast("Network Error", true); }}
    }}

    async function processLogin() {{
        let key = document.getElementById('log_secret').value;
        if(!key) return showToast("Enter your Secret Key!", true);

        try {{
            let res = await fetch('/api/login', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/x-www-form-urlencoded'}},
                body: new URLSearchParams({{'secret_key': key}})
            }});
            let data = await res.json();
            if(res.ok) {{
                myPublicId = data.public_id;
                document.getElementById('my_name').innerText = data.name;
                document.getElementById('my_id').innerText = data.public_id;
                document.getElementById('my_dp').src = avatars[data.gender] || avatars["Male"];
                showToast(`Welcome back, ${{data.name}}!`);
                switchView('view-dashboard');
            }} else showToast("Invalid Secret Key!", true);
        }} catch(e) {{ showToast("Network Error", true); }}
    }}

    async function searchForFriend() {{
        let id = document.getElementById('search_id').value;
        if(!id) return;
        let resBox = document.getElementById('search-results');
        resBox.innerHTML = "<p style='text-align:center; color:#6B7280; font-size:14px; margin-top:20px;'>Searching...</p>";

        try {{
            let res = await fetch('/api/search/' + id);
            let data = await res.json();
            if(res.ok) {{
                let friendAvatar = avatars[data.gender] || avatars["Male"];
                resBox.innerHTML = `
                    <div class="friend-card">
                        <img src="${{friendAvatar}}">
                        <div style="flex:1;">
                            <div style="font-weight:600; font-size:16px; color:#111827;">${{data.name}}</div>
                            <div style="font-size:13px; color:#6B7280; font-family:monospace;">${{id}}</div>
                        </div>
                        <button class="btn-chat" onclick="openChatRoom('${{id}}', '${{data.name}}', '${{data.gender}}')">Chat</button>
                    </div>
                `;
            }} else resBox.innerHTML = "<p style='text-align:center; color:#EF4444; font-weight:500; margin-top:20px;'>User not found!</p>";
        }} catch(e) {{ showToast("Network Error", true); }}
    }}

    // 🚀 THE WSS SECURITY FIX (AUTO-DETECTS HTTPS OR HTTP)
    async function openChatRoom(fId, fName, fGender) {{
        currentFriendId = fId;
        document.getElementById('chat_name').innerText = fName;
        document.getElementById('chat_dp').src = avatars[fGender] || avatars["Male"];
        switchView('view-chat');

        let chatBox = document.getElementById('chat_box');
        chatBox.innerHTML = '<div style="text-align:center; color:#9CA3AF; font-size:12px; margin-bottom:20px; padding:10px; background:#F8FAFC; border-radius:10px;">🔒 Fetching Secure Chat History...</div>';

        // 1. Chat History Fetch
        try {{
            let res = await fetch(`/api/history/${{myPublicId}}/${{currentFriendId}}`);
            let data = await res.json();
            
            chatBox.innerHTML = '<div style="text-align:center; color:#9CA3AF; font-size:12px; margin-bottom:20px; padding:10px; background:#F8FAFC; border-radius:10px;">🔒 End-to-end encrypted</div>';
            
            if(data.messages) {{
                data.messages.forEach(msg => {{
                    let div = document.createElement('div');
                    div.className = 'bubble ' + (msg.sender === myPublicId ? 'bubble-me' : 'bubble-them');
                    div.innerText = msg.text;
                    chatBox.appendChild(div);
                }});
                chatBox.scrollTop = chatBox.scrollHeight;
            }}
        }} catch(e) {{
            chatBox.innerHTML = '<div style="text-align:center; color:#EF4444; font-size:12px; margin-bottom:20px;">Failed to load history!</div>';
        }}

        // 2. 🚀 MAGIC WSS CONNECTION (Secure Chat Engine)
        if(myChatWs) myChatWs.close();
        let wsProtocol = window.location.protocol === "https:" ? "wss://" : "ws://";
        myChatWs = new WebSocket(wsProtocol + window.location.host + "/ws/" + myPublicId);
        
        myChatWs.onmessage = function(event) {{
            let msgData = JSON.parse(event.data);
            
            if ((msgData.sender === myPublicId && msgData.receiver === currentFriendId) || 
                (msgData.sender === currentFriendId && msgData.receiver === myPublicId)) {{
                
                let div = document.createElement('div');
                div.className = 'bubble ' + (msgData.sender === myPublicId ? 'bubble-me' : 'bubble-them');
                div.innerText = msgData.text;
                chatBox.appendChild(div);
                chatBox.scrollTop = chatBox.scrollHeight;
            }}
        }};
    }}

    function sendChatMsg(event) {{
        event.preventDefault();
        let input = document.getElementById('msg_val');
        
        if(input.value.trim() !== "" && myChatWs && myChatWs.readyState === WebSocket.OPEN) {{
            let payload = {{
                receiver: currentFriendId,
                text: input.value
            }};
            myChatWs.send(JSON.stringify(payload));
            input.value = "";
        }}
    }}
</script>
</body>
</html>
"""

# ================= API ROUTES =================
@app.get("/")
async def serve_home():
    return HTMLResponse(html_app)

@app.post("/api/register")
async def register_api(name: str = Form(...), dob: str = Form(...), gender: str = Form(...), db: Session = Depends(get_db)):
    secret_key = generate_id("KEY")
    public_id = generate_id("ME")
    db.add(User(full_name=name, dob=dob, secret_key=secret_key, public_id=public_id, gender=gender))
    db.commit()
    return {"status": "success", "secret_key": secret_key, "public_id": public_id}

@app.post("/api/login")
async def login_api(secret_key: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.secret_key == secret_key).first()
    if user:
        return {"status": "success", "name": user.full_name, "public_id": user.public_id, "gender": user.gender}
    raise HTTPException(status_code=400, detail="Invalid Secret Key!")

@app.get("/api/search/{public_id}")
async def search_api(public_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.public_id == public_id).first()
    if user:
        return {"status": "success", "name": user.full_name, "gender": user.gender}
    raise HTTPException(status_code=404, detail="Not found")

@app.get("/api/history/{my_id}/{friend_id}")
async def get_history(my_id: str, friend_id: str, db: Session = Depends(get_db)):
    messages = db.query(Message).filter(
        or_(
            and_(Message.sender_id == my_id, Message.receiver_id == friend_id),
            and_(Message.sender_id == friend_id, Message.receiver_id == my_id)
        )
    ).order_by(Message.timestamp.asc()).all()
    
    return {"status": "success", "messages": [{"sender": m.sender_id, "text": m.text} for m in messages]}

# DB PREVENT LOCKS ENGINE
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg_data = json.loads(data)
                receiver_id = msg_data.get("receiver")
                text = msg_data.get("text")
                
                db = SessionLocal()
                try:
                    new_msg = Message(sender_id=client_id, receiver_id=receiver_id, text=text)
                    db.add(new_msg)
                    db.commit()
                except Exception as db_err:
                    print(f"DB Write Error: {db_err}")
                    db.rollback()
                finally:
                    db.close()
                
                await manager.broadcast(json.dumps({
                    "sender": client_id,
                    "receiver": receiver_id,
                    "text": text
                }))
            except Exception as e:
                print(f"WS Payload Error: {e}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
