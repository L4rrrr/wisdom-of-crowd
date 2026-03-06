import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 設定 ---
TRUE_VALUE = 568  # 真値（正解）をここにセット
DB_FILE = "guesses.csv"

st.set_page_config(page_title="群衆の知恵 デモ", layout="wide")

# データの読み込み
def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["guess"])

df = load_data()

# --- サイドバー：操作パネル ---
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
    st.header("演出設定")
    show_truth = st.toggle("正解（真値）を表示する")
    
    st.divider()
    if st.button("全データをリセット"):
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
            st.rerun()

# --- メイン画面：導入解説 ---
st.title("🔮 群衆の知恵：ビー玉数当て実験")

st.info("""
**「一人の天才よりも、100人の普通の人の平均の方が、真実に近い」**
これを『群衆の知恵（Wisdom of the Crowd）』と呼びます。

この実験では、皆さんの予想をリアルタイムで集計し、その「平均値」がどれだけ正解に近づくかを検証します。
一人の予想は大きく外れるかもしれませんが、集団としての判断は驚くほど正確になります。
""")

with st.expander("💡 なぜこれが「投資」や「経済」に関係あるの？"):
    st.write("""
    実は、**「株価」や「為替」が決まる仕組み**もこれと同じです。
    世界中の投資家が「この価値はこれくらいだ」と予想し、売り買いした結果（平均）が今の価格になっています。
    
    市場という「群衆」が、バラバラな情報を持ち寄り、一つの「妥当な価格」を作り出すプロセスを、この瓶の中で体験してみましょう！
    """)

# --- グラフと分析エリア ---
if not df.empty:
    latest_guess = df["guess"].iloc[-1]
    current_avg = df["guess"].mean()
    df['cumulative_avg'] = df['guess'].expanding().mean()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 1. 収束プロセス
        fig_line = px.line(df, y='cumulative_avg', title="平均値の収束プロセス",
                          labels={'cumulative_avg': '個数', 'index': '参加人数'})
        
        # 直近の予想（オレンジ点線）
        fig_line.add_hline(y=latest_guess, line_dash="dot", line_color="#EF553B", 
                          annotation_text=f"直近の予想: {latest_guess}個", annotation_position="bottom right")
        
        # 正解（緑実線：スイッチON時のみ）
        if show_truth:
            fig_line.add_hline(y=TRUE_VALUE, line_dash="solid", line_color="#00CC96", 
                              annotation_text=f"正解: {TRUE_VALUE}個", annotation_position="top left")
        
        fig_line.update_layout(font=dict(size=18), xaxis_title="参加人数（人）", yaxis_title="個数（個）")
        st.plotly_chart(fig_line, use_container_width=True)

    with col2:
        # 2. 分布（ヒストグラム）
        fig_hist = px.histogram(df, x="guess", title="予想値の分布（みんなのバラつき）",
                                labels={'guess': '予想された個数', 'count': '人数'},
                                nbins=30, text_auto=True)
        fig_hist.update_layout(bargap=0.1, font=dict(size=18), 
                               xaxis_title="予想された個数（個）", yaxis_title="人数（人）")
        st.plotly_chart(fig_hist, use_container_width=True)

    # --- 足元の数字メトリクス ---
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("直近の予想", f"{latest_guess} 個")
    c2.metric("現在の平均値", f"{current_avg:.1f} 個", delta=f"{current_avg - latest_guess:.1f}", delta_color="off")
    c3.metric("参加人数", f"{len(df)} 人")

    # --- 【復活！】正解表示時の決めゼリフ ---
    if show_truth:
        st.divider()
        error_pct = abs(current_avg - TRUE_VALUE) / TRUE_VALUE
        st.success(f"""
        ### 🎊 正解は {TRUE_VALUE} 個でした！
        現在の平均値 **{current_avg:.1f}** との誤差は、わずか **{error_pct:.1%}** です。
        
        これが『群衆の知恵』の力です。
        個々の予想はバラバラでも、多様な意見が集まることで、集団の平均は真実（妥当な価格）へと驚くほど近づいていくのです。
        """)

else:
    st.info("左側のパネルから最初の予想を入力してください。")