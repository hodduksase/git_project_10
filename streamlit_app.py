import streamlit as st
import json
import os
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(
    page_title="Daily Planner",
    page_icon="��",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2C3E50;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .date-header {
        font-size: 1.8rem;
        color: #34495E;
        text-align: center;
        margin-bottom: 1rem;
        padding: 1rem;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 15px;
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .date-header:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        transition: all 0.3s ease;
    }
    .task-input {
        background-color: #F8F9FA;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border: 2px solid #E9ECEF;
        transition: border-color 0.3s ease;
    }
    .task-input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    .time-slot {
        background-color: #FFFFFF;
        border: 1px solid #E9ECEF;
        border-radius: 8px;
        padding: 0.5rem;
        margin-bottom: 0.5rem;
        transition: all 0.3s ease;
    }
    .time-slot:hover {
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transform: translateY(-1px);
    }
    .completed {
        background-color: #D4EDDA;
        text-decoration: line-through;
        color: #155724;
        border-left: 4px solid #28a745;
    }
    .block-task {
        background-color: #E3F2FD;
        border-left: 4px solid #2196F3;
        position: relative;
    }
    .block-task::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;
        background: linear-gradient(135deg, #2196F3, #21CBF3);
    }
    .stats-card {
        background-color: #F8F9FA;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border: 1px solid #E9ECEF;
        transition: all 0.3s ease;
    }
    .stats-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    .stButton > button {
        border-radius: 20px;
        border: none;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    .sidebar .stButton > button {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        font-size: 0.8rem;
        padding: 0.3rem 0.8rem;
    }
    .sidebar .stButton > button:hover {
        box-shadow: 0 4px 12px rgba(240, 147, 251, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'user_password' not in st.session_state:
    st.session_state.user_password = None
if 'selected_date' not in st.session_state:
    st.session_state.selected_date = date.today()
if 'tasks' not in st.session_state:
    st.session_state.tasks = {}
if 'show_date_picker' not in st.session_state:
    st.session_state.show_date_picker = False

def get_user_data_file(username):
    return f"data_{username}.json"

def load_user_data(username):
    filename = get_user_data_file(username)
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_user_data(username, data):
    filename = get_user_data_file(username)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def login_page():
    """로그인 페이지"""
    st.title("🔐 시간 관리 플래너 로그인")
    st.markdown("---")
    
    # 로그인 폼
    with st.form("login_form"):
        user_id = st.text_input("아이디")
        password = st.text_input("비밀번호", type="password")
        
        if st.form_submit_button("로그인", type="primary"):
            if user_id and password:
                # 아이디와 비밀번호 조합으로 사용자 구분
                user_key = f"{user_id}_{password}"
                st.session_state.logged_in = True
                st.session_state.current_user = user_key
                st.session_state.password_verified = True
                st.success(f"로그인 성공! 사용자: {user_id}")
                st.rerun()
            else:
                st.error("아이디와 비밀번호를 입력해주세요.")
    
    st.markdown("---")
    st.info("💡 **사용법**: 아이디와 비밀번호 조합으로 계정이 구분됩니다. 같은 아이디라도 비밀번호가 다르면 새로운 계정입니다.")

def main_planner():
    """메인 플래너 화면"""
    st.title("📅 시간 관리 플래너")
    
    # 사이드바에 로그아웃 버튼
    with st.sidebar:
        st.header("👤 사용자 정보")
        # user_key에서 아이디 부분만 추출
        user_id = st.session_state.current_user.split('_')[0] if '_' in st.session_state.current_user else st.session_state.current_user
        st.write(f"**사용자**: {user_id}")
        if st.button("로그아웃", type="secondary"):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.session_state.password_verified = False
            st.rerun()
    
    # 사용자 데이터 로드
    user_data = load_user_data(st.session_state.current_user)
    
    # 탭 생성
    tab1, tab2, tab3, tab4 = st.tabs(["📝 일일 계획", "📊 통계", "🔧 블록 작업", "📅 주간 보기"])
    
    with tab1:
        # 날짜 선택
        selected_date = st.date_input("날짜 선택", value=datetime.now())
        daily_planner_tab(selected_date, user_data)
    
    with tab2:
        statistics_tab(user_data)
    
    with tab3:
        block_tasks_tab(user_data)
    
    with tab4:
        weekly_view_tab(user_data)

def daily_planner_tab(selected_date, user_data):
    """일일 계획 탭"""
    st.header(f"📝 {selected_date.strftime('%Y년 %m월 %d일')} 일일 계획")
    
    date_str = selected_date.strftime("%Y-%m-%d")
    
    if date_str not in user_data:
        user_data[date_str] = {"tasks": {}, "block_tasks": []}
    
    # 두 개의 컬럼으로 나누기
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("📅 시간별 계획")
        # 시간대별 작업 입력
        time_slots = [
            ("새벽", "06:00", "12:00"),
            ("오후", "12:00", "18:00"),
            ("저녁", "18:00", "23:59"),
            ("새벽", "00:00", "06:00")
        ]
        
        for period, start_time, end_time in time_slots:
            st.write(f"**🌅 {period} ({start_time}-{end_time})**")
            
            # 30분 단위 시간 슬롯
            current_time = datetime.strptime(start_time, "%H:%M")
            end_time_obj = datetime.strptime(end_time, "%H:%M")
            
            while current_time < end_time_obj:
                time_slot = current_time.strftime("%H:%M")
                next_time = (current_time + timedelta(minutes=30)).strftime("%H:%M")
                slot_key = f"{time_slot}-{next_time}"
                
                task_col1, task_col2, task_col3 = st.columns([1, 3, 1])
                
                with task_col1:
                    st.write(f"**{time_slot}**")
                
                with task_col2:
                    task_key = f"{date_str}_{slot_key}"
                    task = st.text_input(
                        "작업 내용",
                        value=user_data[date_str]["tasks"].get(slot_key, ""),
                        key=f"task_{task_key}",
                        label_visibility="collapsed"
                    )
                    user_data[date_str]["tasks"][slot_key] = task
                
                with task_col3:
                    completed_key = f"completed_{task_key}"
                    completed = st.checkbox(
                        "완료",
                        value=user_data[date_str]["tasks"].get(f"{slot_key}_completed", False),
                        key=completed_key
                    )
                    user_data[date_str]["tasks"][f"{slot_key}_completed"] = completed
                
                current_time += timedelta(minutes=30)
    
    with col_right:
        st.subheader("🔧 블록 작업")
        
        # 블록 작업 추가
        st.write("**새 블록 작업 추가**")
        block_task_name = st.text_input("작업명", key=f"block_task_name_{date_str}")
        block_start_time = st.time_input("시작 시간", key=f"block_start_time_{date_str}")
        block_end_time = st.time_input("종료 시간", key=f"block_end_time_{date_str}")
        block_color = st.color_picker("색상", "#FF6B6B", key=f"block_color_{date_str}")
        
        if st.button("추가", key=f"add_block_{date_str}", type="primary"):
            if block_task_name and block_start_time < block_end_time:
                new_block = {
                    "name": block_task_name,
                    "start": block_start_time.strftime("%H:%M"),
                    "end": block_end_time.strftime("%H:%M"),
                    "color": block_color,
                    "completed": False
                }
                user_data[date_str]["block_tasks"].append(new_block)
                save_user_data(st.session_state.current_user, user_data)
                st.success("추가됨!")
                st.rerun()
            else:
                st.error("작업명과 시간을 확인하세요")
        
        # 블록 작업 목록
        st.write("**현재 블록 작업**")
        if user_data[date_str]["block_tasks"]:
            for i, block in enumerate(user_data[date_str]["block_tasks"]):
                with st.container():
                    st.write(f"**{block['name']}**")
                    st.write(f"⏰ {block['start']} - {block['end']}")
                    
                    block_col1, block_col2, block_col3 = st.columns([2, 1, 1])
                    with block_col1:
                        st.color_picker("색상", block['color'], disabled=True, key=f"color_{date_str}_{i}")
                    with block_col2:
                        completed = st.checkbox(
                            "완료",
                            value=block['completed'],
                            key=f"block_completed_{date_str}_{i}"
                        )
                        user_data[date_str]["block_tasks"][i]['completed'] = completed
                    with block_col3:
                        if st.button("삭제", key=f"delete_block_{date_str}_{i}"):
                            user_data[date_str]["block_tasks"].pop(i)
                            save_user_data(st.session_state.current_user, user_data)
                            st.rerun()
                    st.markdown("---")
        else:
            st.info("블록 작업이 없습니다")
    
    # 저장 버튼 (전체 너비)
    st.markdown("---")
    if st.button("💾 저장", type="primary"):
        save_user_data(st.session_state.current_user, user_data)
        st.success("저장되었습니다!")

def weekly_view_tab(user_data):
    """주간 보기 탭"""
    st.header("📊 주간 보기")
    
    # 이번 주 날짜들
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    week_dates = [start_of_week + timedelta(days=i) for i in range(7)]
    
    # 주간 데이터 표시
    weekly_data = []
    for date in week_dates:
        date_str = date.strftime("%Y-%m-%d")
        if date_str in user_data:
            tasks = user_data[date_str].get("tasks", {})
            completed_tasks = sum(1 for k, v in tasks.items() if k.endswith("_completed") and v)
            total_tasks = len([k for k in tasks.keys() if not k.endswith("_completed")])
            
            weekly_data.append({
                "날짜": date.strftime("%m/%d"),
                "요일": date.strftime("%A"),
                "완료된 작업": completed_tasks,
                "전체 작업": total_tasks,
                "완료율": f"{(completed_tasks/total_tasks*100):.1f}%" if total_tasks > 0 else "0%"
            })
    
    if weekly_data:
        df = pd.DataFrame(weekly_data)
        st.dataframe(df, use_container_width=True)
        
        # 완료율 차트
        fig = px.bar(df, x="날짜", y="완료된 작업", 
                    title="주간 작업 완료 현황",
                    color="완료된 작업",
                    color_continuous_scale="viridis")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("이번 주 데이터가 없습니다.")

def statistics_tab(user_data):
    """통계 탭"""
    st.header("📈 통계 분석")
    
    if not user_data:
        st.info("데이터가 없습니다.")
        return
    
    # 전체 통계 계산
    total_tasks = 0
    completed_tasks = 0
    total_hours = 0
    
    for date_str, day_data in user_data.items():
        tasks = day_data.get("tasks", {})
        for key, value in tasks.items():
            if not key.endswith("_completed"):
                total_tasks += 1
                total_hours += 0.5  # 30분 단위
            elif value:  # 완료된 작업
                completed_tasks += 1
    
    # 통계 표시
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("총 작업 수", total_tasks)
    
    with col2:
        st.metric("완료된 작업", completed_tasks)
    
    with col3:
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        st.metric("완료율", f"{completion_rate:.1f}%")
    
    with col4:
        st.metric("총 계획 시간", f"{total_hours:.1f}시간")
    
    # 월별 통계
    monthly_stats = {}
    for date_str, day_data in user_data.items():
        month = date_str[:7]  # YYYY-MM
        if month not in monthly_stats:
            monthly_stats[month] = {"tasks": 0, "completed": 0}
        
        tasks = day_data.get("tasks", {})
        for key, value in tasks.items():
            if not key.endswith("_completed"):
                monthly_stats[month]["tasks"] += 1
            elif value:
                monthly_stats[month]["completed"] += 1
    
    if monthly_stats:
        monthly_data = []
        for month, stats in monthly_stats.items():
            completion_rate = (stats["completed"] / stats["tasks"] * 100) if stats["tasks"] > 0 else 0
            monthly_data.append({
                "월": month,
                "작업 수": stats["tasks"],
                "완료 수": stats["completed"],
                "완료율": completion_rate
            })
        
        df_monthly = pd.DataFrame(monthly_data)
        
        # 월별 완료율 차트
        fig = px.line(df_monthly, x="월", y="완료율", 
                     title="월별 완료율 추이",
                     markers=True)
        st.plotly_chart(fig, use_container_width=True)

def block_tasks_tab(user_data):
    """블록 작업 탭"""
    st.header("🔧 블록 작업 관리")
    
    # 새 블록 작업 추가
    st.subheader("새 블록 작업 추가")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        task_name = st.text_input("작업명", key="block_task_name")
    
    with col2:
        start_time = st.time_input("시작 시간", key="block_start_time")
    
    with col3:
        end_time = st.time_input("종료 시간", key="block_end_time")
    
    with col4:
        color = st.color_picker("색상", "#FF6B6B", key="block_color")
    
    if st.button("블록 작업 추가", type="primary"):
        if task_name and start_time < end_time:
            new_block = {
                "name": task_name,
                "start": start_time.strftime("%H:%M"),
                "end": end_time.strftime("%H:%M"),
                "color": color,
                "completed": False
            }
            user_data[datetime.now().strftime("%Y-%m-%d")]["block_tasks"].append(new_block)
            save_user_data(st.session_state.current_user, user_data)
            st.success("블록 작업이 추가되었습니다!")
            st.rerun()
        else:
            st.error("작업명을 입력하고 시작 시간이 종료 시간보다 빨라야 합니다.")
    
    # 기존 블록 작업 표시
    st.subheader("현재 블록 작업")
    
    if user_data[datetime.now().strftime("%Y-%m-%d")]["block_tasks"]:
        for i, block in enumerate(user_data[datetime.now().strftime("%Y-%m-%d")]["block_tasks"]):
            col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])
            
            with col1:
                st.write(f"**{block['name']}**")
            
            with col2:
                st.write(f"{block['start']} - {block['end']}")
            
            with col3:
                st.color_picker("색상", block['color'], disabled=True, key=f"color_{i}")
            
            with col4:
                completed = st.checkbox(
                    "완료",
                    value=block['completed'],
                    key=f"block_completed_{i}"
                )
                user_data[datetime.now().strftime("%Y-%m-%d")]["block_tasks"][i]['completed'] = completed
            
            with col5:
                if st.button("삭제", key=f"delete_block_{i}"):
                    user_data[datetime.now().strftime("%Y-%m-%d")]["block_tasks"].pop(i)
                    save_user_data(st.session_state.current_user, user_data)
                    st.rerun()
    else:
        st.info("블록 작업이 없습니다.")

# 메인 앱 실행
def main():
    st.set_page_config(
        page_title="시간 관리 플래너",
        page_icon="📅",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 세션 상태 초기화
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = None
    if "password_verified" not in st.session_state:
        st.session_state.password_verified = False
    
    # 로그인하지 않은 경우
    if not st.session_state.logged_in:
        login_page()
    else:
        # 로그인된 경우 바로 메인 플래너 표시
        main_planner()

main() 