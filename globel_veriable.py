
REGISTRATION_DIR_127 = r"D:\MS\TRC-LAB\ICH Project\Registration\ICH_127"
DATASETS_DIR_127 = r"D:\MS\TRC-LAB\ICH Datasets\ICH_127"

# window settings
CT_MIN, CT_MAX = 0, 80     # brain WW: 80, WL: 40
# CT_MIN, CT_MAX = -20, 180  # subdural WW: 200, WL: 80
# CT_MIN, CT_MAX = -800, 2000  # temporal bone WW: 2800, WL: 600

WINDOW_WIDTH, WINDOW_LEVEL = CT_MAX - CT_MIN, (CT_MAX + CT_MIN) // 2
