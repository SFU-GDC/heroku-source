echo "Ghetto Lint: helps find a small subset of syntax errors. Can be run locally."
echo "================= Checking main.py " 
python3 -m py_compile main.py
printf "import main" | python3

# NOTE: can't do this cause myconstant import will mess things up ;-;
#for d in cogs/*.py ; do
#    echo "================= Checking $d"
#    python3 $d
#done