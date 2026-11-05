import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
INK="#17211f"; BR="#0f6b63"; SOFT="#e1f1ee"; LINE="#9fb3ae"; G="#2f855a"; Y="#d9a400"; R="#b42318"; GREY="#eef2f1"
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":8.5})
def box(ax,x,y,w,h,text,fc=SOFT,ec=BR,fs=8.2,bold=False,tc=INK):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.01,rounding_size=0.02",fc=fc,ec=ec,lw=1.1))
    ax.text(x+w/2,y+h/2,text,ha="center",va="center",fontsize=fs,color=tc,fontweight="bold" if bold else "normal",wrap=True,linespacing=1.25)
def arrow(ax,x1,y1,x2,y2,c=BR,ls="-",rad=0.0):
    ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle="-|>",mutation_scale=11,lw=1.2,color=c,linestyle=ls,connectionstyle=f"arc3,rad={rad}"))
def new(w=6.6,h=4.2):
    f,ax=plt.subplots(figsize=(w,h)); ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off"); return f,ax

# Figure 1 conceptual framework
f,ax=new(6.8,4.8)
ax.text(0.5,0.975,"Pressures and cues (what people live with)",ha="center",fontsize=9,fontweight="bold",color=BR)
box(ax,0.02,0.80,0.96,0.15,"Academic load and exams  |  Money, fees and informal loans  |  Family and home\nBeing away  |  News, social media and loss  |  Sleep and alcohol",fc=GREY,ec=LINE)
arrow(ax,0.5,0.80,0.5,0.73)
box(ax,0.02,0.52,0.30,0.20,"Private wellbeing check\non the phone\nPHQ-9, GAD-7, PC-PTSD-5\nAUDIT-C, resilience,\nmoney module, weekly pulse",fs=7.6)
box(ax,0.37,0.52,0.26,0.20,"Result for the person\nGreen  Amber  Red\n(support, never a judgement)",fc="#fff",ec=BR)
box(ax,0.68,0.52,0.30,0.20,"Choice of what to do\nlessons  ask the nurse\ncall-back  navigator\nchaplain  referral",bold=False)
arrow(ax,0.32,0.62,0.37,0.62); arrow(ax,0.63,0.62,0.68,0.62)
arrow(ax,0.83,0.52,0.83,0.43)
box(ax,0.02,0.22,0.96,0.20,"Outcomes of the pilot\nUptake  |  time to first contact  |  referrals that reached a visit\nUsability (SUS)  |  perceived confidentiality  |  help-seeking intention\nFeasibility  |  retention of students (exploratory)",fc="#fff",ec=BR)
box(ax,0.02,0.02,0.46,0.14,"Moderators: stigma, trust that lecturers and\ncommanders cannot see answers, fear of consequences",fc=GREY,ec=LINE,fs=7.6)
box(ax,0.52,0.02,0.46,0.14,"Adaptive loop: group early warning > pre-set\nrule > change service > log the change",fc=GREY,ec=LINE,fs=7.6)
arrow(ax,0.25,0.16,0.25,0.22,c=LINE); arrow(ax,0.75,0.16,0.75,0.22,c=LINE)
f.savefig("fig/fig1_framework.png",dpi=200,bbox_inches="tight",facecolor="white"); plt.close(f)

# Figure 2 data flow and access
f,ax=new(6.8,5.0)
box(ax,0.02,0.42,0.18,0.16,"Student phone\n(scores shown\nonly here)",fc="#fff",bold=True)
box(ax,0.27,0.72,0.34,0.20,"Research database\nanonymous answers\nonly researchers read",fc=SOFT,fs=7.8)
box(ax,0.27,0.42,0.34,0.16,"Nurse queue\ncall-back requests and\nanonymous questions",fc=SOFT,fs=7.8)
box(ax,0.27,0.08,0.34,0.20,"College support office\nsees ONLY a colour band\nof people who chose\nto share it",fc="#fdf3d4",ec=Y,fs=7.8)
box(ax,0.70,0.06,0.29,0.24,"Lecturers, commanders\nand managers:\ngroup figures only\n(groups of 10 or more)",fc=GREY,ec=LINE,fs=7.6)
box(ax,0.70,0.72,0.29,0.20,"College registry\n(honest broker)\ncode + outcome only",fc=GREY,ec=LINE,fs=7.8)
box(ax,0.70,0.42,0.29,0.16,"Marks, progression\nand discipline:\nno link to answers",fc="#fff",ec=R,bold=True,tc=R)
arrow(ax,0.20,0.54,0.27,0.80,ls="-"); ax.text(0.19,0.72,"anonymous\nanswers",fontsize=7,color=BR,ha="right")
arrow(ax,0.20,0.50,0.27,0.50); ax.text(0.205,0.515,"if asked",fontsize=7,color=BR)
arrow(ax,0.20,0.45,0.27,0.22,c=Y); ax.text(0.10,0.30,"opt-in: colour\nonly, withdrawable",fontsize=7,color="#8a6a00",ha="center")
arrow(ax,0.70,0.82,0.61,0.82,c=LINE); ax.text(0.655,0.86,"outcomes",fontsize=7,color=INK,ha="center")
arrow(ax,0.61,0.18,0.70,0.18,c=LINE,ls="--")
ax.text(0.5,0.97,"Who can see what",ha="center",fontsize=10,fontweight="bold",color=BR)
ax.text(0.5,0.02,"No name or service number is stored with any answer. Detailed scores never leave the phone except as anonymous research data.",ha="center",fontsize=7.4,color=INK)
f.savefig("fig/fig2_access.png",dpi=200,bbox_inches="tight",facecolor="white"); plt.close(f)

# Figure 3 adaptive loop
f,ax=new(6.6,4.6)
steps=[("1  Sense","Weekly pulse, check-ins, anonymous questions, topics people ask about, stressors people tick themselves"),
       ("2  Detect","Group early warning: struggling-or-worse up 10 points on the usual (groups of 10 or more only)"),
       ("3  Decide","Pre-agreed rules; nurse and welfare lead review; ethics focal person informed"),
       ("4  Respond","New lesson or banner, extra nurse hours, welfare drop-in, a question switched on or off"),
       ("5  Record","Change log: trigger, change, approver; protocol version stamped on every response")]
h=0.135; gap=0.03; y0=0.78
for i,(t,d) in enumerate(steps):
    y=y0-i*(h+gap)
    box(ax,0.03,y,0.17,h,t,fc=BR,ec=BR,fs=7.8,bold=True,tc="white")
    import textwrap
    box(ax,0.21,y,0.62,h,textwrap.fill(d,52),fc=SOFT if i%2==0 else "#fff",fs=7.4)
    if i<4: arrow(ax,0.115,y,0.115,y-gap)
arrow(ax,0.83,0.78-4*(h+gap)+h/2,0.93,0.78-4*(h+gap)+h/2,c=LINE,ls="--")
ax.plot([0.93,0.93],[0.78-4*(h+gap)+h/2,y0+h/2],color=LINE,ls="--",lw=1.2); arrow(ax,0.93,y0+h/2,0.83,y0+h/2,c=LINE,ls="--")
ax.text(0.965,0.45,"Did the change help?\n(uptake, time to contact,\nstressor mix)",rotation=90,ha="center",va="center",fontsize=7.2,color=INK)
ax.text(0.5,0.97,"Adaptive sense-and-respond loop",ha="center",fontsize=10,fontweight="bold",color=BR)
f.savefig("fig/fig3_loop.png",dpi=200,bbox_inches="tight",facecolor="white"); plt.close(f)

# Figure 4 Gantt
f,ax=plt.subplots(figsize=(6.6,3.3))
tasks=[("Approvals: ethics, NACOSTI, DCHS letter of support, data protection assessment",1,2),("Expert review of questions; testing with 10 to 15 students",2,3),("Build checks, safety protocol, nurse rota, peer champions",2,3),("Pilot at DCHS (4 weeks to 3 months): checks, pulse, call-back",4,6),("End-of-pilot feedback; registry outcome file (if agreed)",6,7),("Analysis (jamovi), costed adoption plan, policy brief",6,8),("Dissertation and dissemination",7,8)]
cols=[LINE,BR,BR,G,G,"#8a6a00","#8a6a00"]
for i,(t,a,b) in enumerate(tasks):
    ax.barh(len(tasks)-1-i,b-a+1,left=a-0.5,color=cols[i],height=0.55)
ax.set_yticks(range(len(tasks))); ax.set_yticklabels([t for t,_,_ in tasks][::-1],fontsize=7.4)
ax.set_xticks(range(1,9)); ax.set_xticklabels(["M%d"%i for i in range(1,9)],fontsize=7.6); ax.set_xlim(0.5,8.5)
ax.grid(axis="x",color="#e3eae8"); ax.set_axisbelow(True)
for s in ("top","right"): ax.spines[s].set_visible(False)
ax.set_title("Eight-month work plan (M1 = first month after proposal approval)",fontsize=9.5,fontweight="bold",color=BR,loc="left")
f.savefig("fig/fig4_gantt.png",dpi=200,bbox_inches="tight",facecolor="white"); plt.close(f)
print("ok")
