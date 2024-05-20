from sqlalchemy import (Column, ForeignKey, Integer, MetaData, String, Table,
                        create_engine)
from sqlalchemy.orm import (Mapped, declarative_base, mapped_column,
                            relationship, sessionmaker)
from models import *
import os,re


# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Add scenarios
tc = ""
nfs = list()
nls = list()
ncs = list()
tcfs = list()
tcls = list()
tccs = list()

# Add TCs
TCs = [
    {'TC':'Cyclist crosses from the roadside', 'FI':'Information reception - FOV,, Plan - Prediction'},
    {'TC':'Front cyclist moves towards the road edge and halt', 'FI':'Plan-behavior interpretation & prediction'},
    {'TC':'Multiple vehicles cut in to ego path in a short time', 'FI':'Plan - situation understanding & decision making'},
    {'TC':'Traffic jam in front when neighbor lane is free', 'FI':'Plan - situation understanding + prediction'},
]

# Add tc scenarios
# for tc_row in TCs:
#     session.add(TriggeringCondition(triggering_condition_name=tc_row['TC'], functional_insufficiency=tc_row['FI'], functional_insufficiency_origin='expert'))
# session.commit()

# 
tcs = ["Cyclist_crosses_from_the_roadside",
        "Front_cyclist_moves_towards_the_road_edge_and_halt",
        "Multiple_vehicles_cut_in_to_ego_path_in_a_short_time",
        "Traffic_jam_in_front_when_neighbor_lane_is_free",
    ]
nfs = list()
nls = list()
ncs = list()
tcfs = dict()
tcls = dict()
tccs = dict()

for tc in tcs:
    tcfs[tc]=list()
    tcls[tc]=list()
    tccs[tc]=list()

def extract_number(filename):
    match1 = re.search(r'(\d+)\.scenic', filename)
    match2 = re.search(r'(\d+)\.md', filename)
    if match1:
        return int(match1.group(1))
    if match2:
        return int(match2.group(1))
    else:
        return float('inf')

dir_path = "/home/weidong/Tools/Scenic/scenic_projects/nominal_scenario_catalog/"
for dirpath, dirnames, filenames in os.walk(dir_path):
    for filename in filenames:
        # find nfs
        if re.compile(r"nf\d+\.md").match(filename):
            path = os.path.join(dirpath, filename)
            nfs.append(path)
        # find nls
        elif re.compile(r"nl\d+\.scenic").match(filename):
            path = os.path.join(dirpath, filename)
            nls.append(path)
        # find ncs
        elif re.compile(r"nc\d+\.scenic").match(filename):
            path = os.path.join(dirpath, filename)
            ncs.append(path)
        # find tcfs
        elif re.compile(r"tcf\d+\.md").match(filename):
            path = os.path.join(dirpath, filename)
            for tc in tcs:
                if tc in path:
                    tcfs[tc].append(path)
        # find tcls
        elif re.compile(r"tcl\d+\.scenic").match(filename):
            path = os.path.join(dirpath, filename)
            for tc in tcs:
                if tc in path:
                    tcls[tc].append(path)
        # find tccs
        elif re.compile(r"tcc\d+\.scenic").match(filename):
            path = os.path.join(dirpath, filename)
            for tc in tcs:
                if tc in path:
                    tccs[tc].append(path)
        else:
            assert(f"{filename} went wrong.")

# sort
nfs.sort(key=extract_number)
nls.sort(key=extract_number)
ncs.sort(key=extract_number)
for tc in tcfs.values():
    tc.sort(key=extract_number)
for tc in tcls.values():
    tc.sort(key=extract_number)
for tc in tccs.values():
    tc.sort(key=extract_number)

# convert to sql
for idx, path in enumerate(nfs):
    nfs[idx] = FunctionalNominalScenario(path=path)

for idx, path in enumerate(nls):
    nls[idx] = LogicalNominalScenario(path=path)

for idx, path in enumerate(ncs):
    ncs[idx] = ConcreteNominalScenario(path=path)

for idx, tc in enumerate(TCs):
    TCs[idx] = TriggeringCondition(triggering_condition_name=tc['TC'],functional_insufficiency=tc['FI'],functional_insufficiency_origin='expert')

for tcfs_tc in tcfs.values():
    for idx, path in enumerate(tcfs_tc):
        tcfs_tc[idx] = TCEnhancedFunctionalScenario(path=path)

for tcls_tc in tcls.values():
    for idx, path in enumerate(tcls_tc):
        tcls_tc[idx] = TCEnhancedLogicalScenario(path=path)

for tccs_tc in tccs.values():
    for idx, path in enumerate(tccs_tc):
        tccs_tc[idx] = TCEnhancedConcreteScenario(path=path)


# TC append tcf
for tc_idx, tc in enumerate(TCs):
    for tcf_idx, tcf in enumerate(tcfs[tc.triggering_condition_name.replace(' ','_')]):
        tc.tc_enhanced_functional_scenario_items.append(tcf)

# nf append nl, tcf
for nf_idx, nf in enumerate(nfs):
    for tcfs_tc in tcfs.values():
        for tcf in tcfs_tc:
            if int(re.search(r'tcf(\d+)\.md', tcf.path).group(1)) in range(nf_idx*2+1,nf_idx*2+3):
                nf.tc_enhanced_functional_scenario_items.append(tcf)
    for nl_idx, nl in enumerate(nls):
        if int(re.search(r'nl(\d+)\.scenic', nl.path).group(1)) in range(nf_idx*2+1,nf_idx*2+3):
            nf.logical_nominal_scenario_items.append(nl)

# tcf append tcl
for tc, tcfs_tc in tcfs.items():
    for tcf_idx, tcf in enumerate(tcfs_tc):
        if tcf_idx == 0:
            for tcl in tcls[tc]:
                try:
                    if int(re.search(r'tcl(\d+)\.scenic', tcl.path).group(1)) in [1,2,5,6]:
                        tcf.tc_enhanced_logical_scenario_items.append(tcl)
                except Exception as e:
                    print(e)
                    print(tcl)
                    print(tcl.path)
                    quit()
        if tcf_idx == 1:
            for tcl in tcls[tc]:
                if int(re.search(r'tcl(\d+)\.scenic', tcl.path).group(1)) in [3,4,7,8]:
                    tcf.tc_enhanced_logical_scenario_items.append(tcl)
        if tcf_idx == 2:
            for tcl in tcls[tc]:
                if int(re.search(r'tcl(\d+)\.scenic', tcl.path).group(1)) in [9,10,13,14]:
                    tcf.tc_enhanced_logical_scenario_items.append(tcl)
        if tcf_idx == 3:
            for tcl in tcls[tc]:
                if int(re.search(r'tcl(\d+)\.scenic', tcl.path).group(1)) in [11,12,15,16]:
                    tcf.tc_enhanced_logical_scenario_items.append(tcl)

# nl append nc, tcl
for nl_idx, nl in enumerate(nls):
    for tcls_tc in tcls.values():
        for tcl in tcls_tc:
            if int(re.search(r'tcl(\d+)\.scenic', tcl.path).group(1)) in range(4*nl_idx+1,4*nl_idx+5):
                nl.tc_enhanced_logical_scenario_items.append(tcl)
    for nc in ncs:
        if int(re.search(r'nc(\d+)\.scenic', nc.path).group(1)) in range(2*nl_idx+1,2*nl_idx+3):
            nl.concrete_nominal_scenario_items.append(nc)

# tcl append tcc
for tc, tcls_tc in tcls.items():
    for tcl_idx, tcl in enumerate(tcls_tc):
        tcl_n = int(re.search(r'tcl(\d+)\.scenic', tcl.path).group(1))
        if tcl_n in range(1,5):
            for tcc in tccs[tc]:
                if int(re.search(r'tcc(\d+)\.scenic', tcc.path).group(1)) in [1+2*(tcl_n-1),2+2*(tcl_n-1),9+2*(tcl_n-1),10+2*(tcl_n-1)]:
                    tcl.tc_enhanced_concrete_scenario_items.append(tcc)
        elif tcl_n in range(5,9):
            for tcc in tccs[tc]:
                if int(re.search(r'tcc(\d+)\.scenic', tcc.path).group(1)) in [17+2*(tcl_n-5),18+2*(tcl_n-5),25+2*(tcl_n-5),26+2*(tcl_n-5)]:
                    tcl.tc_enhanced_concrete_scenario_items.append(tcc)
        elif tcl_n in range(9,13):
            for tcc in tccs[tc]:
                if int(re.search(r'tcc(\d+)\.scenic', tcc.path).group(1)) in [33+2*(tcl_n-9),34+2*(tcl_n-9),41+2*(tcl_n-9),42+2*(tcl_n-9)]:
                    tcl.tc_enhanced_concrete_scenario_items.append(tcc)
        elif tcl_n in range(13,17):
            for tcc in tccs[tc]:
                if int(re.search(r'tcc(\d+)\.scenic', tcc.path).group(1)) in [49+2*(tcl_n-13),50+2*(tcl_n-13),57+2*(tcl_n-13),58+2*(tcl_n-13)]:
                    tcl.tc_enhanced_concrete_scenario_items.append(tcc)
        else:
            assert()

# nc append tcc
for nc_idx, nc in enumerate(ncs):
    for tccs_tc in tccs.values():
        for tcc in tccs_tc:
            if int(re.search(r'tcc(\d+)\.scenic', tcc.path).group(1)) in range(8*nc_idx+1,8*nc_idx+9):
                nc.tc_enhanced_concrete_scenario_items.append(tcc)


import json 

# Regulations
with open('regulations.json') as f:
    # Load JSON data
    data = json.load(f)
    regus = [(r['regulation'], r['required_behavior']) for r in data['regulations']]
    rbhbs = [(r['required_behavior'],r['hazardous_behavior']) for r in data['regulations']]

rb_hb = dict()
for rbhb_tuple in rbhbs:
    for idx, rb in enumerate(rbhb_tuple[0]):
        if rb in rb_hb:
            if rb_hb[rb] != rbhb_tuple[1][idx]:
                assert("rb has multiple hb.")
        rb_hb[rb] =  rbhb_tuple[1][idx]

rbs_sql = [RequiredBehavior(behavior_name=rb) for rb in rb_hb.keys()]


for regu in regus:
    reg = Regulation(regulation_description=regu[0])
    # regulation append rb
    for rb in regu[1]:
        for rb_sql in rbs_sql:
            if rb_sql.behavior_name == rb:
                reg.required_behaviors.append(rb_sql)
    
# rb append hb
for rb, hb in rb_hb.items():
    for rb_sql in rbs_sql:
        if rb_sql.behavior_name == rb:
            rb_sql.hazardous_behavior = HazardousBehavior(behavior_description=hb)


from sqlalchemy.exc import IntegrityError

# add regulations
session.add_all(rbs_sql)
# add tcs
session.add_all(TCs)
session.commit()
import time

time.sleep(3)
# 
tcls_sql = session.query(TCEnhancedLogicalScenario).all()

print(len(tcls_sql))
for tcl in tcls_sql:
    print(tcl.id)
    if int(re.search(r'tcl(\d+)\.scenic', tcl.path).group(1)) in [2,4,6,8,10,12,14,16] and "Cyclist_crosses_from_the_roadside" in tcl.path:
        for tcc in tcl.tc_enhanced_concrete_scenario_items:
            testcase = TestCase()
            testcase.tc_enhanced_concrete_scenario = tcc
            reg = session.query(Regulation).filter(Regulation.id.in_([1,4,7])).all()
            print(len(reg))
            for r in reg:
                testcase.regulations.append(r)
                print("Adding regs.")
            session.add(testcase)

    elif int(re.search(r'tcl(\d+)\.scenic', tcl.path).group(1)) in [1,3,5,7,9,11,13,15] and "Cyclist_crosses_from_the_roadside" in tcl.path:
        for tcc in tcl.tc_enhanced_concrete_scenario_items:
            testcase = TestCase()
            testcase.tc_enhanced_concrete_scenario = tcc
            reg = session.query(Regulation).filter(Regulation.id.in_([1,4,5,6])).all()
            for r in reg:
                testcase.regulations.append(r)
            session.add(testcase)

    elif "Front_cyclist_moves_towards_the_road_edge_and_halt" in tcl.path:
        for tcc in tcl.tc_enhanced_concrete_scenario_items:
            testcase = TestCase()
            testcase.tc_enhanced_concrete_scenario = tcc
            reg = session.query(Regulation).filter(Regulation.id.in_([1,3,5,8,11,13])).all()
            for r in reg:
                testcase.regulations.append(r)
            session.add(testcase)

    elif "Multiple_vehicles_cut_in_to_ego_path_in_a_short_time" in tcl.path:
        for tcc in tcl.tc_enhanced_concrete_scenario_items:
            testcase = TestCase()
            testcase.tc_enhanced_concrete_scenario = tcc
            reg = session.query(Regulation).filter(Regulation.id.in_([1,5,15])).all()
            for r in reg:
                testcase.regulations.append(r)
            session.add(testcase)

    elif "Traffic_jam_in_front_when_neighbor_lane_is_free" in tcl.path:
        for tcc in tcl.tc_enhanced_concrete_scenario_items:
            testcase = TestCase()
            testcase.tc_enhanced_concrete_scenario = tcc
            reg = session.query(Regulation).filter(Regulation.id.in_([1,3,5,9])).all()
            for r in reg:
                testcase.regulations.append(r)
            session.add(testcase)
    else:
        assert("testcase went wrong.")

# nf = FunctionalNominalScenario(path=nfs[0])
# nl = LogicalNominalScenario(path=nls[0])
# nc = ConcreteNominalScenario(path="")
# tc = TriggeringCondition(triggering_condition_name="",functional_insufficiency="",functional_insufficiency_origin="")
# tcf = TCEnhancedFunctionalScenario(path="")
# tcl = TCEnhancedLogicalScenario(path="")
# tcc = TCEnhancedConcreteScenario(path="")
# reg = Regulation(regulation_description="")
# rb = RequiredBehavior(behavior_name="")
# rb.behavior_name
# hb = HazardousBehavior(behavior_description="")
# testcase = TestCase()




session.commit()
