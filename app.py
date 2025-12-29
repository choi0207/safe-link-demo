import streamlit as st
import numpy as np
import pandas as pd
import time

# 1. 앱 페이지 설정 (모바일 비율처럼 보이게 설정)
st.set_page_config(page_title="Safe-Link Demo", layout="centered")

st.title("📱 Safe-Link: 낙상 사전 인식 시스템")
st.subheader("실시간 환자 거리 모니터링")

# 2. 사이드바 - 설정 제어 (앱의 설정 메뉴 역할)
st.sidebar.header("🛠️ 시스템 설정")
safe_distance = st.sidebar.slider("안전 거리 설정 (m)", 1.0, 5.0, 3.0)
process_noise = st.sidebar.slider("칼만 필터 감도", 0.001, 0.1, 0.01)

# 3. 칼만 필터 클래스
class KalmanFilter:
    def __init__(self, process_variance, measurement_variance):
        self.process_variance = process_variance
        self.measurement_variance = measurement_variance
        self.estimated_value = 1.0
        self.post_error_covariance = 1.0

    def update(self, measurement):
        prior_error_covariance = self.post_error_covariance + self.process_variance
        kalman_gain = prior_error_covariance / (prior_error_covariance + self.measurement_variance)
        self.estimated_value = self.estimated_value + kalman_gain * (measurement - self.estimated_value)
        self.post_error_covariance = (1 - kalman_gain) * prior_error_covariance
        return self.estimated_value

# 4. 앱 구동 로직
if st.button('실시간 모니터링 시작'):
    kf = KalmanFilter(process_noise, 2.0)
    chart_placeholder = st.empty() # 그래프가 업데이트될 자리
    status_placeholder = st.empty() # 상태 메시지가 뜰 자리
    
    data = pd.DataFrame(columns=['Real', 'Filtered'])
    
    for t in range(100):
        # 시뮬레이션 데이터: 40단계부터 환자가 멀어짐
        real_d = 1.0 + (t * 0.05) if t < 40 else 3.5 + (np.random.randn() * 0.1)
        
        # 노이즈 섞인 RSSI 측정값 생성
        rssi_noise = np.random.normal(0, 3)
        measured_d = real_d + (rssi_noise * 0.2)
        
        # 칼만 필터로 보정
        filtered_d = kf.update(measured_d)
        
        # 데이터 저장
        new_row = {'Real': real_d, 'Filtered': filtered_d}
        data = pd.concat([data, pd.DataFrame([new_row])], ignore_index=True)
        
        # 그래프 업데이트
        chart_placeholder.line_chart(data)
        
        # 거리 기반 상태 표시 및 사전 인식 알람
        if filtered_d > safe_distance:
            status_placeholder.error(f"⚠️ 위험! 환자 이탈 감지 (현재 거리: {filtered_d:.2f}m)")
            # 여기서 실제 스마트폰이라면 푸시 알림이 발송됨
        else:
            status_placeholder.success(f"✅ 안전 (현재 거리: {filtered_d:.2f}m)")
            
        time.sleep(0.1) # 실시간 느낌을 위해 0.1초 대기
