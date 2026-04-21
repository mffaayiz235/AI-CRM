from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

app = FastAPI()

# CORS (safe)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data model
class Interaction(BaseModel):
    doctor_name: str
    notes: str
    interaction_type: str

# In-memory DB
db = []

# AI Agent (simple logic)
def ai_agent(data):
    text = data.notes.lower()

    sentiment = "Neutral"
    if "good" in text:
        sentiment = "Positive"
    elif "bad" in text:
        sentiment = "Negative"

    follow_up = "Schedule next meeting"

    product = "Vitamin Supplement"
    if "pain" in text:
        product = "Pain Relief Tablet"

    summary = f"{data.doctor_name}: {data.notes}"

    return {
        "doctor_name": data.doctor_name,
        "interaction_type": data.interaction_type,
        "summary": summary,
        "sentiment": sentiment,
        "follow_up": follow_up,
        "product": product
    }

# APIs
@app.post("/log")
def log(data: Interaction):
    result = ai_agent(data)
    db.append(result)
    return {"message": "Logged"}

@app.get("/all")
def get_all():
    return db

@app.delete("/delete/{id}")
def delete(id: int):
    if id < len(db):
        db.pop(id)
        return {"message": "Deleted"}
    return {"error": "Invalid ID"}

# Frontend UI (HTML + JS)
@app.get("/", response_class=HTMLResponse)
def home():
    return """
<!DOCTYPE html>
<html>
<head>
<title>AI CRM</title>
<style>
body { font-family: Arial; padding:20px; }
input, textarea, select { width:100%; margin:5px 0; padding:8px; }
button { padding:10px; background:#007bff; color:white; border:none; }
.card { border:1px solid #ccc; padding:10px; margin-top:10px; }
</style>
</head>

<body>

<h1>AI CRM - HCP Interaction</h1>

<input id="doctor" placeholder="Doctor Name">

<select id="type">
<option>Visit</option>
<option>Call</option>
<option>Email</option>
</select>

<textarea id="notes" placeholder="Enter notes"></textarea>

<button onclick="submitData()">Submit</button>

<h2>Interactions</h2>
<div id="list"></div>

<script>
async function loadData() {
    const res = await fetch('/all');
    const data = await res.json();

    let html = "";
    data.forEach((item, i) => {
        html += `
        <div class="card">
            <b>${item.doctor_name}</b><br>
            Type: ${item.interaction_type}<br>
            ${item.summary}<br>
            Sentiment: ${item.sentiment}<br>
            Follow-up: ${item.follow_up}<br>
            Product: ${item.product}<br>
            <button onclick="deleteItem(${i})">Delete</button>
        </div>`;
    });

    document.getElementById("list").innerHTML = html;
}

async function submitData() {
    const doctor = document.getElementById("doctor").value;
    const notes = document.getElementById("notes").value;
    const type = document.getElementById("type").value;

    await fetch('/log', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({
            doctor_name: doctor,
            notes: notes,
            interaction_type: type
        })
    });

    loadData();
}

async function deleteItem(id) {
    await fetch('/delete/' + id, {method:'DELETE'});
    loadData();
}

loadData();
</script>

</body>
</html>
"""