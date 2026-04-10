import streamlit as st
import pandas as pd

st.set_page_config(page_title="Katie式 雲井ペンタトニック対応表", layout="wide")

st.title("Katie式 雲井ペンタトニック対応表")
st.caption("コード対応 + スケール表 + ギター指板ポジション図版付き")

# ======================================
# 音名定義（半音は♭表記に統一）
# ======================================
NOTES = ["C", "D♭", "D", "E♭", "E", "F", "G♭", "G", "A♭", "A", "B♭", "B"]

# 雲井ペンタトニック: 1, 2, ♭3, 5, ♭6
KUMOI_INTERVALS = [0, 2, 3, 7, 9]  # ← 8じゃなくて9
KUMOI_DEGREES = ["1", "2", "♭3", "5", "6"]

# ギター標準チューニング（6弦→1弦）
STRING_TUNING = {
    "6": "E",
    "5": "A",
    "4": "D",
    "3": "G",
    "2": "B",
    "1": "E"
}

MAX_FRET = 15


# ======================================
# ユーティリティ
# ======================================
def transpose(note, semitones):
    idx = NOTES.index(note)
    return NOTES[(idx + semitones) % 12]

def build_scale(root, intervals):
    return [transpose(root, i) for i in intervals]

def format_scale(root):
    return " - ".join(build_scale(root, KUMOI_INTERVALS))

def degree_map_for_scale(root):
    scale_notes = build_scale(root, KUMOI_INTERVALS)
    return dict(zip(scale_notes, KUMOI_DEGREES))

def get_note_on_string(open_note, fret):
    return transpose(open_note, fret)


# ======================================
# Katie式対応ルール
# ======================================
def get_katie_kumoi_map(chord_root):
    return {
        f"{chord_root}m7": [
            {
                "使用ペンタ": f"{chord_root} 雲井ペンタトニック",
                "響き": "ドリアン風",
                "解説": "m7コード上でルートの雲井ペンタを使うことで、短調の中にも少し明るさのあるドリアン風の表情を作る。"
            },
            {
                "使用ペンタ": f"{transpose(chord_root, 5)} 雲井ペンタトニック",
                "響き": "哀愁のエオリアン風",
                "解説": "4度上の雲井ペンタを使うと、より哀愁感のあるマイナー色が出やすく、エオリアン寄りの雰囲気になる。"
            },
        ],
        f"{chord_root}7": [
            {
                "使用ペンタ": f"{chord_root} 雲井ペンタトニック",
                "響き": "JAZZブルース風",
                "解説": "7コード上でルートの雲井ペンタを使うと、ブルージーさと和風っぽさが混ざった独特のJAZZブルース感が出る。"
            },
            {
                "使用ペンタ": f"{transpose(chord_root, 7)} 雲井ペンタトニック",
                "響き": "ミクソリディアン風",
                "解説": "5度上の雲井ペンタを使うことで、ドミナント7th上の自然な抜け感が出て、ミクソリディアン風に聞こえやすい。"
            },
            {
                "使用ペンタ": f"{transpose(chord_root, 1)} 雲井ペンタトニック",
                "響き": "オルタード風（ドミナント向け）",
                "解説": "♭2上の雲井ペンタを使うと、外側へ踏み込んだ緊張感が生まれ、オルタードっぽいスリリングな響きになる。"
            },
        ]
    }


# ======================================
# 指板表（音名+度数）
# ======================================
def build_fretboard_dataframe(scale_root, max_fret=15):
    scale_notes = build_scale(scale_root, KUMOI_INTERVALS)
    deg_map = degree_map_for_scale(scale_root)

    rows = []
    for string_no in ["1", "2", "3", "4", "5", "6"]:
        open_note = STRING_TUNING[string_no]
        row = {"弦": string_no}
        for fret in range(max_fret + 1):
            note = get_note_on_string(open_note, fret)
            if note in scale_notes:
                row[f"{fret}F"] = f"{note}\n({deg_map[note]})"
            else:
                row[f"{fret}F"] = ""
        rows.append(row)

    return pd.DataFrame(rows)


# ======================================
# ●で見える指板図
# ルートは ◎
# それ以外のスケール音は ●
# 非スケール音は -
# ======================================
def build_dot_fretboard_dataframe(scale_root, max_fret=15):
    scale_notes = build_scale(scale_root, KUMOI_INTERVALS)

    rows = []
    for string_no in ["1", "2", "3", "4", "5", "6"]:
        open_note = STRING_TUNING[string_no]
        row = {"弦": f"{string_no}弦"}
        for fret in range(max_fret + 1):
            note = get_note_on_string(open_note, fret)
            if note == scale_root:
                row[f"{fret}F"] = "◎"
            elif note in scale_notes:
                row[f"{fret}F"] = "●"
            else:
                row[f"{fret}F"] = "－"
        rows.append(row)

    return pd.DataFrame(rows)


# ======================================
# 各対応カード表示
# ======================================
def render_scale_card(item):
    scale_root = item["使用ペンタ"].replace(" 雲井ペンタトニック", "")
    scale_notes = build_scale(scale_root, KUMOI_INTERVALS)

    with st.container(border=True):
        st.markdown(f"### {item['使用ペンタ']}")
        st.write(f"**響き:** {item['響き']}")
        st.write(f"**解説:** {item['解説']}")
        st.write(f"**構成音:** {' - '.join(scale_notes)}")

        with st.expander("●で見る指板ポジション"):
            st.write("**凡例:** ◎ = ルート / ● = スケール音 / － = それ以外")
            dot_df = build_dot_fretboard_dataframe(scale_root, MAX_FRET)
            st.dataframe(dot_df, use_container_width=True, hide_index=True)

        with st.expander("音名と度数で見る指板ポジション"):
            note_df = build_fretboard_dataframe(scale_root, MAX_FRET)
            st.dataframe(note_df, use_container_width=True, hide_index=True)


# ======================================
# UI
# ======================================
selected_root = st.selectbox("ルートを選んでください", NOTES, index=0)
mapping = get_katie_kumoi_map(selected_root)

st.markdown("---")
st.subheader(f"{selected_root}m7 / {selected_root}7 に対する Katie式 雲井ペンタ対応")

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"## {selected_root}m7")
    for item in mapping[f"{selected_root}m7"]:
        render_scale_card(item)

with col2:
    st.markdown(f"## {selected_root}7")
    for item in mapping[f"{selected_root}7"]:
        render_scale_card(item)


# ======================================
# 全スケール表
# ======================================
st.markdown("---")
st.subheader("雲井ペンタトニック スケール表")

scale_rows = []
for root in NOTES:
    scale_rows.append({
        "ルート": root,
        "度数": " - ".join(KUMOI_DEGREES),
        "構成音": format_scale(root)
    })

st.table(scale_rows)


# ======================================
# 下部のメイン指板図
# ======================================
st.markdown("---")
st.subheader(f"{selected_root} 雲井ペンタトニック 指板図")

st.write("**凡例:** ◎ = ルート / ● = スケール音 / － = それ以外")
main_dot_df = build_dot_fretboard_dataframe(selected_root, MAX_FRET)
st.dataframe(main_dot_df, use_container_width=True, hide_index=True)

st.subheader(f"{selected_root} 雲井ペンタトニック 音名・度数表")
main_note_df = build_fretboard_dataframe(selected_root, MAX_FRET)
st.dataframe(main_note_df, use_container_width=True, hide_index=True)


# ======================================
# 練習メモ
# ======================================
st.markdown("---")
st.subheader("Katie式 練習メモ")
st.write(
    f"{selected_root}m7 では『{selected_root}雲井ペンタ = ドリアン風』『{transpose(selected_root, 5)}雲井ペンタ = 哀愁のエオリアン風』として使い分けできる。"
)
st.write(
    f"{selected_root}7 では『{selected_root}雲井ペンタ = JAZZブルース風』『{transpose(selected_root, 7)}雲井ペンタ = ミクソリディアン風』『{transpose(selected_root, 1)}雲井ペンタ = オルタード風』として整理できる。"
)
st.write(
    "まずはルート位置を◎で把握して、その近くの●をつなぐように弾くと、実戦でかなり使いやすい。"
)