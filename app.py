import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from pathlib import Path

from optimizer import (
    TARGETS, FE_LOWER, FE_UPPER,
    get_default_chemistry, load_chemistry_from_excel,
    solve_blend_with_compensation, calculate_cost_breakdown,
    quality_checks, quality_table, redistribute_adjustment,
    what_if_analysis, compute_achieved,
)

# ============================================================
# PAGE
# ============================================================
st.set_page_config(
    page_title="Sinter Burden Optimizer",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE = Path(__file__).parent
ASSETS = BASE / "assets"

# ============================================================
# THEME — task-management inspired industrial workspace
# ============================================================
st.markdown("""
<style>
:root{
  --bg:#0a0c13;
  --bg2:#11131d;
  --sidebar:#171821;
  --panel:#151720;
  --panel2:#1b1d28;
  --line:#2a2d3a;
  --text:#f4f5f8;
  --muted:#8f93a5;
  --blue:#2f80ed;
  --cyan:#2bd1dc;
  --green:#35c879;
  --amber:#f4b63f;
  --red:#f05b65;
  --purple:#9a6cff;
  --orange:#ff8b4d;
}

html,body,[class*="css"]{font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;}
.stApp{
  background:
    radial-gradient(circle at 68% 4%, rgba(69,92,190,.12), transparent 28%),
    radial-gradient(circle at 100% 80%, rgba(67,185,138,.07), transparent 25%),
    var(--bg);
  color:var(--text);
}
.block-container{max-width:1750px;padding:.7rem 1rem 2rem 1rem;}
[data-testid="stSidebar"]{
  background:linear-gradient(180deg,#181a24 0%,#151720 100%);
  border-right:1px solid #292c38;
}
[data-testid="stSidebar"] > div:first-child{padding:1rem .85rem;}
h1,h2,h3,h4{color:var(--text)!important;}
h1{font-size:2rem!important;letter-spacing:-.03em;}
h2{font-size:1.35rem!important;}
h3{font-size:1.05rem!important;}
.small{font-size:.72rem;color:var(--muted);}
.eyebrow{font-size:.64rem;color:#7c82a0;letter-spacing:.14em;text-transform:uppercase;font-weight:800;}
.muted{color:var(--muted);font-size:.75rem;}
.panel{
  background:linear-gradient(145deg,rgba(24,26,36,.96),rgba(17,19,28,.98));
  border:1px solid var(--line);
  border-radius:13px;
  padding:.85rem;
  box-shadow:0 10px 30px rgba(0,0,0,.13);
}
.panel-tight{padding:.65rem;}
.hero{
  background:linear-gradient(120deg,#171924 0%,#12141d 55%,#15182a 100%);
  border:1px solid #2a2d3b;
  border-radius:16px;
  padding:1rem 1.15rem;
}
.logo-row{display:flex;align-items:center;justify-content:center;gap:12px;padding:.25rem 0 .65rem;}
.logo-row img{height:42px;width:auto;object-fit:contain;background:#fff;border-radius:6px;padding:3px;}
.jv-title{font-size:.78rem;font-weight:800;letter-spacing:.04em;text-align:center;color:#f5f6fa;}
.jv-sub{font-size:.59rem;color:#85899a;text-align:center;margin-top:2px;}
.nav-group{font-size:.58rem;letter-spacing:.16em;color:#777c91;text-transform:uppercase;font-weight:800;margin:1.1rem .3rem .35rem;}
.nav-note{font-size:.62rem;color:#73788c;margin:.8rem .25rem;}
.badge{
 display:inline-flex;align-items:center;gap:5px;padding:4px 8px;border-radius:999px;
 font-size:.64rem;font-weight:800;border:1px solid transparent;
}
.badge-ok{background:rgba(53,200,121,.12);color:#5be092;border-color:rgba(53,200,121,.25);}
.badge-out{background:rgba(240,91,101,.12);color:#ff7d87;border-color:rgba(240,91,101,.25);}
.badge-blue{background:rgba(47,128,237,.12);color:#67a7ff;border-color:rgba(47,128,237,.25);}
.badge-amber{background:rgba(244,182,63,.12);color:#ffc85d;border-color:rgba(244,182,63,.25);}
.kpi{
 background:linear-gradient(145deg,#171923,#12141c);
 border:1px solid var(--line);border-radius:13px;padding:.82rem .9rem;
 min-height:105px;position:relative;overflow:hidden;
}
.kpi:before{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--accent,#2f80ed);}
.kpi-label{font-size:.58rem;letter-spacing:.12em;color:#85899c;font-weight:800;}
.kpi-value{font-size:1.25rem;font-weight:800;margin-top:.35rem;color:#f6f7fa;}
.kpi-sub{font-size:.65rem;color:#7e8293;margin-top:.22rem;}
.kpi-blue{--accent:#2f80ed}.kpi-green{--accent:#35c879}.kpi-amber{--accent:#f4b63f}.kpi-cyan{--accent:#2bd1dc}.kpi-purple{--accent:#9a6cff}.kpi-red{--accent:#f05b65}
.section-title{font-size:.68rem;letter-spacing:.13em;text-transform:uppercase;color:#8790a6;font-weight:900;margin-bottom:.5rem;}
.edit-hint{
  font-size:.66rem;color:#a8aec0;background:#11131b;border:1px solid #303342;
  border-radius:8px;padding:.42rem .55rem;margin-bottom:.5rem;
}
.notice{
  border-radius:10px;padding:.55rem .7rem;font-size:.72rem;font-weight:700;
  background:rgba(53,200,121,.10);border:1px solid rgba(53,200,121,.25);color:#67df98;
}
.notice-warn{background:rgba(244,182,63,.10);border-color:rgba(244,182,63,.25);color:#ffd06a;}
.notice-bad{background:rgba(240,91,101,.10);border-color:rgba(240,91,101,.25);color:#ff8089;}
.table-wrap{border:1px solid var(--line);border-radius:10px;overflow:hidden;background:#12141c;}
table.pretty{width:100%;border-collapse:collapse;font-size:.69rem;}
table.pretty th{background:#1b1d27;color:#9ea4b6;text-align:left;padding:8px 9px;font-size:.60rem;letter-spacing:.04em;text-transform:uppercase;}
table.pretty td{border-top:1px solid #252834;padding:8px 9px;color:#e8eaf0;}
table.pretty tr:hover td{background:#181a24;}
.group-iron td:first-child{border-left:3px solid #4f8ff7;}
.group-flux td:first-child{border-left:3px solid #42d08a;}
.group-recycle td:first-child{border-left:3px solid #f4b63f;}
.group-fuel td:first-child{border-left:3px solid #f05b65;}
.total-row td{background:#1c1e28!important;font-weight:900;border-top:2px solid #3a3d4c!important;}
.status-dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:5px;}
.dot-ok{background:#4fdd8c;box-shadow:0 0 8px rgba(79,221,140,.5);}
.dot-out{background:#ff6570;box-shadow:0 0 8px rgba(255,101,112,.5);}
.progress{height:7px;background:#272a36;border-radius:99px;overflow:hidden;margin-top:5px;}
.progress > div{height:100%;border-radius:99px;background:linear-gradient(90deg,#4f8ff7,#42d08a);}
.right-card{
 background:#171923;border:1px solid #2b2e3a;border-radius:13px;padding:.8rem;
}
.timeline{border-left:2px solid #303341;margin:.4rem 0 .1rem .35rem;padding-left:.85rem;}
.timeline-item{position:relative;margin:0 0 .95rem;}
.timeline-item:before{content:"";position:absolute;left:-1.37rem;top:.2rem;width:8px;height:8px;border-radius:50%;background:#4f8ff7;box-shadow:0 0 0 4px #171923;}
.timeline-item:nth-child(2):before{background:#f4b63f}
.timeline-item:nth-child(3):before{background:#9a6cff}
.timeline-item:nth-child(4):before{background:#35c879}
.timeline-title{font-size:.72rem;font-weight:800;color:#e9ebf0;}
.timeline-sub{font-size:.61rem;color:#85899b;margin-top:2px;}
.stButton>button{
 border-radius:9px!important;border:1px solid #343744!important;background:#1b1d27!important;
 color:#eef0f5!important;font-weight:700!important;font-size:.72rem!important;
}
.stButton>button:hover{border-color:#4f8ff7!important;background:#202330!important;}
button[kind="primary"]{background:linear-gradient(135deg,#2f80ed,#2467d0)!important;border-color:#2f80ed!important;}
[data-testid="stDataEditor"]{border:1px solid #2b2e3a;border-radius:10px;overflow:hidden;}
[data-testid="stMetric"]{background:#171923;border:1px solid #2b2e3a;border-radius:10px;padding:.55rem;}
div[data-baseweb="tab-list"]{gap:4px;background:#141620;padding:4px;border-radius:10px;}
button[data-baseweb="tab"]{font-size:.68rem!important;border-radius:8px!important;}
button[data-baseweb="tab"][aria-selected="true"]{background:#272a37!important;color:#fff!important;}
hr{border-color:#2a2d38!important;}
</style>
""", unsafe_allow_html=True)

# ============================================================
# HELPERS
# ============================================================
GROUP_ORDER = ["Iron_ore", "Flux", "Recycle", "Fuel"]
GROUP_LABEL = {"Iron_ore":"Iron Ore","Flux":"Flux","Recycle":"Recycle","Fuel":"Fuel"}
GROUP_COLORS = {"Iron_ore":"#3d7ff0","Flux":"#42c77a","Recycle":"#f3b63f","Fuel":"#ef5b62"}

def active_df():
    out = st.session_state.df.copy()
    for m in out.index:
        if not st.session_state.availability.get(m, True):
            out.loc[m, "Available_Tonnes"] = 0
    return out

def set_dataset(new_df, source_name):
    st.session_state.df = new_df.copy()
    st.session_state.source_name = source_name
    st.session_state.availability = {m: True for m in new_df.index}
    st.session_state.result = None
    st.session_state.previous_cost = None
    st.session_state.manual_base = None
    st.session_state.manual_adjusted = None
    st.session_state.what_if = None
    st.session_state.inputs_changed = False

def quality_status(achieved):
    if achieved is None:
        return False, []
    checks = quality_checks(achieved, TARGETS)
    failed = [k for k,v in checks.items() if not v]
    return not failed, failed

def html_table(df, total=False, money_cols=None, status_col=None):
    money_cols = money_cols or set()
    cols = list(df.columns)
    rows = []
    for _, r in df.iterrows():
        is_total = str(r.get("Material","")) == "TOTAL"
        g = str(r.get("Group",""))
        cls = "total-row" if is_total else {
            "Iron_ore":"group-iron","Flux":"group-flux",
            "Recycle":"group-recycle","Fuel":"group-fuel"
        }.get(g,"")
        cells=[]
        for c in cols:
            v=r[c]
            if pd.isna(v): v=""
            if c in money_cols and v != "":
                v=f"₹{float(v):,.2f}"
            elif isinstance(v,float):
                v=f"{v:,.2f}"
            if status_col and c == status_col:
                s=str(v)
                if "OK" in s or "Available" in s or "Feasible" in s:
                    v=f'<span class="badge badge-ok">● {s}</span>'
                elif "OUT" in s or "Unavailable" in s or "NO" in s or "Hard" in s:
                    v=f'<span class="badge badge-out">● {s}</span>'
            cells.append(f"<td>{v}</td>")
        rows.append(f'<tr class="{cls}">{"".join(cells)}</tr>')
    header="".join(f"<th>{c}</th>" for c in cols)
    return f'<div class="table-wrap"><table class="pretty"><thead><tr>{header}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'

def cost_breakdown(blend, df):
    bd, cost, burden = calculate_cost_breakdown(blend, df)
    bd["_ord"] = bd["Group"].map({g:i for i,g in enumerate(GROUP_ORDER)}).fillna(99)
    bd = bd.sort_values(["_ord","Material"]).drop(columns="_ord")
    total = pd.DataFrame([{
        "Material":"TOTAL","Group":"",
        "kg/t":burden,"% of Burden":100.0,
        "Cost Rs/t":cost,"% of Cost":100.0
    }])
    return pd.concat([bd,total],ignore_index=True), cost, burden

def run_optimizer(reference_blend=None):
    before = st.session_state.result["cost"] if st.session_state.result else None
    result = solve_blend_with_compensation(
        active_df(), 1000, TARGETS, baseline_blend=reference_blend
    )
    st.session_state.previous_cost = before
    st.session_state.result = {
        "status":result[0],"blend":result[1],"cost":result[2],
        "achieved":result[3],"diagnostics":result[4],
        "fallback":result[5],"df":active_df().copy()
    }
    st.session_state.inputs_changed=False
    st.session_state.manual_base = result[1].copy() if result[1] else None
    st.session_state.manual_adjusted = result[1].copy() if result[1] else None

def apply_editor_changes(edited):
    changed=False
    for _, row in edited.iterrows():
        m=row["Material"]
        p=float(row["Price (₹/t)"])
        stock=float(row["RM Stock (t)"])
        av=bool(row["Available"])
        if p != float(st.session_state.df.loc[m,"Price_Rs_t"]):
            st.session_state.df.loc[m,"Price_Rs_t"]=p; changed=True
        if stock != float(st.session_state.df.loc[m,"Available_Tonnes"]):
            st.session_state.df.loc[m,"Available_Tonnes"]=stock; changed=True
        if av != bool(st.session_state.availability.get(m,True)):
            st.session_state.availability[m]=av; changed=True
    if changed:
        st.session_state.inputs_changed=True

def render_commercial_editor(key="commercial"):
    rows=[]
    for m in st.session_state.df.index:
        rows.append({
            "Material":m,
            "Group":GROUP_LABEL.get(st.session_state.df.loc[m,"Group"],st.session_state.df.loc[m,"Group"]),
            "Available":bool(st.session_state.availability.get(m,True)),
            "Price (₹/t)":float(st.session_state.df.loc[m,"Price_Rs_t"]),
            "RM Stock (t)":float(st.session_state.df.loc[m,"Available_Tonnes"]),
            "Tech Max":float(st.session_state.df.loc[m,"Tech_Max"]),
        })
    ed=st.data_editor(pd.DataFrame(rows),hide_index=True,use_container_width=True,height=390,key=key,
        disabled=["Material","Group","Tech Max"],
        column_config={
            "Available":st.column_config.CheckboxColumn("Available",help="OFF = optimizer cannot use this material."),
            "Price (₹/t)":st.column_config.NumberColumn("Price (₹/t)",min_value=0,step=1,format="₹ %.0f"),
            "RM Stock (t)":st.column_config.NumberColumn("RM Stock (t)",min_value=0,step=100,format="%.0f"),
            "Tech Max":st.column_config.NumberColumn("Tech Max",format="%.0f"),
        })
    apply_editor_changes(ed)

def quality_html(achieved):
    q=quality_table(achieved,TARGETS)
    q["Status"]=q["Status"].map({"OK":"OK","OUT":"OUT"})
    return html_table(q,status_col="Status")

def donut(data, title):
    fig=px.pie(data,names="Group",values="Value",hole=.62,
               color="Group",color_discrete_map=GROUP_COLORS)
    fig.update_traces(textposition="inside",textinfo="percent",hovertemplate="<b>%{label}</b><br>%{value:.1f}<extra></extra>")
    fig.update_layout(
        height=330,margin=dict(l=5,r=5,t=25,b=5),
        paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e9ebf0",size=11),showlegend=True,
        legend=dict(orientation="v",x=.99,y=.5,xanchor="right")
    )
    fig.add_annotation(text=f"<b>{data['Value'].sum():,.1f}</b><br><span style='font-size:11px'>kg/t</span>",
                       x=.5,y=.5,showarrow=False,font=dict(size=18,color="#f5f6fa"))
    return fig

# ============================================================
# SESSION
# ============================================================
if "df" not in st.session_state:
    set_dataset(get_default_chemistry(),"Built-in Master Chemistry")
if "nav" not in st.session_state: st.session_state.nav="Dashboard"
if "result" not in st.session_state: st.session_state.result=None
if "previous_cost" not in st.session_state: st.session_state.previous_cost=None
if "inputs_changed" not in st.session_state: st.session_state.inputs_changed=False
if "manual_base" not in st.session_state: st.session_state.manual_base=None
if "manual_adjusted" not in st.session_state: st.session_state.manual_adjusted=None
if "what_if" not in st.session_state: st.session_state.what_if=None

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown(
        '<div class="brand-title">🏭 BAJAJ MUKAND</div>'
        '<div class="brand-sub">Alloy Steel Group • Hospet Plant</div>',
        unsafe_allow_html=True
    )
    st.markdown('<div class="jv-title">KALYANI × MUKAND</div><div class="jv-sub">Joint Venture • Hospet Plant</div>',unsafe_allow_html=True)
    st.markdown("---")

    groups=[
        ("WORKSPACE",[("🏠","Dashboard")]),
        ("OPTIMIZATION",[("📦","RM Stock"),("🥧","Burden Composition"),("₹","Cost Composition"),("🎯","Optimization Results"),("🔧","Manual Adjustment")]),
        ("ANALYSIS",[("🔬","What-if Analysis"),("⚠️","Bottleneck Analysis")]),
        ("SYSTEM",[("📊","Reports"),("⚙️","Upload & Settings")])
    ]
    for title,items in groups:
        st.markdown(f'<div class="nav-group">{title}</div>',unsafe_allow_html=True)
        for icon,item in items:
            if st.button(f"{icon}  {item}",key=f"nav_{item}",use_container_width=True,
                         type="primary" if st.session_state.nav==item else "secondary"):
                st.session_state.nav=item
                st.rerun()

    st.markdown("---")
    st.markdown(f'<div class="nav-note"><b>DATA SOURCE</b><br>{st.session_state.source_name}<br>{len(st.session_state.df)} materials loaded</div>',unsafe_allow_html=True)
    st.markdown('<div class="nav-note">Sinter Burden Optimizer<br><b>v6.0 • Industrial UI</b></div>',unsafe_allow_html=True)

# ============================================================
# TOP HEADER
# ============================================================
h1,h2,h3=st.columns([5.4,2.0,1.35])
with h1:
    st.markdown("# SINTER BURDEN OPTIMIZER")
    st.markdown('<div class="muted">Cost-optimal sinter mix • quality assurance • material availability intelligence</div>',unsafe_allow_html=True)
with h2:
    ok,failed=quality_status(st.session_state.result["achieved"]) if st.session_state.result else (True,[])
    if st.session_state.result and not ok:
        st.markdown('<div class="badge badge-out" style="width:100%;justify-content:center;padding:9px">⚠ QUALITY ALERT</div>',unsafe_allow_html=True)
    else:
        st.markdown('<div class="badge badge-ok" style="width:100%;justify-content:center;padding:9px">✓ QUALITY OK</div>',unsafe_allow_html=True)
with h3:
    now=datetime.now()
    st.markdown(f'<div style="text-align:right;font-size:.63rem;color:#9aa0b0"><b>PLANT: HOSPET</b><br>{now:%d %b %Y}<br>{now:%I:%M %p}</div>',unsafe_allow_html=True)

# ============================================================
# DASHBOARD
# ============================================================
def dashboard_page():
    # Hero/control strip
    st.markdown('<div class="hero">',unsafe_allow_html=True)
    c1,c2,c3=st.columns([4.5,2.0,1.65])
    with c1:
        st.markdown('<div class="eyebrow">ACTIVE WORKSPACE</div>',unsafe_allow_html=True)
        st.markdown(f"**{st.session_state.source_name}**")
        st.markdown(f'<span class="small">{len(st.session_state.df)} materials • prices & RM stock editable • availability toggle enabled</span>',unsafe_allow_html=True)
    with c2:
        up=st.file_uploader("Upload master chemistry",type=["xlsx"],label_visibility="collapsed",key="dash_upload")
        if up:
            try:
                loaded=load_chemistry_from_excel(up)
                if st.button("Use Uploaded Chemistry",use_container_width=True):
                    set_dataset(loaded,f"Uploaded • {up.name}");st.rerun()
            except Exception as e: st.error(str(e))
    with c3:
        if st.button("🚀 RUN OPTIMIZER",type="primary",use_container_width=True):
            with st.spinner("Solving burden with PuLP / CBC..."):
                run_optimizer()
            st.rerun()
    st.markdown('</div>',unsafe_allow_html=True)

    if st.session_state.inputs_changed:
        st.markdown('<div class="notice notice-warn">✏ Commercial inputs changed. Run the optimizer to refresh the solution.</div>',unsafe_allow_html=True)
    st.write("")

    result=st.session_state.result
    if not result or result["blend"] is None:
        st.info("Edit RM Stock / Price / Availability if required, then click RUN OPTIMIZER.")
        render_commercial_editor("dashboard_editor")
        return

    r_df=result["df"]; blend=result["blend"]; achieved=result["achieved"]; cost=result["cost"]
    bd,total_cost,total_burden=cost_breakdown(blend,r_df)
    groups=bd[bd["Material"]!="TOTAL"].groupby("Group")["kg/t"].sum().reindex(GROUP_ORDER).fillna(0)
    group_cost=bd[bd["Material"]!="TOTAL"].groupby("Group")["Cost Rs/t"].sum().reindex(GROUP_ORDER).fillna(0)

    # KPI row
    kcols=st.columns(5)
    delta=""
    if st.session_state.previous_cost is not None and cost is not None:
        d=cost-st.session_state.previous_cost
        delta=f"{'↓' if d<0 else '↑'} ₹{abs(d):,.2f}/t"
    cards=[
        ("kpi-blue","TOTAL COST",f"₹ {cost:,.2f}/t","Cost per tonne"),
        ("kpi-green","TOTAL BURDEN",f"{total_burden:,.1f} kg/t","Total mix per tonne"),
        ("kpi-amber","ACHIEVED Fe",f"{achieved['Fe']:.2f}% ",f"Target {FE_LOWER:.1f}–{FE_UPPER:.1f}%"),
        ("kpi-cyan","SOLUTION","Optimal" if result["status"]=="Optimal" else "Review","CBC optimization status"),
        ("kpi-purple","COST CHANGE",delta or "—","vs previous run"),
    ]
    for col,(cl,lab,val,sub) in zip(kcols,cards):
        with col:
            st.markdown(f'<div class="kpi {cl}"><div class="kpi-label">{lab}</div><div class="kpi-value">{val}</div><div class="kpi-sub">{sub}</div></div>',unsafe_allow_html=True)

    st.write("")
    ok,failed=quality_status(achieved)
    st.markdown(
        f'<div class="notice{" notice-bad" if not ok else ""}">{"● QUALITY OK — All mandatory quality constraints satisfied" if ok else "● QUALITY ALERT — "+", ".join(failed)+" outside target"}</div>',
        unsafe_allow_html=True)

    st.write("")
    # Main workspace + right rail
    main,rail=st.columns([4.0,1.15])
    with main:
        # Top composition row
        a,b,c=st.columns([1.55,1.0,1.45])
        with a:
            st.markdown('<div class="panel">',unsafe_allow_html=True)
            st.markdown('<div class="section-title">RM COMMERCIAL INPUTS</div>',unsafe_allow_html=True)
            st.markdown('<div class="edit-hint">✏ <b>Editable</b> Price • RM Stock • Availability &nbsp; | &nbsp; 🔒 Chemistry / Tech Max</div>',unsafe_allow_html=True)
            render_commercial_editor("dashboard_editor_result")
            st.markdown('</div>',unsafe_allow_html=True)
        with b:
            st.markdown('<div class="panel">',unsafe_allow_html=True)
            st.markdown('<div class="section-title">BURDEN COMPOSITION</div>',unsafe_allow_html=True)
            data=pd.DataFrame({"Group":[GROUP_LABEL[g] for g in GROUP_ORDER],"Value":[groups[g] for g in GROUP_ORDER]})
            data["Group"]=data["Group"].map({"Iron Ore":"Iron_ore","Flux":"Flux","Recycle":"Recycle","Fuel":"Fuel"})
            # use internal group labels for colors
            fig=donut(data,"")
            st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
            st.markdown('<div class="small">Sequential order: Iron Ore → Flux → Recycle → Fuel</div>',unsafe_allow_html=True)
            st.markdown('</div>',unsafe_allow_html=True)
        with c:
            st.markdown('<div class="panel">',unsafe_allow_html=True)
            st.markdown('<div class="section-title">FINAL SINTER CHEMISTRY</div>',unsafe_allow_html=True)
            st.markdown(quality_html(achieved),unsafe_allow_html=True)
            st.markdown('</div>',unsafe_allow_html=True)

        st.write("")
        # Lower row
        a,b=st.columns([1.05,1.95])
        with a:
            st.markdown('<div class="panel">',unsafe_allow_html=True)
            st.markdown('<div class="section-title">RAW MATERIAL CHEMISTRY</div>',unsafe_allow_html=True)
            chem=r_df[["Group","Fe","SiO2","Al2O3","CaO","MgO","LOI"]].copy().reset_index().rename(columns={"index":"Material"})
            chem["Group"]=chem["Group"].map(GROUP_LABEL)
            st.markdown(html_table(chem.round(3)),unsafe_allow_html=True)
            st.markdown('</div>',unsafe_allow_html=True)
        with b:
            st.markdown('<div class="panel">',unsafe_allow_html=True)
            st.markdown('<div class="section-title">OPTIMAL BURDEN & COST BREAKDOWN</div>',unsafe_allow_html=True)
            display=bd.copy()
            display["Group"]=display["Group"].map(GROUP_LABEL).fillna("")
            st.markdown(html_table(display.round(2),money_cols={"Cost Rs/t"}),unsafe_allow_html=True)
            st.markdown('</div>',unsafe_allow_html=True)

        st.write("")
        st.markdown('<div class="panel">',unsafe_allow_html=True)
        st.markdown('<div class="section-title">COST COMPOSITION</div>',unsafe_allow_html=True)
        cc1,cc2,cc3,cc4=st.columns(4)
        for col,g in zip([cc1,cc2,cc3,cc4],GROUP_ORDER):
            val=float(group_cost[g])
            pct=val/total_cost*100 if total_cost else 0
            with col:
                st.markdown(f'<div class="kpi {"kpi-blue" if g=="Iron_ore" else "kpi-green" if g=="Flux" else "kpi-amber" if g=="Recycle" else "kpi-red"}"><div class="kpi-label">{GROUP_LABEL[g]} COST</div><div class="kpi-value">₹{val:,.2f}</div><div class="kpi-sub">{pct:.1f}% of total cost</div><div class="progress"><div style="width:{min(100,pct)}%"></div></div></div>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)

    with rail:
        st.markdown('<div class="right-card">',unsafe_allow_html=True)
        st.markdown('<div class="section-title">OPTIMIZER BRIEF</div>',unsafe_allow_html=True)
        st.markdown('<div class="timeline">',unsafe_allow_html=True)
        items=[
            ("Quality Gate","All mandatory chemistry limits checked"),
            ("Cost Engine","Minimum-cost feasible burden selected"),
            ("Stock Gate","Availability and RM stock enforced"),
            ("Decision","Recipe ready for production review"),
        ]
        for title,sub in items:
            st.markdown(f'<div class="timeline-item"><div class="timeline-title">{title}</div><div class="timeline-sub">{sub}</div></div>',unsafe_allow_html=True)
        st.markdown('</div></div>',unsafe_allow_html=True)
        st.write("")
        st.markdown('<div class="right-card">',unsafe_allow_html=True)
        st.markdown('<div class="section-title">QUALITY WATCH</div>',unsafe_allow_html=True)
        for k,v in quality_checks(achieved,TARGETS).items():
            st.markdown(f'<div style="display:flex;justify-content:space-between;font-size:.68rem;padding:.34rem 0;border-bottom:1px solid #272a35"><span>{k}</span><span class="badge {"badge-ok" if v else "badge-out"}">{"OK" if v else "OUT"}</span></div>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)

# ============================================================
# PAGES
# ============================================================
def rm_stock_page():
    st.markdown("## RM Stock")
    st.caption("Commercial inputs used by the optimizer.")
    st.markdown('<div class="edit-hint">✏ Editable: Price • RM Stock • Availability &nbsp; | &nbsp; 🔒 Chemistry • Technical Max</div>',unsafe_allow_html=True)
    render_commercial_editor("rm_stock")
    if st.session_state.inputs_changed:
        st.markdown('<div class="notice notice-warn">Inputs changed — run the optimizer from Dashboard.</div>',unsafe_allow_html=True)

def burden_page():
    st.markdown("## Burden Composition")
    if not st.session_state.result:
        st.info("Run the optimizer first."); return
    r=st.session_state.result
    bd,cost,burden=cost_breakdown(r["blend"],r["df"])
    x=bd[bd["Material"]!="TOTAL"].groupby("Group")["kg/t"].sum().reindex(GROUP_ORDER).fillna(0)
    data=pd.DataFrame({"Group":GROUP_ORDER,"Value":[x[g] for g in GROUP_ORDER]})
    l,rcol=st.columns([1.4,1.6])
    with l:
        st.plotly_chart(donut(data,""),use_container_width=True,config={"displayModeBar":False})
    with rcol:
        st.markdown('<div class="panel">',unsafe_allow_html=True)
        st.markdown('<div class="section-title">GROUP TOTALS</div>',unsafe_allow_html=True)
        rows=[]
        for g in GROUP_ORDER:
            rows.append({"Group":GROUP_LABEL[g],"kg/t":x[g],"% of Burden":x[g]/burden*100 if burden else 0})
        rows.append({"Group":"TOTAL","kg/t":burden,"% of Burden":100})
        st.markdown(html_table(pd.DataFrame(rows).round(2)),unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)

def cost_page():
    st.markdown("## Cost Composition")
    if not st.session_state.result:
        st.info("Run the optimizer first."); return
    r=st.session_state.result
    bd,cost,burden=cost_breakdown(r["blend"],r["df"])
    x=bd[bd["Material"]!="TOTAL"].groupby("Group")["Cost Rs/t"].sum().reindex(GROUP_ORDER).fillna(0)
    data=pd.DataFrame({"Group":GROUP_ORDER,"Value":[x[g] for g in GROUP_ORDER]})
    a,b=st.columns([1.35,1.65])
    with a: st.plotly_chart(donut(data,""),use_container_width=True,config={"displayModeBar":False})
    with b:
        rows=[{"Group":GROUP_LABEL[g],"Cost Rs/t":x[g],"% of Cost":x[g]/cost*100 if cost else 0} for g in GROUP_ORDER]
        rows.append({"Group":"TOTAL","Cost Rs/t":cost,"% of Cost":100})
        st.markdown(html_table(pd.DataFrame(rows).round(2),money_cols={"Cost Rs/t"}),unsafe_allow_html=True)

def results_page():
    st.markdown("## Optimization Results")
    if not st.session_state.result:
        st.info("Run the optimizer first."); return
    r=st.session_state.result
    st.markdown(f'<div class="notice {"notice-bad" if r["fallback"] else ""}">{ "REFERENCE / QUALITY SHORTFALL" if r["fallback"] else "OPTIMAL SOLUTION"} • ₹{r["cost"]:,.2f}/t</div>',unsafe_allow_html=True)
    st.write("")
    st.markdown(quality_html(r["achieved"]),unsafe_allow_html=True)
    st.write("")
    bd,_,_=cost_breakdown(r["blend"],r["df"])
    st.markdown(html_table(bd.round(2),money_cols={"Cost Rs/t"}),unsafe_allow_html=True)

def manual_page():
    st.markdown("## Manual Adjustment")
    st.caption("Use the optimized burden as the baseline. Iron Ore and Flux are adjustable; Recycle and Fuel remain fixed.")
    if not st.session_state.result or not st.session_state.result["blend"]:
        st.info("Run the optimizer first."); return

    r=st.session_state.result
    df=r["df"]
    base=st.session_state.manual_base or r["blend"].copy()
    if st.session_state.manual_base is None:
        st.session_state.manual_base=base.copy()
    adjustable=[m for m in base if df.loc[m,"Group"] in ("Iron_ore","Flux")]
    fixed=[m for m in base if df.loc[m,"Group"] in ("Recycle","Fuel")]
    st.markdown('<div class="edit-hint">🎚 Iron Ore: ±15% &nbsp; | &nbsp; Flux: ±10% &nbsp; | &nbsp; Recycle/Fuel: fixed &nbsp; | &nbsp; Total burden preserved</div>',unsafe_allow_html=True)

    requested={}
    cols=st.columns(2)
    for i,m in enumerate(adjustable):
        b=float(base[m]); rng=.15 if df.loc[m,"Group"]=="Iron_ore" else .10
        with cols[i%2]:
            requested[m]=st.slider(f"{m} — kg/t",max(0.0,b*(1-rng)),b*(1+rng),b,.5,key=f"manual_slider_{m}")
    adjusted=redistribute_adjustment(base,df,requested)
    for m in fixed: adjusted[m]=base[m]
    st.session_state.manual_adjusted=adjusted

    ach=compute_achieved(adjusted,df,1000)
    adj_cost=sum(adjusted[m]*df.loc[m,"Price_Rs_t"]/1000 for m in adjusted)
    base_cost=r["cost"] or 0
    delta=adj_cost-base_cost
    total=sum(adjusted.values())

    k=st.columns(5)
    cards=[
        ("kpi-blue","BASE COST",f"₹{base_cost:,.2f}/t","Optimized"),
        ("kpi-purple","ADJUSTED COST",f"₹{adj_cost:,.2f}/t",f"{delta:+,.2f}/t"),
        ("kpi-green","TOTAL BURDEN",f"{total:,.1f} kg/t","Preserved"),
        ("kpi-amber","ADJUSTED Fe",f"{ach['Fe']:.2f}%","Live chemistry"),
        ("kpi-cyan","STATUS","OK" if all(quality_checks(ach,TARGETS).values()) else "CHECK","After adjustment"),
    ]
    for col,(cl,l,v,s) in zip(k,cards):
        with col: st.markdown(f'<div class="kpi {cl}"><div class="kpi-label">{l}</div><div class="kpi-value">{v}</div><div class="kpi-sub">{s}</div></div>',unsafe_allow_html=True)

    st.write("")
    a,b=st.columns([1.3,1.7])
    with a:
        st.markdown('<div class="section-title">ADJUSTED QUALITY</div>',unsafe_allow_html=True)
        st.markdown(quality_html(ach),unsafe_allow_html=True)
    with b:
        st.markdown('<div class="section-title">ADJUSTED BURDEN & COST</div>',unsafe_allow_html=True)
        bd,_,_=cost_breakdown(adjusted,df)
        st.markdown(html_table(bd.round(2),money_cols={"Cost Rs/t"}),unsafe_allow_html=True)

    st.write("")
    b1,b2,b3=st.columns(3)
    with b1:
        if st.button("↩ Reset to Optimized",use_container_width=True):
            for m in adjustable:
                st.session_state[f"manual_slider_{m}"]=float(base[m])
            st.session_state.manual_adjusted=base.copy()
            st.rerun()
    with b2:
        if st.button("✅ Apply Adjustment",type="primary",use_container_width=True):
            st.session_state.active_manual=adjusted.copy()
            st.success("Manual burden applied as the active recipe.")
    with b3:
        if st.button("🚀 Apply & Re-run Optimizer",use_container_width=True):
            with st.spinner("Re-optimizing around the adjusted recipe..."):
                run_optimizer(reference_blend=adjusted)
            st.success("Optimizer re-run completed.")
            st.rerun()

def what_if_page():
    st.markdown("## What-if Analysis")
    st.caption("Test the cost and feasibility impact if an available iron ore, flux or fuel becomes unavailable.")
    if st.button("▶ Evaluate Missing-Material Scenarios",type="primary"):
        with st.spinner("Running scenarios..."):
            st.session_state.what_if=what_if_analysis(active_df(),TARGETS)
    if st.session_state.what_if is not None:
        wi=st.session_state.what_if.copy()
        if "Group" in wi.columns:
            wi["_o"]=wi["Group"].map({g:i for i,g in enumerate(GROUP_ORDER)}).fillna(99)
            wi=wi.sort_values(["_o","Missing Material"]).drop(columns="_o")
        st.markdown(html_table(wi.fillna("—")),unsafe_allow_html=True)

def bottleneck_page():
    st.markdown("## Bottleneck Analysis")
    if not st.session_state.result:
        st.info("Run the optimizer first."); return
    r=st.session_state.result
    if r["diagnostics"]:
        for d in r["diagnostics"]:
            st.markdown(f'<div class="notice notice-warn">⚠ {d}</div>',unsafe_allow_html=True)
            st.write("")
    st.markdown(quality_html(r["achieved"]),unsafe_allow_html=True)

def reports_page():
    st.markdown("## Reports")
    if not st.session_state.result:
        st.info("Run the optimizer first."); return
    r=st.session_state.result
    bd,cost,burden=cost_breakdown(r["blend"],r["df"])
    report=bd.copy()
    st.markdown(html_table(report.round(2),money_cols={"Cost Rs/t"}),unsafe_allow_html=True)
    st.download_button("⬇ Download Optimization Report",report.to_csv(index=False).encode(),"sinter_optimization_report.csv","text/csv",use_container_width=True)

def settings_page():
    st.markdown("## Upload & Settings")
    st.markdown(f"**Active source:** {st.session_state.source_name}")
    uploaded=st.file_uploader("Upload Master Chemistry Excel",type=["xlsx"],key="settings_excel")
    if uploaded:
        try:
            loaded=load_chemistry_from_excel(uploaded)
            if st.button("Activate Uploaded Excel",type="primary"):
                set_dataset(loaded,f"Uploaded • {uploaded.name}");st.rerun()
        except Exception as exc: st.error(str(exc))
    if st.button("Restore Built-in Master Chemistry"):
        set_dataset(get_default_chemistry(),"Built-in Master Chemistry");st.rerun()

def chemistry_page():
    st.markdown("## Raw Material Chemistry")
    df=st.session_state.df.copy().reset_index()
    df["Group"]=df["Group"].map(GROUP_LABEL)
    cols=["Material","Group","Fe","SiO2","Al2O3","CaO","MgO","LOI","Tech_Min","Tech_Max"]
    st.markdown(html_table(df[cols].round(3)),unsafe_allow_html=True)

# ============================================================
# ROUTING
# ============================================================
nav=st.session_state.nav
if nav=="Dashboard": dashboard_page()
elif nav=="RM Stock": rm_stock_page()
elif nav=="Burden Composition": burden_page()
elif nav=="Cost Composition": cost_page()
elif nav=="Optimization Results": results_page()
elif nav=="Manual Adjustment": manual_page()
elif nav=="What-if Analysis": what_if_page()
elif nav=="Bottleneck Analysis": bottleneck_page()
elif nav=="Reports": reports_page()
elif nav=="Upload & Settings": settings_page()
