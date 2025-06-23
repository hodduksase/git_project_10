import streamlit as st
import datetime
import json
import os
import pandas as pd
import plotly.express as px
from datetime import datetime, date, timedelta

# 페이지 설정
st.set_page_config(
    page_title="Daily Planner",
    page_icon="📅",
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
    }
    .date-header {
        font-size: 1.5rem;
        color: #34495E;
        text-align: center;
        margin-bottom: 1rem;
    }
    .task-input {
        background-color: #F8F9FA;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .time-slot {
        background-color: #FFFFFF;
        border: 1px solid #E9ECEF;
        border-radius: 8px;
        padding: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .completed {
        background-color: #D4EDDA;
        text-decoration: line-through;
        color: #155724;
    }
    .block-task {
        background-color: #E3F2FD;
        border-left: 4px solid #2196F3;
    }
    .stats-card {
        background-color: #F8F9FA;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'selected_date' not in st.session_state:
    st.session_state.selected_date = date.today()
if 'tasks' not in st.session_state:
    st.session_state.tasks = {}

def load_tasks(date_obj):
    """특정 날짜의 작업을 로드"""
    filename = f"{date_obj.isoformat()}.json"
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_tasks(date_obj, tasks):
    """작업을 저장"""
    filename = f"{date_obj.isoformat()}.json"
    if tasks:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
    elif os.path.exists(filename):
        os.remove(filename)

def get_time_slots():
    """30분 단위 시간 슬롯 생성"""
    slots = []
    for hour in range(24):
        for minute in [0, 30]:
            time_str = f"{hour:02d}:{minute:02d}"
            slots.append(time_str)
    return slots

def get_section_name(hour):
    """시간대별 섹션 이름"""
    if 6 <= hour < 12:
        return "오전"
    elif 12 <= hour < 18:
        return "오후"
    elif 18 <= hour < 24:
        return "밤"
    else:
        return "새벽"

def main():
    st.markdown('<h1 class="main-header">📅 Daily Planner</h1>', unsafe_allow_html=True)
    
    # 사이드바 - 날짜 선택 및 블록 작업
    with st.sidebar:
        st.header("📅 날짜 선택")
        selected_date = st.date_input(
            "날짜를 선택하세요",
            value=st.session_state.selected_date,
            format="YYYY-MM-DD"
        )
        
        if selected_date != st.session_state.selected_date:
            st.session_state.selected_date = selected_date
            st.rerun()
        
        st.markdown(f"**선택된 날짜:** {selected_date.strftime('%Y년 %m월 %d일 (%A)')}")
        
        # 블록 작업 추가
        st.header("🔧 블록 작업 추가")
        block_text = st.text_input("작업 내용")
        col1, col2 = st.columns(2)
        with col1:
            start_time = st.selectbox("시작 시간", get_time_slots(), index=18)  # 09:00
        with col2:
            end_time = st.selectbox("종료 시간", get_time_slots(), index=20)    # 10:00
        
        if st.button("블록 작업 추가", type="primary"):
            if block_text:
                add_block_task(selected_date, block_text, start_time, end_time)
                st.success("블록 작업이 추가되었습니다!")
                st.rerun()
    
    # 메인 컨텐츠
    tasks = load_tasks(selected_date)
    
    # 탭 생성
    tab1, tab2, tab3 = st.tabs(["📝 일일 플래너", "📊 주간 보기", "📈 통계"])
    
    with tab1:
        show_daily_planner(selected_date, tasks)
    
    with tab2:
        show_weekly_view()
    
    with tab3:
        show_statistics()

def add_block_task(date_obj, text, start_time, end_time):
    """블록 작업 추가"""
    tasks = load_tasks(date_obj)
    
    # 시간 슬롯 생성
    start_h, start_m = map(int, start_time.split(':'))
    end_h, end_m = map(int, end_time.split(':'))
    
    current_time = datetime.combine(date_obj, datetime.min.time().replace(hour=start_h, minute=start_m))
    end_datetime = datetime.combine(date_obj, datetime.min.time().replace(hour=end_h, minute=end_m))
    
    time_slots = []
    while current_time <= end_datetime:
        time_slots.append(current_time.strftime("%H:%M"))
        current_time += timedelta(minutes=30)
    
    # 작업 추가
    for i, time_key in enumerate(time_slots):
        if i == 0:
            tasks[time_key] = {"text": text, "done": False, "type": "block_start"}
        elif i == len(time_slots) - 1:
            tasks[time_key] = {"text": "끝", "done": False, "type": "block_end"}
        else:
            tasks[time_key] = {"text": "→", "done": False, "type": "block_middle"}
    
    save_tasks(date_obj, tasks)

def show_daily_planner(date_obj, tasks):
    """일일 플래너 표시"""
    st.markdown(f'<h2 class="date-header">{date_obj.strftime("%Y년 %m월 %d일 (%A)")}</h2>', unsafe_allow_html=True)
    
    # 시간대별로 그룹화
    sections = {"새벽": [], "오전": [], "오후": [], "밤": []}
    
    for time_slot in get_time_slots():
        hour = int(time_slot.split(':')[0])
        section = get_section_name(hour)
        
        task_data = tasks.get(time_slot, {"text": "", "done": False, "type": "normal"})
        
        sections[section].append({
            "time": time_slot,
            "task": task_data.get("text", ""),
            "done": task_data.get("done", False),
            "type": task_data.get("type", "normal")
        })
    
    # 각 섹션별로 표시
    for section_name, section_tasks in sections.items():
        st.subheader(f"🌅 {section_name}")
        
        for task_info in section_tasks:
            col1, col2, col3 = st.columns([1, 3, 1])
            
            with col1:
                st.write(f"**{task_info['time']}**")
            
            with col2:
                # 작업 텍스트 입력
                new_text = st.text_input(
                    f"작업 {task_info['time']}",
                    value=task_info['task'],
                    key=f"task_{task_info['time']}",
                    label_visibility="collapsed"
                )
                
                # 텍스트가 변경되면 저장
                if new_text != task_info['task']:
                    tasks[task_info['time']] = {
                        "text": new_text,
                        "done": task_info['done'],
                        "type": task_info['type']
                    }
                    save_tasks(date_obj, tasks)
            
            with col3:
                # 완료 체크박스
                done = st.checkbox(
                    "완료",
                    value=task_info['done'],
                    key=f"done_{task_info['time']}"
                )
                
                # 완료 상태가 변경되면 저장
                if done != task_info['done']:
                    tasks[task_info['time']] = {
                        "text": task_info['task'],
                        "done": done,
                        "type": task_info['type']
                    }
                    save_tasks(date_obj, tasks)
            
            # 블록 작업 스타일 적용
            if task_info['type'] in ['block_start', 'block_middle', 'block_end']:
                st.markdown('<div class="block-task"></div>', unsafe_allow_html=True)
            
            if task_info['done']:
                st.markdown('<div class="completed"></div>', unsafe_allow_html=True)

def show_weekly_view():
    """주간 보기"""
    st.header("📊 주간 보기")
    
    # 이번 주 날짜들
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    week_dates = [start_of_week + timedelta(days=i) for i in range(7)]
    
    # 주간 데이터 수집
    weekly_data = []
    for week_date in week_dates:
        tasks = load_tasks(week_date)
        completed = sum(1 for task in tasks.values() if isinstance(task, dict) and task.get('done', False))
        total = len(tasks)
        
        weekly_data.append({
            "날짜": week_date.strftime("%m/%d"),
            "요일": week_date.strftime("%A"),
            "완료": completed,
            "전체": total,
            "완료율": (completed / total * 100) if total > 0 else 0
        })
    
    # 데이터프레임으로 표시
    df = pd.DataFrame(weekly_data)
    st.dataframe(df, use_container_width=True)
    
    # 완료율 차트
    fig = px.bar(df, x="날짜", y="완료율", 
                 title="주간 완료율",
                 color="완료율",
                 color_continuous_scale="viridis")
    st.plotly_chart(fig, use_container_width=True)

def show_statistics():
    """통계 보기"""
    st.header("📈 통계")
    
    # 최근 7일 통계
    today = date.today()
    stats_data = []
    
    for i in range(7):
        check_date = today - timedelta(days=i)
        tasks = load_tasks(check_date)
        
        completed = sum(1 for task in tasks.values() if isinstance(task, dict) and task.get('done', False))
        total = len(tasks)
        
        stats_data.append({
            "날짜": check_date.strftime("%m/%d"),
            "완료": completed,
            "전체": total,
            "완료율": (completed / total * 100) if total > 0 else 0
        })
    
    stats_df = pd.DataFrame(stats_data)
    
    # 통계 카드들
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_tasks = stats_df['전체'].sum()
        st.metric("총 작업 수", total_tasks)
    
    with col2:
        completed_tasks = stats_df['완료'].sum()
        st.metric("완료된 작업", completed_tasks)
    
    with col3:
        avg_completion = stats_df['완료율'].mean()
        st.metric("평균 완료율", f"{avg_completion:.1f}%")
    
    # 완료율 트렌드 차트
    fig = px.line(stats_df, x="날짜", y="완료율", 
                  title="최근 7일 완료율 트렌드",
                  markers=True)
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main() 