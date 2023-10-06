
CASE_DIR = r"C:\Users\Hun\Desktop\127 test\Case 223_1006"
CASE_NAME = CASE_DIR[CASE_DIR.rfind("\\") + 1:CASE_DIR.rfind("_")]
# window settings
CT_MIN, CT_MAX = 0, 80     # brain WW: 80, WL: 40
# CT_MIN, CT_MAX = -20, 180  # subdural WW: 200, WL: 80
# CT_MIN, CT_MAX = -800, 2000  # temporal bone WW: 2800, WL: 600

WINDOW_WIDTH, WINDOW_LEVEL = CT_MAX - CT_MIN, (CT_MAX + CT_MIN) // 2
