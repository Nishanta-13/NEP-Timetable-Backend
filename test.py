from ortools.sat.python import cp_model
import csv
from collections import defaultdict

# --------------------------- 1. Load Data from CSV Files ---------------------------

def load_rooms(filename):
    rooms = []
    with open(filename, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rooms.append({"id": row["id"], "capacity": int(row["capacity"])})
    return rooms

def load_groups(filename):
    groups = {}
    with open(filename, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Assumes groups.csv has columns 'id' and 'size'
            groups[row["id"]] = int(row["size"])
    return groups

def load_courses(filename):
    courses = []
    with open(filename, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            groups_list = row.get("groups", "").split(",") if row.get("groups") else []
            
            # FIX 1: Use 'id' (or the correct header) instead of 'course' to avoid KeyError
            course_id = row["id"] 
            
            # FIX 2 & INTEGRATION: Derive 'subject' from 'id' for the consecutive constraint
            # Assumes course IDs are structured like "MATH_101" -> subject is "MATH"
            subject_id = course_id.split('_')[0] 

            courses.append({
                "id": course_id,
                "prof": row["prof"],
                "groups": groups_list,
                "sessions_per_week": int(row["sessions_per_week"]),
                "subject": subject_id
            })
    return courses

def load_professors(filename):
    professors = {}
    with open(filename, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            professors[row["id"]] = row["name"]
    return professors

def load_slots(filename):
    slots = []
    slot_weights = {}
    with open(filename, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            slots.append(row["slot"])
            # Assumes slots.csv has columns 'slot' and 'weight'
            slot_weights[row["slot"]] = int(row["weight"])
    return slots, slot_weights

# --------------------------- 2. Load all input data ---------------------------
ROOMS = load_rooms("rooms.csv")
STUDENT_GROUPS = load_groups("groups.csv")
COURSES = load_courses("courses.csv")
PROFESSORS = load_professors("professors.csv")
SLOTS, SLOT_WEIGHTS = load_slots("slots.csv")
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]

# Helper maps and lists
course_map = {c['id']: c for c in COURSES}
R = [r['id'] for r in ROOMS]
C = [c['id'] for c in COURSES]
PROF_IDS = list(PROFESSORS.keys())
ALL_SUBJECTS = sorted(list(set(c['subject'] for c in COURSES)))

# Pre-filter rooms based on capacity (Hard Constraint 0)
ALLOWED_ROOMS = {}
for c in COURSES:
    required_capacity = sum(STUDENT_GROUPS.get(g, 0) for g in c['groups'])
    ALLOWED_ROOMS[c['id']] = [r['id'] for r in ROOMS if required_capacity <= r['capacity']]


# --------------------------- 3. Build and Solve Model ---------------------------
def build_and_solve():
    model = cp_model.CpModel()
    
    # --- 3.1. Decision Variables (x, y) ---
    x = {} # x[course, day_idx, slot_idx, room]
    for c in C:
        for d in range(len(DAYS)):
            for t in range(len(SLOTS)):
                for r in R:
                    if r in ALLOWED_ROOMS[c]:
                        x[(c,d,t,r)] = model.NewBoolVar(f"x_{c}_{d}_{t}_{r}")
    
    # Intermediate Variable y[group, day_idx, slot_idx, subject] 
    # True if group g has subject s at slot (d,t)
    y = {}
    for g in STUDENT_GROUPS:
        for d in range(len(DAYS)):
            for t in range(len(SLOTS)):
                for s in ALL_SUBJECTS:
                    y[(g,d,t,s)] = model.NewBoolVar(f"y_{g}_{d}_{t}_{s}")
                    
                    # Link y to x: If group g has subject s at (d,t)
                    c_s_g = [c for c in C if course_map[c]['subject'] == s and g in course_map[c]['groups']]
                    
                    if c_s_g:
                        course_vars = [x[(c,d,t,r)] for c in c_s_g for r in R if (c,d,t,r) in x]
                        
                        # y is true if at least one related course is scheduled
                        model.AddBoolOr(course_vars).OnlyEnforceIf(y[(g,d,t,s)])
                        
                        # y is false if no related course is scheduled
                        model.Add(sum(course_vars) == 0).OnlyEnforceIf(y[(g,d,t,s)].Not())


    # --------------------------- 3.2. Hard Constraints ---------------------------
    
    # H1. Course Fulfillment (Required Sessions)
    for c in C:
        req = course_map[c]['sessions_per_week']
        model.Add(sum(x[(c,d,t,r)] for d in range(len(DAYS)) 
                                     for t in range(len(SLOTS)) 
                                     for r in R if (c,d,t,r) in x) == req)

    # H2. Resource Conflict: Room (One course per room per slot)
    for d in range(len(DAYS)):
        for t in range(len(SLOTS)):
            for r in R:
                vars_here = [x[(c,d,t,r)] for c in C if (c,d,t,r) in x]
                if vars_here:
                    model.Add(sum(vars_here) <= 1)

    # H3. Resource Conflict: Professor (One course per professor per slot)
    prof_courses = defaultdict(list)
    for c in C:
        prof_courses[course_map[c]['prof']].append(c)
    for p, clist in prof_courses.items():
        for d in range(len(DAYS)):
            for t in range(len(SLOTS)):
                vars_here = [x[(c,d,t,r)] for c in clist for r in R if (c,d,t,r) in x]
                if vars_here:
                    model.Add(sum(vars_here) <= 1)

    # H4. Resource Conflict: Student Group (One course per group per slot)
    # This is indirectly enforced by the linking constraints for 'y', but explicit enforcement is safer.
    for g in STUDENT_GROUPS:
        c_for_g = [c for c in C if g in course_map[c]['groups']]
        for d in range(len(DAYS)):
            for t in range(len(SLOTS)):
                vars_here = [x[(c,d,t,r)] for c in c_for_g for r in R if (c,d,t,r) in x]
                if vars_here:
                    model.Add(sum(vars_here) <= 1)
                    
    # H5. REQUIRED: No Consecutive Same Subject (Student Group)
    for g in STUDENT_GROUPS:
        for s in ALL_SUBJECTS:
            for d in range(len(DAYS)):
                # Iterate through all consecutive time slots (t and t+1) on the same day
                for t in range(len(SLOTS) - 1):
                    # Sum of the y variables for this subject at time t and t+1 must be at most 1.
                    # If the sum were 2, it would mean y[g,d,t,s]=1 AND y[g,d,t+1,s]=1.
                    model.Add(y[(g,d,t,s)] + y[(g,d,t+1,s)] <= 1) 

    # --------------------------- 3.3. Objective (Soft Constraint) ---------------------------
    
    # Maximize slot preference (efficiency)
    model.Maximize(sum(x[(c,d,t,r)] * SLOT_WEIGHTS[SLOTS[t]] 
                        for c in C for d in range(len(DAYS)) 
                        for t in range(len(SLOTS)) for r in R if (c,d,t,r) in x))

    # --- Solve ---
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30
    solver.parameters.num_search_workers = 8

    print("Solving...")
    status = solver.Solve(model)

    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        # --- Output Generation (Student and Teacher Timetables) ---
        
        # Student timetable CSV
        with open('student_timetable.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Day", "Slot", "Room", "Course_ID", "Prof", "Groups", "Subject"])
            for d in range(len(DAYS)):
                for t in range(len(SLOTS)):
                    for r in R:
                        for c in C:
                            if (c,d,t,r) in x and solver.Value(x[(c,d,t,r)]) == 1:
                                writer.writerow([
                                    DAYS[d], SLOTS[t], r, c, 
                                    PROFESSORS[course_map[c]['prof']], 
                                    ','.join(course_map[c]['groups']),
                                    course_map[c]['subject']
                                ])

        # Teacher timetable CSV
        with open('teacher_timetable.csv','w',newline='') as f:
            writer = csv.writer(f)
            for p_id in PROF_IDS:
                writer.writerow([PROFESSORS[p_id]]) # Print teacher name as separator
                writer.writerow(["Day", "Slot", "Room", "Course_ID", "Groups"])
                for d in range(len(DAYS)):
                    for t in range(len(SLOTS)):
                        for r in R:
                            for c in C:
                                if course_map[c]['prof']==p_id and (c,d,t,r) in x and solver.Value(x[(c,d,t,r)]):
                                    writer.writerow([DAYS[d], SLOTS[t], r, c, ','.join(course_map[c]['groups'])])
                writer.writerow([]) # Blank line after each teacher

        print("✔ Student and Teacher timetables generated: student_timetable.csv and teacher_timetable.csv")
    else:
        print("❌ No feasible solution found. Try relaxing a soft constraint or checking resource capacity.")

# --------------------------- Run ---------------------------
if __name__=='__main__':
    build_and_solve()