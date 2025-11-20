import os
import streamlit as st # type: ignore
import serial # type: ignore
import threading
import time
from serial.tools import list_ports # type: ignore
from streamlit.runtime.scriptrunner import add_script_run_ctx # type: ignore


STORY_FLOW = {
    0: {
        "video": r"C:\Users\Admin\Downloads\clips\intro.mp4",
        "text": "Hi there! Want a compliment? Press the button!",
        "actions": {"action": 1}
    },
    1: {
        "video": r"C:\Users\Admin\Downloads\clips\action1.mp4",
        "text": None, 
        "actions": {"action": 2}
    },
    2: {
        "video": r"C:\Users\Admin\Downloads\clips\action2.mp4", 
        "text": None,
        "actions": {"action": 3}
    },
    3: {
        "video": r"C:\Users\Admin\Downloads\clips\action3_closer.mp4",
        "text": None,
        "actions": {"action": 4}
    },
    4: {
        "video": r"C:\Users\Admin\Downloads\clips\action4.mp4",
        "text": None,
        "actions": {"action": 5}
    },
    5: {
        "video": r"C:\Users\Admin\Downloads\clips\action5.mp4",
        "text": None,
        "actions": {"action": 6, "exit": 10}
    },
    6: {
        "video": r"C:\Users\Admin\Downloads\clips\action6.mp4",
        "text": None,
        "actions": {"action": 7, "exit": 10}
    },
    7: {
        "video": r"C:\Users\Admin\Downloads\clips\action7.mp4",
        "text": None,
        "actions": {"action": 8, "exit": 10} 
    },
    8: {
        "video": r"C:\Users\Admin\Downloads\clips\action8.mp4",
        "text": None,
        "actions": {"action": 9, "exit": 10} 
    },
    9: {
        "video": r"C:\Users\Admin\Downloads\clips\action9.mp4",
        "text": None,
        "actions": {"action":10, "exit": 10} 
    },
    10: {
        "video": r"C:\Users\Admin\Downloads\clips\action10.mp4",
        "text": None,
        "actions": {"action": "final", "exit": "final"} 
    },
    "final": { 
         "video": None,
         "text": "Uncomfortable?\n\nWomen live this every day — online, in messages, in comments, in games, in apps.\nYou could not exit.\nNeither can they.",
         "actions": {}
    }
}

# settings
st.set_page_config(layout="centered", page_title="Flirty Box")

# design css
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pacifico&family=Quicksand:wght@500&display=swap');

    .stApp {
        background: linear-gradient(135deg, #FFF0F5 0%, #FFC0CB 100%);
    }
    
    .block-container {
        background-color: rgba(255, 255, 255, 0.7);
        border-radius: 30px;
        padding: 2rem !important;
        box-shadow: 0 4px 30px rgba(255, 105, 180, 0.2);
        border: 2px solid #FFF;
        max-width: 800px;
    }
    
    video {
        border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        width: 100%;
        margin-bottom: 10px;
    }
    
    h1 {
        font-family: 'Pacifico', cursive;
        color: #D63384;
        text-align: center;
        font-size: 3.5rem !important;
        text-shadow: 2px 2px 0px #FFD1DC;
        line-height: 1.3;
        margin-top: 10px;
    }
    
    p, em {
        font-family: 'Quicksand', sans-serif;
        color: #C71585;
        font-size: 1.8rem !important;
        text-align: center;
    }

    @keyframes pulse {
        0% { opacity: 0.5; transform: scale(0.95); }
        50% { opacity: 1; transform: scale(1.05); }
        100% { opacity: 0.5; transform: scale(0.95); }
    }
    
    .warning-text {
        font-family: 'Quicksand', sans-serif;
        color: #FF1493;
        font-weight: bold;
        font-size: 2rem;
        text-align: center;
        animation: pulse 2s infinite;
        margin-top: 20px;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# state
if 'current_state_id' not in st.session_state:
    st.session_state.current_state_id = 0
if 'last_physical_press' not in st.session_state:
    st.session_state.last_physical_press = None
if 'serial_thread_started' not in st.session_state:
    st.session_state.serial_thread_started = False
if 'serial_conn_obj' not in st.session_state:
    st.session_state.serial_conn_obj = None

# buttons
def read_from_serial(ser):
    while True:
        try:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if "BTN1" in line:
                    st.session_state.last_physical_press = "action"
                elif "BTN2" in line:
                    st.session_state.last_physical_press = "exit"
            time.sleep(0.05)
        except Exception:
            break

if not st.session_state.serial_thread_started:
    port_to_connect = 'COM3' 
    
    msg_place = st.empty()
    msg_place.info(f"Connecting to {port_to_connect}...")
    try:
        ser = serial.Serial(port_to_connect, 9600, timeout=1)
        st.session_state.serial_conn_obj = ser
        
        thread = threading.Thread(target=read_from_serial, args=(ser,), daemon=True)
        add_script_run_ctx(thread)
        thread.start()
        
        st.session_state.serial_thread_started = True
        msg_place.success("✨Connected✨")
        time.sleep(1)
        st.rerun()
    
    except Exception as e:
        msg_place.error(f"Error: {e}")
        st.stop()

# fow
current_state_data = STORY_FLOW.get(st.session_state.current_state_id)

if current_state_data:
    
    # video logic
    if "video" in current_state_data:
        video_path = current_state_data["video"]
        
        if video_path and os.path.exists(video_path):
            st.video(video_path, autoplay=True, muted=False)  
        elif video_path: 
            st.warning(f"Файл {video_path} не найден!")

    # text
    text_content = current_state_data.get('text')
    
    if text_content:
        text_placeholder = st.empty()
        formatted_text = text_content.replace('\n', '\n\n')
        text_placeholder.markdown(f"<h1>{formatted_text}</h1>", unsafe_allow_html=True)

        # sub text
        if 'post_display' in current_state_data:
            full_text = formatted_text
            for delay, line in current_state_data['post_display']:
                time.sleep(delay)
                full_text += f"\n\n*{line}*"
                text_placeholder.markdown(f"<h1>{full_text}</h1>", unsafe_allow_html=True)

    # waiting for the action
    if current_state_data['actions']:
        
        warning_placeholder = st.empty()
        
        st.session_state.last_physical_press = None 
        if st.session_state.serial_conn_obj:
            st.session_state.serial_conn_obj.reset_input_buffer()
        
        start_wait_time = time.time()
        warning_shown = False 

        while True:
            if st.session_state.last_physical_press:
                action_taken = st.session_state.last_physical_press
                time.sleep(0.5) 
                
                if action_taken in current_state_data['actions']:
                    next_state = current_state_data['actions'][action_taken]
                    st.session_state.current_state_id = next_state
                    st.rerun()

            if not warning_shown:
                if (time.time() - start_wait_time) > 10:
                    warning_placeholder.markdown(
                        "<div class='warning-text'>✨ Press the Button ✨</div>", 
                        unsafe_allow_html=True
                    )
                    warning_shown = True
            
            time.sleep(0.1)