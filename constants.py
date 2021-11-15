# STATUS ###################################
STATUS = 'status'
PROCESS = 'process'
FAILED = 'failed'
DONE = 'done'
ERROR = 'error'

# FIELDS CONSTANTS #########################
FIELD = 'field'
CORRECT = 'correct'
ERRORS = 'errors'
NAMES = 'names'
MASSES = 'masses'
EQUATIONS = 'equations'
TOKEN = 'token'
INFORMATION = 'information'
PERCENT = 'percent'
TASK = 'task'
PROCESS_TOKEN = 'process_token'
DATA = 'data'

# ERRORS CONSTANTS #########################
LIST_TYPE_ERROR = "Must be list of values"
INVALID_PROCESS_TOKEN = "Get invalid process token"

# PROCESS TASKS NAMES #####################
TASK_CREATE_MATRIX = "Create the matrix of equations"
GENERATE_START_MEANINGS = 'Generate start meanings'
GENERATE_JMATRIX = 'Generate matrix'
COMPILE_PROGRAM = 'Compile program'
RUN_PROGRAM = 'Run program'
COMPUTE_EQUATIONS = 'Compute equations'

# PROJECT FILES ###########################
PROJECT_SOURCE_DIR_NAME = "ProjectSource"
JMATRIX_GENERATION_DIR = "JmatrixGeneration/"
PATH_TO_ARGUMENTS_FILE = f"/{JMATRIX_GENERATION_DIR}diffs.txt"
PROGRESS_FILE = "progress.txt"

# OTHER CONSTANTS #########################
CORRECT_DICT = {CORRECT: True}
INCORRECT_PROCESS_TOKEN_DICT = {
    STATUS: ERROR,
    ERRORS: [{
        FIELD: PROCESS_TOKEN,
        ERROR: INVALID_PROCESS_TOKEN
    }]
}
