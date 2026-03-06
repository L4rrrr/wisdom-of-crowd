import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 設定 ---
DB_FILE = "guesses.csv"
TRUE_VALUE = 500  # ここに実際の正解数を入力

st.set_page_config(page_title="群衆の知恵 デモ", layout="wide")

# データの初期化関数
def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["guess"])

df = load_data()

# --- メイン画面 ---
st.title("🔮 群衆の知恵：ビー玉数当て実験")
st.write("多くの人の予想を合わせると、真実にどこまで近づくでしょうか？")

# サイドバー：入力・管理
with st.sidebar:
    st.header("スタッフ操作パネル")
    with st.form("input_form", clear_on_submit=True):
        new_guess = st.number_input("お客さんの予想:", min_value=0, step=1)
        submit = st.form_submit_button("記録する")
        if submit:
            new_data = pd.DataFrame({"guess": [new_guess]})
            df = pd.concat([df, new_data], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            st.rerun()

    st.divider()
    if st.button("全データをリセット"):
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
            st.rerun()
    
    if not df.empty:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("結果をCSVで保存", data=csv, file_name="wisdom_results.csv")

# --- 集計・グラフ表示 ---
if not df.empty:
    col1, col2 = st.columns([1, 1])
    
    current_avg = df["guess"].mean()
    count = len(df)

    with col1:
        st.metric("現在の平均値", f"{current_avg:.1f} 個")
        st.metric("サンプル数（人数）", f"{count} 人")
        
        # 収束グラフ（平均値がどう推移したか）
        df['cumulative_avg'] = df['guess'].expanding().mean()
        fig_line = px.line(df, y='cumulative_avg', title="平均値の収束（人数が増えるほど真値へ）")
        fig_line.add_hline(y=TRUE_VALUE, line_dash="dash", line_color="red", annotation_text="真解")
        st.plotly_chart(fig_line, use_container_width=True)

    with col2:
        # 分布グラフ
        # --- 修正案：データに合わせて細かく表示する ---
        fig_hist = px.histogram(
            df, 
            x="guess", 
            title="予想値のバラつき（多様性）",
            nbins=50,             # 棒の数を増やす（数字を大きくすると細かくなります）
            text_auto=True,       # 棒の上に人数を表示
        )
        # 棒の見た目を整える設定
        fig_hist.update_layout(bargap=0.1) 
        # X軸のメモリを自動でいい感じにする
        fig_hist.update_xaxes(nticks=10)

        st.plotly_chart(fig_hist, use_container_width=True)

    # 金融解説モード
    with st.expander("【解説】なぜ平均は正しいのか？"):
        st.write(f"""
        現在の平均値 **{current_avg:.1f}** は、正解の **{TRUE_VALUE}** に対して 
        誤差 **{abs(current_avg - TRUE_VALUE)/TRUE_VALUE:.1%}** です。
        
        これは金融市場における**「効率的市場仮説」**の簡易モデルです。
        一人の天才（専門家）を探すよりも、多様な背景を持つ大勢の予想を統合する方が、
        結果として「妥当な価格」を形成しやすくなります。
        """)
else:
    st.info("左側のパネルから最初の予想を入力してください。")
