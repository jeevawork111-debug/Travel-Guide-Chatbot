import streamlit as st
import os
from groq import Groq
import time
from datetime import datetime
import json
from pathlib import Path
from PIL import Image
import base64
import io


from langchain_community.document_loaders import CSVLoader, PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


docs = []

# Load CSV safely
try:
    csv_loader = CSVLoader(file_path="travel.csv")
    csv_docs = csv_loader.load()
    docs.extend(csv_docs)
    print("CSV loaded ✅")
except Exception as e:
    print("CSV error:", e)

# Load PDF safely (IMPORTANT)
try:
    pdf_loader = PyPDFLoader("travel.pdf")
    pdf_docs = pdf_loader.load()
    docs.extend(pdf_docs)
    print("PDF loaded ✅")
except Exception as e:
    print("PDF skipped ❌ :", e)

print(f"Total documents loaded: {len(docs)}")

# Embeddings
embeddings = HuggingFaceEmbeddings()

# Vector DB
db = FAISS.from_documents(docs, embeddings)

def rag_search(query):
    results = db.similarity_search(query, k=2)
    return "\n".join([r.page_content for r in results])


# ════════════════════════════════════════════════════════════════════════════════════
# 🏨 TRAVEL GUIDE CHATBOT - PLATFORM BOOKING ASSISTANT
# ════════════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="🏨 Travel Guide Chatbot | Hotels, Flights, Trains, Buses & Tours",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ════════════════════════════════════════════════════════════════════════════════════
# 🎨 PREMIUM CSS STYLING FOR TRAVEL THEME
# ════════════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
        font-family: 'Inter', sans-serif;
    }
 1 /* Travel-themed Light Background */
   2 .stApp {
   3     background: linear-gradient(-45deg, #e0f2f7, #c6e9f1, #addbe8, #e0f2f7);
   4     background-size: 400% 400%;
   5     animation: gradientShift 15s ease infinite;
   6 }


    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .main {
        background: rgba(20, 15, 10, 0.92) !important;
        border-radius: 25px;
        margin: 15px;
        padding: 25px;
        backdrop-filter: blur(20px);
        border: 2px solid rgba(255, 165, 0, 0.5) !important;
        box-shadow: 0 20px 60px rgba(255, 165, 0, 0.2), 
                    0 0 40px rgba(255, 200, 0, 0.1) !important;
    }

    .stChatMessage {
        background: transparent;
        padding: 8px 0;
    }

    [data-testid="chatMessage"][aria-label="user"] {
        background: linear-gradient(135deg, #ff9800 0%, #ffb74d 50%, #ffd54f 100%);
        border-radius: 20px;
        padding: 14px 18px;
        margin: 10px 0;
        margin-left: 50px;
        color: #000;
        box-shadow: 0 10px 35px rgba(255, 152, 0, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.5);
        animation: slideInRight 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
        font-weight: 600;
        line-height: 1.6;
        max-width: 85%;
    }

    [data-testid="chatMessage"][aria-label="assistant"] {
        background: linear-gradient(135deg, rgba(40, 25, 15, 0.95) 0%, rgba(50, 30, 20, 0.95) 100%);
        border-radius: 20px;
        padding: 14px 18px;
        margin: 10px 0;
        margin-right: 50px;
        color: #ffd54f;
        box-shadow: 0 10px 35px rgba(255, 165, 0, 0.3);
        border: 1px solid rgba(255, 165, 0, 0.6);
        animation: slideInLeft 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
        line-height: 1.7;
        max-width: 90%;
    }

    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(50px) translateY(10px) rotateX(10deg); }
        to { opacity: 1; transform: translateX(0) translateY(0) rotateX(0deg); }
    }

    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-50px) translateY(10px) rotateX(10deg); }
        to { opacity: 1; transform: translateX(0) translateY(0) rotateX(0deg); }
    }

    textarea {
        background: linear-gradient(135deg, rgba(255, 152, 0, 0.08) 0%, rgba(255, 200, 0, 0.08) 100%) !important;
        color: #ffd54f !important;
        border: 2px solid rgba(255, 165, 0, 0.6) !important;
        border-radius: 14px !important;
        padding: 14px 16px !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        transition: all 0.4s ease !important;
        box-shadow: 0 5px 20px rgba(255, 165, 0, 0.2) !important;
    }

    textarea:focus {
        box-shadow: 0 0 40px rgba(255, 165, 0, 0.6) !important;
        border-color: #ffb74d !important;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(60, 38, 20, 0.98) 0%, rgba(40, 25, 15, 0.95) 100%) !important;
        border-right: 3px solid rgba(255, 152, 0, 0.6);
    }

    .stSidebar .stMarkdown h2,
    .stSidebar .stMarkdown h3 {
        background: linear-gradient(135deg, #ff9800, #ffb74d, #ffd54f);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800;
        margin: 20px 0 14px 0;
    }

    .stButton button {
        background: linear-gradient(135deg, #ff9800 0%, #ffb74d 50%, #ffd54f 100%) !important;
        color: #000 !important;
        border-radius: 12px !important;
        padding: 12px 26px !important;
        font-weight: 700 !important;
        box-shadow: 0 10px 30px rgba(255, 152, 0, 0.4) !important;
        transition: all 0.3s ease !important;
    }

    .stButton button:hover {
        transform: translateY(-5px) scale(1.08) !important;
        box-shadow: 0 20px 50px rgba(255, 165, 0, 0.5) !important;
    }

    label, span, .stMarkdown {
        color: #ffffff !important;
    }

    .stInfo, .stSuccess {
        background: linear-gradient(135deg, rgba(255, 152, 0, 0.2), rgba(255, 200, 0, 0.15)) !important;
        border-left: 5px solid #ffb74d !important;
        border-radius: 12px !important;
        padding: 16px !important;
    }

    .platform-card {
        background: linear-gradient(135deg, rgba(255, 152, 0, 0.1), rgba(255, 200, 0, 0.05)) !important;
        border: 2px solid rgba(255, 165, 0, 0.4) !important;
        border-radius: 12px !important;
        padding: 16px !important;
        margin: 12px 0 !important;
    }

    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(255, 152, 0, 0.5), rgba(255, 200, 0, 0.5), transparent);
        margin: 24px 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════════
# 🌍 TRAVEL PLATFORMS DATABASE
# ════════════════════════════════════════════════════════════════════════════════════

TRAVEL_PLATFORMS = {
    "Hotels": [
        {
            "name": "Booking.com",
            "description": "Global hotel booking platform with millions of properties, competitive rates, and no booking fees",
            "url": "https://www.booking.com",
            "icon": "🏨"
        },
        {
            "name": "MakeMyTrip",
            "description": "India's leading travel platform for hotels, flights, and packages with exclusive deals",
            "url": "https://www.makemytrip.com",
            "icon": "✈️"
        },
        {
            "name": "Goibibo",
            "description": "Popular Indian travel platform offering budget-friendly hotel and travel deals",
            "url": "https://www.goibibo.com",
            "icon": "🌟"
        }
    ],
    "Train Tickets": [
        {
            "name": "IRCTC",
            "description": "Official Indian Railways booking platform for train tickets across India",
            "url": "https://www.irctc.co.in",
            "icon": "🚂"
        }
    ],
    "Bus Tickets": [
        {
            "name": "RedBus",
            "description": "India's largest online bus booking platform with thousands of operators",
            "url": "https://www.redbus.in",
            "icon": "🚌"
        }
    ],
    "Flight Tickets": [
        {
            "name": "MakeMyTrip Flights",
            "description": "Comprehensive flight booking with all major airlines and competitive pricing",
            "url": "https://www.makemytrip.com/flights",
            "icon": "✈️"
        },
        {
            "name": "Cleartrip",
            "description": "Popular flight booking platform with real-time prices and instant confirmations",
            "url": "https://www.cleartrip.com",
            "icon": "🛫"
        }
    ],
    "Tourist Places": [
        {
            "name": "TripAdvisor",
            "description": "World's largest travel community with reviews, photos, and booking for attractions",
            "url": "https://www.tripadvisor.in",
            "icon": "🗺️"
        }
    ]
}

# ════════════════════════════════════════════════════════════════════════════════════
# 💾 CHAT HISTORY FUNCTIONS
# ════════════════════════════════════════════════════════════════════════════════════

def create_history_directory():
    """Create chat history directory"""
    history_dir = Path("travel_guide_history")
    history_dir.mkdir(exist_ok=True)
    return history_dir

def load_conversations_metadata():
    """Load conversation history"""
    history_dir = create_history_directory()
    conversations = {}
    
    for file in sorted(history_dir.glob("conversation_*.json"), reverse=True)[:20]:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                conv_id = file.stem.replace("conversation_", "")
                conversations[conv_id] = {
                    "title": data.get("title", "Untitled"),
                    "timestamp": data.get("timestamp", ""),
                    "messages_count": len(data.get("messages", [])),
                    "file": file
                }
        except:
            pass
    
    return conversations

def create_new_conversation():
    """Create a new conversation"""
    conv_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    st.session_state.current_conversation_id = conv_id
    st.session_state.messages = [{
        "role": "assistant",
        "content": "🏨 **Welcome to Travel Guide Chatbot!** ✈️\n\nI'm here to help you with:\n\n🏨 **Hotel Booking** - Find and book hotels worldwide\n✈️ **Flight Tickets** - Compare and book flights\n🚂 **Train Tickets** - Book trains across India\n🚌 **Bus Tickets** - Reserve bus seats easily\n🗺️ **Tourist Places** - Discover attractions and reviews\n📋 **Trip Planning** - Get personalized travel itineraries\n\n**How I can help:**\n- Show trusted booking platforms with direct links\n- Personalize recommendations based on your city/destination\n- Help plan your complete trip\n- Answer all your travel queries\n\n💡 Example queries:\n- \"Book hotel in Mumbai\"\n- \"Flight tickets Delhi to Bangalore\"\n- \"Plan a 5-day trip to Goa\"\n- \"Tourist places in Kerala\"\n\nWhat's your travel need today? Let's get started! 🌍"
    }]
    st.rerun()

def save_current_conversation():
    """Save conversation to file"""
    if len(st.session_state.messages) <= 1:
        return None
    
    history_dir = create_history_directory()
    conv_id = st.session_state.get("current_conversation_id", datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3])
    
    user_messages = [msg for msg in st.session_state.messages if msg["role"] == "user"]
    if user_messages:
        first_question = user_messages[0]["content"][:50] + ("..." if len(user_messages[0]["content"]) > 50 else "")
    else:
        first_question = "Travel Chat"
    
    data = {
        "id": conv_id,
        "title": first_question,
        "timestamp": datetime.now().isoformat(),
        "messages": st.session_state.messages,
        "model": st.session_state.get("model", "llama-3.1-8b-instant")
    }
    
    filepath = history_dir / f"conversation_{conv_id}.json"
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return filepath

def load_conversation(conv_id):
    """Load a saved conversation"""
    history_dir = create_history_directory()
    filepath = history_dir / f"conversation_{conv_id}.json"
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            st.session_state.current_conversation_id = conv_id
            st.session_state.messages = data.get("messages", [])
            st.rerun()
    except:
        st.error("Failed to load conversation")

def delete_conversation(conv_id):
    """Delete a conversation"""
    history_dir = create_history_directory()
    filepath = history_dir / f"conversation_{conv_id}.json"
    
    try:
        filepath.unlink()
        if st.session_state.get("current_conversation_id") == conv_id:
            create_new_conversation()
    except:
        st.error("Failed to delete")

# ════════════════════════════════════════════════════════════════════════════════════
# 🎯 PLATFORM SUGGESTION FUNCTIONS
# ════════════════════════════════════════════════════════════════════════════════════

def format_platform_suggestion(category, platforms):
    """Format platform suggestions nicely"""
    output = f"\n### {TRAVEL_PLATFORMS[category][0]['icon']} {category.upper()}\n\n"
    
    for idx, platform in enumerate(platforms, 1):
        output += f"**{idx}. {platform['name']}**\n"
        output += f"   📝 {platform['description']}\n"
        output += f"   🔗 [{platform['url']}]({platform['url']})\n\n"
    
    return output

def get_platform_suggestions(user_query):
    """Extract travel needs and return relevant platforms"""
    query_lower = user_query.lower()
    suggestions = {}
    
    # Hotel booking detection
    if any(word in query_lower for word in ['hotel', 'room', 'accommodation', 'stay', 'book hotel', 'accommodation']):
        suggestions['Hotels'] = TRAVEL_PLATFORMS['Hotels']
    
    # Train booking detection
    if any(word in query_lower for word in ['train', 'railway', 'irctc', 'ticket', 'book train']):
        suggestions['Train Tickets'] = TRAVEL_PLATFORMS['Train Tickets']
    
    # Bus booking detection
    if any(word in query_lower for word in ['bus', 'coach', 'redbus', 'book bus']):
        suggestions['Bus Tickets'] = TRAVEL_PLATFORMS['Bus Tickets']
    
    # Flight booking detection
    if any(word in query_lower for word in ['flight', 'air', 'plane', 'book flight', 'fly', 'ticket']):
        suggestions['Flight Tickets'] = TRAVEL_PLATFORMS['Flight Tickets']
    
    # Tourist places detection
    if any(word in query_lower for word in ['tourist', 'attraction', 'place', 'visit', 'see', 'trip', 'itinerary', 'plan']):
        suggestions['Tourist Places'] = TRAVEL_PLATFORMS['Tourist Places']
    
    return suggestions

# ════════════════════════════════════════════════════════════════════════════════════

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "🏨 **Welcome to Travel Guide Chatbot!** ✈️\n\nI'm here to help with:\n\n🏨 Hotel Booking • ✈️ Flights • 🚂 Trains • 🚌 Buses • 🗺️ Tourist Places • 📋 Trip Planning\n\nWhat would you like to book or plan? 🌍"
    }]

if "current_conversation_id" not in st.session_state:
    st.session_state.current_conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]

# ════════════════════════════════════════════════════════════════════════════════════
# 🎨 HEADER
# ════════════════════════════════════════════════════════════════════════════════════

col1, col2, col3 = st.columns([0.2, 1, 0.2])
with col2:
    st.markdown("""
    <div style="text-align: center; padding: 25px 0;">
        <h1 style="
            background: linear-gradient(135deg, #ff9800, #ffb74d, #ffd54f, #ff9800);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 3em;
            font-weight: 900;
            margin: 0;
        ">🏨 Travel Guide Chatbot</h1>
        <p style="color: #ffb74d; font-size: 1.1em; margin-top: 8px;">
            Your <span style="color: #ffd54f; font-weight: 800;">Smart Travel Booking Assistant</span> 🌍
        </p>
        <div style="margin-top: 10px; display: flex; justify-content: center; gap: 12px;">
            <span style="background: rgba(255, 152, 0, 0.3); padding: 5px 12px; border-radius: 20px; color: #ffb74d; font-weight: 700; font-size: 11px;">✈️ Hotels</span>
            <span style="background: rgba(255, 152, 0, 0.3); padding: 5px 12px; border-radius: 20px; color: #ffb74d; font-weight: 700; font-size: 11px;">🚂 Trains</span>
            <span style="background: rgba(255, 152, 0, 0.3); padding: 5px 12px; border-radius: 20px; color: #ffb74d; font-weight: 700; font-size: 11px;">🚌 Buses</span>
            <span style="background: rgba(255, 152, 0, 0.3); padding: 5px 12px; border-radius: 20px; color: #ffb74d; font-weight: 700; font-size: 11px;">✈️ Flights</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

# ════════════════════════════════════════════════════════════════════════════════════
# 🎛️ SIDEBAR
# ════════════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    if st.button("➕ New Chat", use_container_width=True):
        create_new_conversation()
    
    st.divider()
    
    # Quick Links
    st.markdown("### 🔗 Quick Links")
    col_quick = st.columns(2)
    
    with col_quick[0]:
        if st.button("🏨 Hotels", use_container_width=True):
            st.session_state.quick_search = "hotel"
    with col_quick[1]:
        if st.button("✈️ Flights", use_container_width=True):
            st.session_state.quick_search = "flight"
    
    col_quick = st.columns(2)
    with col_quick[0]:
        if st.button("🚂 Trains", use_container_width=True):
            st.session_state.quick_search = "train"
    with col_quick[1]:
        if st.button("🚌 Buses", use_container_width=True):
            st.session_state.quick_search = "bus"
    
    st.divider()
    
    # Chat History
    st.markdown("### 📚 Recent Chats")
    conversations = load_conversations_metadata()
    
    if conversations:
        for conv_id, conv_data in list(conversations.items())[:10]:
            col_conv, col_del = st.columns([0.85, 0.15])
            
            with col_conv:
                title = conv_data["title"]
                if len(title) > 30:
                    title = title[:27] + "..."
                
                if st.button(f"💬 {title}", use_container_width=True, key=f"load_{conv_id}"):
                    load_conversation(conv_id)
            
            with col_del:
                if st.button("🗑️", key=f"del_{conv_id}"):
                    delete_conversation(conv_id)
                    st.rerun()
    else:
        st.info("No chat history yet", icon='📝')
    
    st.divider()
    
    # API Configuration
    st.markdown("### ⚙️ Settings")
    
    if 'GROQ_API_KEY' in st.secrets:
        st.success('✅ API Key Set', icon='🔐')
        groq_api = st.secrets['GROQ_API_KEY']
    else:
        groq_api = st.text_input('API Key:', type='password', placeholder='gsk_••••••')
        if groq_api and groq_api.startswith('gsk_'):
            st.success('✅ Valid Key!', icon='✨')
    
    os.environ['GROQ_API_KEY'] = groq_api
    
    st.divider()
    
    # Model Selection
    st.markdown("### 🤖 AI Model")
    selected_model = st.selectbox(
        'Model:',
        options=['llama-3.1-8b-instant', 'llama-3.1-70b-versatile'],
        format_func=lambda x: '⚡ Fast (8B)' if x == 'llama-3.1-8b-instant' else '🧠 Advanced (70B)'
    )
    
    st.divider()
    
    if st.button("🧹 Clear Chat", use_container_width=True):
        st.session_state.messages = [{
            "role": "assistant",
            "content": "✨ Chat cleared! Ready for your next travel query. 🌍"
        }]
        st.rerun()
    
    st.divider()
    
    st.markdown("### ℹ️ About")
    st.info('🏨 Instant platform suggestions for hotels, flights, trains, buses & tourist places with direct booking links!', icon='⭐')

# ════════════════════════════════════════════════════════════════════════════════════
# 💬 CHAT INTERFACE
# ════════════════════════════════════════════════════════════════════════════════════

client = Groq(api_key=os.environ.get('GROQ_API_KEY', ''))

# Display Chat Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🏨" if message["role"] == "assistant" else "👤"):
        st.markdown(message["content"])

# Main Response Function
def generate_response():
    try:
        # Last user question
        user_query = st.session_state.messages[-1]["content"]

        # 🔥 RAG SEARCH (CSV + PDF)
        rag_context = rag_search(user_query)

        system_prompt = f"""
You are Travel Guide Chatbot.

Use this DATA if relevant:
{rag_context}

Rules:
- Simple English
- Friendly
- If city mentioned, explain using dataset first
- If not found in dataset, answer normally
- Help with hotels, trips, tourist places

User Question:
{user_query}
"""

        response = client.chat.completions.create(
            model=selected_model,
            messages=[{"role": "user", "content": system_prompt}],
            temperature=0.4,
            max_tokens=900
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# Chat Input
if prompt := st.chat_input("🏨 Book hotel, flights, plan trip... Ask anything! 🌍", disabled=not groq_api):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    
    # Get platform suggestions based on query
    platform_suggestions = get_platform_suggestions(prompt)
    
    with st.chat_message("assistant", avatar="🏨"):
        # Generate AI response
        with st.spinner("✈️ Finding travel options..."):
            ai_response = generate_response()
            st.markdown(ai_response)
        
        # Show platform suggestions if any
        if platform_suggestions:
            st.divider()
            st.markdown("### 🔗 **Booking Platforms** 👇")
            
            for category, platforms in platform_suggestions.items():
                st.markdown(f"**{category}:**")
                
                for idx, platform in enumerate(platforms, 1):
                    with st.container():
                        col_name, col_link = st.columns([0.4, 0.6])
                        
                        with col_name:
                            st.markdown(f"**{idx}. {platform['name']}**")
                        
                        with col_link:
                            st.markdown(f"[🔗 Open Website]({platform['url']})")
                        
                        st.caption(f"   📝 {platform['description']}")
                        st.divider()
            
            st.info("💡 Click the links above to book directly on official websites!", icon='👆')
    
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    save_current_conversation()

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid rgba(255, 165, 0, 0.2);">
    <p style="color: #ff9800; font-size: 12px;">
        🏨 Travel Guide Chatbot • Trusted Booking Platforms • Right to Your Destination 🌍✈️
    </p>
</div>
""", unsafe_allow_html=True)

